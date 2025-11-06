import traceback
import re
import os

from src.core.state import GraphState
from langchain_core.messages import HumanMessage, AIMessage
import git
import json
from src.providers.llm_providers import LLMProvider

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"



def extract_llm_content(response_content):
    if isinstance(response_content, list):
        if all(isinstance(item, str) for item in response_content):
            return "".join(response_content)
        if (
            len(response_content) > 0
            and isinstance(response_content[0], dict)
            and "text" in response_content[0]
        ):
            return response_content[0]["text"]
    if isinstance(response_content, str):
        return response_content
    return ""


def colorize_code_blocks(text: str) -> str:
    """Adiciona cores aos blocos de código no relatório executivo."""
    import re

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    text = re.sub(r"^(##\s+.*?)$", f"{BOLD}{CYAN}\\1{RESET}", text, flags=re.MULTILINE)
    text = re.sub(r"^(###\s+.*?)$", f"{BOLD}{BLUE}\\1{RESET}", text, flags=re.MULTILINE)

    replacements = {
        "🔴 Alta": f"{RED}{BOLD}🔴 Alta{RESET}",
        "🔴 High": f"{RED}{BOLD}🔴 High{RESET}",
        "🟡 Média": f"{YELLOW}{BOLD}🟡 Média{RESET}",
        "🟡 Medium": f"{YELLOW}{BOLD}🟡 Medium{RESET}",
        "🟢 Baixa": f"{GREEN}{BOLD}🟢 Baixa{RESET}",
        "🟢 Low": f"{GREEN}{BOLD}🟢 Low{RESET}",
        "**Arquivo:**": f"{BOLD}Arquivo:{RESET}",
        "**File:**": f"{BOLD}File:{RESET}",
        "**Linha:**": f"{BOLD}Linha:{RESET}",
        "**Line:**": f"{BOLD}Line:{RESET}",
        "**Prioridade:**": f"{BOLD}Prioridade:{RESET}",
        "**Priority:**": f"{BOLD}Priority:{RESET}",
        "**Motivo:**": f"{BOLD}Motivo:{RESET}",
        "**Reason:**": f"{BOLD}Reason:{RESET}",
        "**Ação:**": f"{BOLD}Ação:{RESET}",
        "**Action:**": f"{BOLD}Action:{RESET}",
        "**Código Atual:**": f"{BOLD}Código Atual:{RESET}",
        "**Current Code:**": f"{BOLD}Current Code:{RESET}",
        "**Código Sugerido:**": f"{BOLD}Código Sugerido:{RESET}",
        "**Suggested Code:**": f"{BOLD}Suggested Code:{RESET}",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"(\*\*Código Atual:\*\*|\*\*Current Code:\*\*)\s*```(\w+)?\s*(.*?)```",
        lambda m: f'{BOLD}{m.group(1)}{RESET}\n```{m.group(2) or ""}\n{RED}{m.group(3)}{RESET}\n```',
        text,
        flags=re.DOTALL,
    )

    text = re.sub(
        r"(\*\*Código Sugerido:\*\*|\*\*Suggested Code:\*\*)\s*```(\w+)?\s*(.*?)```",
        lambda m: f'{BOLD}{m.group(1)}{RESET}\n```{m.group(2) or ""}\n{GREEN}{m.group(3)}{RESET}\n```',
        text,
        flags=re.DOTALL,
    )

    return text


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
    language = state["config"].get("language", "pt")
    print("Obtendo o diff do repositório..." if language == "pt" else "Getting the repository diff...")

    try:
        repo = git.Repo(state["repo_path"])
        diff_unstaged = repo.git.diff()
        diff_staged = repo.git.diff("--cached")

        full_diff = ""
        if diff_unstaged:
            full_diff += ("=== Mudanças não staged ===\n" if language == "pt" else "=== Unstaged changes ===\n") + diff_unstaged + "\n\n"
        if diff_staged:
            full_diff += ("=== Mudanças staged ===\n" if language == "pt" else "=== Staged changes ===\n") + diff_staged + "\n"

        if not full_diff:
            return {"diff": None, "error": "Nenhuma mudança detectada no repositório." if language == "pt" else "No changes detected in the repository."}

        else:
            max_size = state["config"].get("diff_max_size", 15000)
            if len(full_diff) > max_size:
                full_diff = full_diff[:max_size] + "\n\n... (truncado)"
            return {"diff": full_diff, "error": None}

    except Exception as e:
        return {"diff": None, "error": (f"Erro ao obter o diff: {str(e)}" if language == "pt" else f"Error getting diff: {str(e)}")}


