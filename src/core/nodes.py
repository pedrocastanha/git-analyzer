import traceback
import re
import os

from src.core.state import GraphState
from langchain_core.messages import HumanMessage, AIMessage
import git
import json
from src.providers.llm_providers import LLMProvider

def extract_llm_content(response_content):
    if isinstance(response_content, list):
        if all(isinstance(item, str) for item in response_content):
            return "".join(response_content)
        if len(response_content) > 0 and isinstance(response_content[0], dict) and 'text' in response_content[0]:
            return response_content[0]['text']
    if isinstance(response_content, str):
        return response_content
    return ""

def extract_json_from_llm_output(text: str) -> dict:
    """Extrai JSON de saída de LLM, sendo tolerante a vários formatos."""

    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"⚠️  Erro ao parsear JSON do bloco ```json: {e}")

    match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    pattern = r'\{\s*"plan"\s*:\s*"([^"]*(?:\\"[^"]*)*)"\s*,\s*"patch"\s*:\s*"([^"]*(?:\\"[^"]*)*)"'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        plan = match.group(1)
        patch = match.group(2)
        return {"plan": plan, "patch": patch}

    return None

async def get_diff_node(state: GraphState) -> dict:
    print("Obtendo o diff do repositório...")

    try:
        repo = git.Repo(state['repo_path'])
        diff_unstaged = repo.git.diff()
        diff_staged = repo.git.diff('--cached')

        full_diff = ""
        if diff_unstaged:
            full_diff += "=== Mudanças não staged ===\n" + diff_unstaged + "\n\n"
        if diff_staged:
            full_diff += "=== Mudanças staged ===\n" + diff_staged + "\n"

        if not full_diff:
            return {'diff': None, 'error': "Nenhuma mudança detectada no repositório."}

        else:
            max_size = state['config'].get('diff_max_size', 15000)
            if len(full_diff) > max_size:
                full_diff = full_diff[:max_size] + "\n\n... (truncado)"
            return {'diff': full_diff, 'error': None}

    except Exception as e:
        return {'diff': None, 'error': f"Erro ao obter o diff: {str(e)}"}

async def analyze_code_node(state: GraphState) -> dict:
    print("Analisando o código...")

    if not state.get('diff'):
        return {"analysis": None}

    try:
        agent = LLMProvider.create(state['config'], 'analyze')

        messages = [HumanMessage(content=state['diff'])]
        response = await agent.ainvoke({"messages": messages})

        analysis = extract_llm_content(response.content)
        return {
            "analysis": analysis,
            "messages": messages + [response]
        }
    except Exception as e:
        return {"analysis": None, "error": f"Erro na análise do código: {str(e)}"}


async def generate_improvements_node(state: GraphState) -> dict:
    print("Gerando sugestões de melhorias...\n")

    if not state['analysis'] or not state['diff']:
        return {'patch': None}

    try:
        agent = LLMProvider.create(state['config'], 'generate_improvements')

        response = await agent.ainvoke({
            "messages": [
                HumanMessage(content="Gerar sugestões de melhorias manuais.")
            ],
            "analysis": state['analysis'],
            "diff": state['diff']
        })
        new_messages = state['messages'] + [response]
        content = extract_llm_content(response.content)

        print("\n" + "="*70)
        print("📋 SUGESTÕES DE MELHORIAS")
        print("="*70)
        print(content)
        print("="*70 + "\n")

        return {'patch': None, 'analysis': content, "messages": new_messages}

    except Exception as e:
        return {'patch': None, 'error': f"Erro ao gerar sugestões: {str(e)}"}

async def generate_commit_message_node(state: GraphState) -> dict:
    print("Gerando mensagem de commit...")

    if state.get('commit_message'):
        return {}

    if not state['diff']:
        return {'commit_message': None}

    try:
        agent = LLMProvider.create(state['config'], 'generate_commit_message')

        lang = state['config'].get('language', 'pt')
        lang_instruction = "em português" if lang == 'pt' else "in English"

        response = await agent.ainvoke({
            "messages": [
                HumanMessage(content="Gerar mensagem de commit.")
            ],
            "diff": state['diff'],
            "lang_instruction": lang_instruction
        })
        new_messages = state['messages'] + [response]
        commit_message = extract_llm_content(response.content)
        return {'commit_message': commit_message.strip(), "messages": new_messages}

    except Exception as e:
        return {'commit_message': None, 'error': f"Erro ao gerar commit: {e}"}