async def analyze_code_node(state: GraphState) -> dict:
    language = state["config"].get("language", "pt")
    print("Analisando o código..." if language == "pt" else "Analyzing the code...")

    if not state.get("diff"):
        return {"analysis": None}

    try:
        agent = LLMProvider.create(state["config"], "analyze")

        messages = [HumanMessage(content=state["diff"])]
        response = await agent.ainvoke({"messages": messages})

        analysis = extract_llm_content(response.content)
        return {"analysis": analysis, "messages": messages + [response]}
    except Exception as e:
        return {"analysis": None, "error": f"Erro na análise do código: {str(e)}"}


async def generate_improvements_node(state: GraphState) -> dict:
    language = state["config"].get("language", "pt")
    print("Gerando sugestões de melhorias...\n" if language == "pt" else "Generating improvement suggestions...\n")

    if not state["analysis"] or not state["diff"]:
        return {"patch": None}

    truncated_analysis = state["analysis"][:4000]

    try:
        agent = LLMProvider.create(state["config"], "generate_improvements")

        message_content = (
            "Gerar sugestões de melhorias manuais."
            if language == "pt"
            else "Generate manual improvement suggestions."
        )

        response = await agent.ainvoke(
            {
                "messages": [HumanMessage(content=message_content)],
                "analysis": truncated_analysis,
                "diff": state["diff"],
            }
        )
        new_messages = state["messages"] + [response]
        content = extract_llm_content(response.content)

        colorized_content = colorize_code_blocks(content)

        title = (
            "📋 SUGESTÕES DE MELHORIAS"
            if language == "pt"
            else "📋 IMPROVEMENT SUGGESTIONS"
        )
        print("\n" + "=" * 70)
        print(title)
        print("=" * 70)
        print("=" * 70 + "\n")

        return {"patch": None, "analysis": content, "messages": new_messages}

    except Exception as e:
        return {"patch": None, "error": f"Erro ao gerar sugestões: {str(e)}"}


async def generate_commit_message_node(state: GraphState) -> dict:
    language = state["config"].get("language", "pt")
    print("Gerando mensagem de commit..." if language == "pt" else "Generating commit message...")

    if state.get("commit_message"):
        return {}

    if not state["diff"]:
        return {"commit_message": None}

    try:
        agent = LLMProvider.create(state["config"], "generate_commit_message")

        lang = state["config"].get("language", "pt")
        lang_instruction = "em português" if lang == "pt" else "in English"

        response = await agent.ainvoke(
            {
                "messages": [HumanMessage(content="Gerar mensagem de commit." if language == "pt" else "Generate commit message.")],
                "diff": state["diff"],
                "lang_instruction": lang_instruction,
            }
        )
        new_messages = state["messages"] + [response]
        commit_message = extract_llm_content(response.content)
        return {"commit_message": commit_message.strip(), "messages": new_messages}

    except Exception as e:
        return {"commit_message": None, "error": (f"Erro ao gerar commit: {e}" if language == "pt" else f"Error generating commit: {e}")}


async def apply_patch_node(state: GraphState) -> dict:
    language = state["config"].get("language", "pt")
    print("Aplicando o patch gerado..." if language == "pt" else "Applying the generated patch...")

    if not state["patch"] or not state["user_confirmation"]:
        return {}

    try:
        repo = git.Repo(state["repo_path"])
        patch_dir = "/tmp/ai_git"
        patch_file = f"{patch_dir}/patch.patch"

        os.makedirs(patch_dir, exist_ok=True)

        patch_content = state["patch"]
        if r"\n" in patch_content or "\\n" in patch_content:
            patch_content = patch_content.replace("\\n", "\n")

        with open(patch_file, "w") as f:
            f.write(patch_content)

        repo.git.apply(patch_file)
        print("Patch aplicado com sucesso." if language == "pt" else "Patch applied successfully.")
        return {}
    except Exception as e:
        error_message = (f"Erro ao aplicar o patch: {str(e)}" if language == "pt" else f"Error applying patch: {str(e)}")
        print(error_message)
        return {"error": error_message}


async def commit_and_push_node(state: GraphState) -> dict:
    language = state["config"].get("language", "pt")
    print("Comitando e enviando mudanças..." if language == "pt" else "Committing and pushing changes...")

    if not state["commit_message"] or not state["user_confirmation"]:
        return {}

    try:
        repo = git.Repo(state["repo_path"])

        if state["config"].get("auto_stage", True):
            repo.git.add(A=True)

        repo.index.commit(state["commit_message"])

        if state["config"].get("auto_push", True):
            origin = repo.remote(name="origin")
            current_branch = repo.active_branch.name
            origin.push(current_branch)
            print((f"Mudanças enviadas com sucesso na branch '{current_branch}'" if language == "pt" else f"Changes pushed successfully on branch '{current_branch}'"))

        else:
            print("commit realizado" if language == "pt" else "commit done")
        return {}
    except Exception as e:
        error_message = (f"Erro ao commitar: {str(e)}" if language == "pt" else f"Error committing: {str(e)}")
        print(error_message)
        return {"error": error_message}


async def deep_analyze_critic_node(state: GraphState) -> dict:
    language = state["config"].get("language", "pt")
    print("\n" + "=" * 60)
    print(f"🔴 {RED}AGENTE CRÍTICO ANALISANDO{RESET}" if language == "pt" else f"🔴 {RED}CRITICAL AGENT ANALYZING{RESET}")
    print("=" * 60)

    conversation_history = state.get("conversation_history", [])
    diff = state["diff"]
    messages = []

    if not conversation_history:
        initial_prompt = (
            f"Analise o seguinte diff:\n\n {diff}"
            if language == "pt"
            else f"Analyze the following diff:\n\n {diff}"
        )
        messages = [HumanMessage(content=initial_prompt)]
    else:
        messages = conversation_history.copy()
        continue_prompt = (
            "Por favor, responda ao ponto levantado pelo Construtivo."
            if language == "pt"
            else "Please respond to the point raised by the Constructive agent."
        )
        messages.append(HumanMessage(content=continue_prompt))

    try:
        agent = LLMProvider.create(state["config"], "deep_analyze_critic")
        response = await agent.ainvoke({"messages": messages})
        text = extract_llm_content(response.content)

        if not text or len(text.strip()) < 10:
            print(f"⚠️  AVISO: Agente Crítico retornou resposta vazia!" if language == "pt" else f"⚠️  WARNING: Critical Agent returned empty response!")
            print(f"Response.content: {response.content}")
            return {"error": ("Agente Crítico não gerou resposta válida" if language == "pt" else "Critical Agent did not generate a valid response")}

        print(text)

        ai_message = AIMessage(content=text, name="Crítico de Segurança e Padrões" if language == "pt" else "Security and Standards Critic")

        updated_history = conversation_history + [ai_message]
        print(f"💾 Histórico atualizado: {len(updated_history)} mensagens\n" if language == "pt" else f"💾 History updated: {len(updated_history)} messages\n")

        return {"conversation_history": updated_history}

    except Exception as e:
        error_msg = (f"Erro no Agente Crítico: {str(e)}" if language == "pt" else f"Error in Critical Agent: {str(e)}")
        print(f"❌ {error_msg}")
        import traceback

        traceback.print_exc()
        return {"error": error_msg}