async def apply_patch_node(state: GraphState) -> dict:
    print("Aplicando o patch gerado...")

    if not state['patch'] or not state['user_confirmation']:
        return {}

    try:
        repo = git.Repo(state['repo_path'])
        patch_dir = "/tmp/ai_git"
        patch_file = f"{patch_dir}/patch.patch"

        os.makedirs(patch_dir, exist_ok=True)

        patch_content = state['patch']
        if r'\n' in patch_content or '\\n' in patch_content:
            patch_content = patch_content.replace('\\n', '\n')

        with open(patch_file, 'w') as f:
            f.write(patch_content)

        repo.git.apply(patch_file)
        print("Patch aplicado com sucesso.")
        return {}
    except Exception as e:
        error_message = f"Erro ao aplicar o patch: {str(e)}"
        print(error_message)
        return {'error': error_message}

async def commit_and_push_node(state: GraphState) -> dict:
    print("Comitando e enviando mudanças...")

    if not state['commit_message'] or not state['user_confirmation']:
        return {}

    try:
        repo = git.Repo(state['repo_path'])

        if state['config'].get('auto_stage', True):
            repo.git.add(A=True)

        repo.index.commit(state['commit_message'])

        if state['config'].get('auto_push', True):
            origin = repo.remote(name='origin')
            current_branch = repo.active_branch.name
            origin.push(current_branch)
            print(f"Mudanças enviadas com sucesso na branch '{current_branch}')")

        else:
            print("commit realizado")
        return {}
    except Exception as e:
        error_message = f"Erro ao commitar: {str(e)}"
        print(error_message)
        return {'error': error_message}

async def deep_analyze_critic_node(state: GraphState) -> dict:
    print("\n" + "=" * 60)
    print("🔴 AGENTE CRÍTICO ANALISANDO")
    print("=" * 60)

    conversation_history = state.get("conversation_history", [])
    diff = state['diff']
    messages = []

    if not conversation_history:
        messages = [HumanMessage(content=f"Analise o seguinte diff:\n\n {diff}")]
    else:
        messages = conversation_history.copy()
        messages.append(HumanMessage(content="Por favor, responda ao ponto levantado pelo Construtivo."))

    try:
        agent = LLMProvider.create(state['config'], 'deep_analyze_critic')
        response = await agent.ainvoke({"messages": messages})
        text = extract_llm_content(response.content)

        if not text or len(text.strip()) < 10:
            print(f"⚠️  AVISO: Agente Crítico retornou resposta vazia!")
            print(f"Response.content: {response.content}")
            return {"error": "Agente Crítico não gerou resposta válida"}

        ai_message = AIMessage(content=text, name="Crítico de Segurança e Padrões")

        print(f"\033[91m{text[:500]}{'...' if len(text) > 500 else ''}\033[0m")
        print(f"📊 Tamanho da resposta: {len(text)} caracteres\n")

        updated_history = conversation_history + [ai_message]
        print(f"💾 Histórico atualizado: {len(updated_history)} mensagens\n")

        return {"conversation_history": updated_history}

    except Exception as e:
        error_msg = f"Erro no Agente Crítico: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return {"error": error_msg}

async def deep_analyze_constructive_node(state: GraphState) -> dict:
    print("\n" + "=" * 60)
    print("🟢 AGENTE CONSTRUTIVO ANALISANDO")
    print("=" * 60)

    conversation_history = state.get("conversation_history", [])
    diff = state.get('diff', '')

    if not conversation_history:
        print("⚠️  AVISO: Construtivo chamado sem histórico!")
        return {"error": "Construtivo precisa do Crítico primeiro"}

    messages = conversation_history.copy()

    last_critic_msg = ""
    for msg in reversed(messages):
        if hasattr(msg, 'name') and msg.name == "Crítico de Segurança e Padrões":
            last_critic_msg = msg.content
            break

    prompt = f"""Por favor, analise as preocupações levantadas pelo Crítico e responda de forma construtiva.

Última análise do Crítico:
{last_critic_msg[:1000] if last_critic_msg else "N/A"}

Lembre-se do diff original que estamos discutindo:
```
{diff[:500]}...
```

Sua resposta:"""

    messages.append(HumanMessage(content=prompt))

    print(f"📋 Total de mensagens enviadas: {len(messages)}")
    print(f"📏 Tamanho total do histórico: {sum(len(str(m.content)) for m in messages)} caracteres\n")

    try:
        agent = LLMProvider.create(state['config'], 'deep_analyze_constructive')

        response = await agent.ainvoke({"messages": messages})

        print(f"🔍 DEBUG - Response type: {type(response)}")
        print(f"🔍 DEBUG - Response.content type: {type(response.content)}")
        print(f"🔍 DEBUG - Response.content: {response.content}")

        text = extract_llm_content(response.content)

        if not text or len(text.strip()) < 10:
            print(f"⚠️  AVISO: Agente Construtivo retornou resposta vazia!")
            print(f"Response.content: {response.content}")
            return {"error": "Agente Construtivo não gerou resposta válida"}

        ai_message = AIMessage(content=text, name="Construtivo de Lógica e Desempenho")

        print(f"\033[92m{text[:500]}{'...' if len(text) > 500 else ''}\033[0m")
        print(f"📊 Tamanho da resposta: {len(text)} caracteres\n")

        updated_history = conversation_history + [ai_message]
        print(f"💾 Histórico atualizado: {len(updated_history)} mensagens\n")

        return {"conversation_history": updated_history}

    except Exception as e:
        error_msg = f"Erro no Agente Construtivo: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return {"error": error_msg}