async def deep_analyze_constructive_node(state: GraphState) -> dict:
    language = state["config"].get("language", "pt")
    print("\n" + "=" * 60)
    print(f"🟢 {GREEN}AGENTE CONSTRUTIVO ANALISANDO{RESET}" if language == "pt" else f"🟢{GREEN}CONSTRUCTIVE AGENT ANALYZING{RESET}")
    print("=" * 60)

    conversation_history = state.get("conversation_history", [])
    diff = state.get("diff", "")

    if not conversation_history:
        print("⚠️  AVISO: Construtivo chamado sem histórico!" if language == "pt" else "⚠️  WARNING: Constructive called without history!")
        return {"error": ("Construtivo precisa do Crítico primeiro" if language == "pt" else "Constructive needs Critic first")}

    messages = conversation_history.copy()

    last_critic_msg = ""
    for msg in reversed(messages):
        if hasattr(msg, "name") and (msg.name == "Crítico de Segurança e Padrões" or msg.name == "Security and Standards Critic"):
            last_critic_msg = msg.content
            break

    if language == "pt":
        prompt = f"""Por favor, analise as preocupações levantadas pelo Crítico e responda de forma construtiva.

            Última análise do Crítico:
            {last_critic_msg if last_critic_msg else "N/A"}
            
            Lembre-se do diff original que estamos discutindo:
            ```
            {diff}...
            ```

            Sua resposta:"""
    else:
        prompt = f"""Please analyze the concerns raised by the Critic and respond constructively.

            Last Critic analysis:
            {last_critic_msg if last_critic_msg else "N/A"}
            
            Remember the original diff we are discussing:
            ```
            {diff}...
            ```
            
            Your response:"""

    messages.append(HumanMessage(content=prompt))

    print(f"📋 Total de mensagens enviadas: {len(messages)}" if language == "pt" else f"📋 Total messages sent: {len(messages)}")

    try:
        agent = LLMProvider.create(state["config"], "deep_analyze_constructive")

        response = await agent.ainvoke({"messages": messages})

        text = extract_llm_content(response.content)

        if not text or len(text.strip()) < 10:
            print(f"⚠️  AVISO: Agente Construtivo retornou resposta vazia!" if language == "pt" else f"⚠️  WARNING: Constructive Agent returned empty response!")
            print(f"Response.content: {response.content}")
            return {"error": ("Agente Construtivo não gerou resposta válida" if language == "pt" else "Constructive Agent did not generate a valid response")}

        print(text)

        ai_message = AIMessage(content=text, name="Construtivo de Lógica e Desempenho" if language == "pt" else "Logic and Performance Constructive")

        updated_history = conversation_history + [ai_message]
        print(f"💾 Histórico atualizado: {len(updated_history)} mensagens\n" if language == "pt" else f"💾 History updated: {len(updated_history)} messages\n")

        return {"conversation_history": updated_history}

    except Exception as e:
        error_msg = (f"Erro no Agente Construtivo: {str(e)}" if language == "pt" else f"Error in Constructive Agent: {str(e)}")
        print(f"❌ {error_msg}")
        import traceback

        traceback.print_exc()
        return {"error": error_msg}


async def deep_generate_improvements_node(state: GraphState) -> dict:
    language = state["config"].get("language", "pt")
    print("\n" + "=" * 60)
    print("🔧 GERANDO PLANO DE AÇÃO E PATCH" if language == "pt" else "🔧 GENERATING ACTION PLAN AND PATCH")
    print("=" * 60 + "\n")
    conversation_history = state.get("conversation_history", [])

    if not conversation_history or not state["diff"]:
        return {"patch": None, "analysis": None}

    conversation_text = "\n\n".join(
        [
            f"**{msg.name if hasattr(msg, 'name') else ('Agente' if language == 'pt' else 'Agent')}**:\n{msg.content}"
            for msg in conversation_history
        ]
    )
    
    if language == "pt":
        final_analysis = f"""=== DISCUSSÃO COMPLETA ENTRE OS AGENTES ===

    {conversation_text}

    === FIM DA DISCUSSÃO ===

    Com base nesta discussão profunda, gere um RELATÓRIO EXECUTIVO detalhado."""
    else:
        final_analysis = f"""=== FULL DISCUSSION BETWEEN AGENTS ===

    {conversation_text}

    === END OF DISCUSSION ===

    Based on this in-depth discussion, generate a detailed EXECUTIVE REPORT."""
    try:
        print("📊 Gerando relatório executivo da análise...\n" if language == "pt" else "📊 Generating executive analysis report...\n")
        agent = LLMProvider.create(state["config"], "executive_report")
        response = await agent.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content="Gerar relatório executivo com base na discussão." if language == "pt" else "Generate executive report based on discussion."
                    )
                ],
                "analysis": final_analysis,
                "diff": state["diff"],
            }
        )

        content = extract_llm_content(response.content)

        if not content or len(content.strip()) < 10:
            print("⚠️  LLM retornou resposta vazia ou muito curta!" if language == "pt" else "⚠️  LLM returned empty or very short response!")
            return {
                "patch": None,
                "analysis": ("Não foi possível gerar o relatório executivo." if language == "pt" else "Could not generate executive report."),
                "messages": state.get("messages", []) + [response],
            }

        colorized_content = colorize_code_blocks(content)

        print("\n" + "=" * 80)
        print("📊 RELATÓRIO EXECUTIVO - ANÁLISE PROFUNDA" if language == "pt" else "📊 EXECUTIVE REPORT - DEEP ANALYSIS")
        print("=" * 80)
        print(colorized_content)
        print("=" * 80 + "\n")

        return {
            "patch": None,
            "analysis": content,
            "messages": state.get("messages", []) + [response],
        }
    except Exception as e:
        error_msg = (f"Erro ao gerar melhorias: {str(e)}" if language == "pt" else f"Error generating improvements: {str(e)}")
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {"patch": None, "analysis": None, "error": error_msg}