async def deep_generate_improvements_node(state: GraphState) -> dict:
    print("\n" + "=" * 60)
    print("🔧 GERANDO PLANO DE AÇÃO E PATCH")
    print("=" * 60 + "\n")
    conversation_history = state.get("conversation_history", [])

    if not conversation_history or not state['diff']:
        return {'patch': None, 'analysis': None}

    conversation_text = "\n\n".join([
        f"**{msg.name if hasattr(msg, 'name') else 'Agente'}**:\n{msg.content}"
        for msg in conversation_history
    ])
    final_analysis = f"""=== DISCUSSÃO COMPLETA ENTRE OS AGENTES ===

    {conversation_text}

    === FIM DA DISCUSSÃO ===

    Com base nesta discussão profunda, gere um patch Git VÁLIDO e APLICÁVEL."""
    try:
        print("🔧 Invocando agente especialista em geração de patches...\n")
        agent = LLMProvider.create(state['config'], 'patch_generator')
        response = await agent.ainvoke({
            "messages": [
                HumanMessage(content="Gerar plano de ação e patch com base na conversa a seguir.")
            ],
            "analysis": final_analysis,
            "diff": state['diff']
        })

        content = extract_llm_content(response.content)

        if not content or len(content.strip()) < 10:
            print("⚠️  LLM retornou resposta vazia ou muito curta!")
            print("Provavelmente a discussão foi muito longa ou complexa.")
            print("Vamos criar um plano básico sem patch.\n")
            return {
                'patch': None,
                'analysis': "A discussão foi concluída, mas não foi possível gerar um patch automático. Revise as sugestões dos agentes manualmente.",
                'messages': state.get('messages', []) + [response]
            }

        result = extract_json_from_llm_output(content)
        if not result:
            print("⚠️  Não foi possível extrair JSON. Tentando fallback...")
            print(f"Conteúdo (primeiros 1000 chars):\n{content[:1000]}\n")

            try:
                debug_file = "/tmp/ai_git/last_llm_response.txt"
                os.makedirs("/tmp/ai_git", exist_ok=True)
                with open(debug_file, 'w') as f:
                    f.write(content)
                print(f"💾 Resposta completa salva em: {debug_file}\n")
            except:
                pass

            return {
                'patch': None,
                'analysis': content if content else "Não foi possível gerar análise.",
                'messages': state.get('messages', []) + [response]
            }

        plan = result.get("plan", "Nenhum plano fornecido")
        patch = result.get("patch", "")

        print(f"📋 Plano extraído ({len(plan)} chars)")
        print(f"📦 Patch extraído ({len(patch)} chars)\n")

        if not patch or "NO_CHANGES_NEEDED" in patch:
            print("\n" + "="*60)
            print("📋 REVIEW DO CÓDIGO - ANÁLISE PROFUNDA")
            print("="*60)
            print(plan)
            print("="*60 + "\n")
            return {
                'patch': None,
                'analysis': plan,
                'messages': state.get('messages', []) + [response]
            }
        else:
            print(f"✅ Patch gerado com sucesso!\n")
            return {
                'patch': patch,
                'analysis': plan,
                'messages': state.get('messages', []) + [response]
            }
    except Exception as e:
        error_msg = f"Erro ao gerar melhorias: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {'patch': None, 'analysis': None, 'error': error_msg}