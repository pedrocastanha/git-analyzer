from src.core.state import GraphState
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import git
from src.providers.llm_providers import LLMProvider


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

        analysis = response.content[0]['text']
        return {
            "analysis": analysis,
            "messages": messages + [response]
        }
    except Exception as e:
        return {"analysis": None, "error": f"Erro na análise do código: {str(e)}"}


async def generate_improvements_node(state: GraphState) -> dict:
    print("Gerando patch de melhorias...")

    if not state['analysis'] or not state['diff']:
        return {'patch': None}

    try:
        agent = LLMProvider.create(state['config'], 'generate_improvements')

        response = await agent.ainvoke({
            "messages": [
                HumanMessage(content="Gerar patch de melhorias.")
            ],
            "analysis": state['analysis'],
            "diff": state['diff']
        })
        new_messages = state['messages'] + [response]
        patch = response.content[0]['text']
        if "NO_CHANGES_NEEDED" in patch:
            return {'patch': None, "messages": new_messages}
        else:
            return {'patch': patch, "messages": new_messages}
    except Exception as e:
        return {'patch': None, 'error': f"Erro ao gerar o patch: {str(e)}"}

async def generate_commit_message_node(state: GraphState) -> dict:
    print("Gerando mensagem de commit...")

    if not state['diff']:
        return {'commit_message': None}

    try:
        agent = LLMProvider.create(state['config'], 'generate_commit_message')

        types = ', '.join(state['config'].get('conventional_commits_types', []))
        lang = state['config'].get('language', 'pt')
        lang_instruction = "em português" if lang == 'pt' else "in English"

        response = await agent.ainvoke({
            "messages": [
                HumanMessage(content="Gerar mensagem de commit.")
            ],
            "diff": state['diff'],
            "types": types,
            "lang_instruction": lang_instruction
        })
        new_messages = state['messages'] + [response]
        commit_message = response.content[0]['text']
        return {'commit_message': commit_message.strip(), "messages": new_messages}

    except Exception as e:
        return {'commit_message': None, 'error': f"Erro ao gerar commit: {e}"}

async def apply_patch_node(state: GraphState) -> dict:
    print("Aplicando o patch gerado...")

    if not state['patch'] or not state['user_confirmation']:
        return {}

    try:
        repo = git.Repo(state['repo_path'])
        patch_file = "/tmp/ai_git/patch.patch"

        with open(patch_file, 'w') as f:
            f.write(state['patch'])

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
        error_message = f"Erro ao comitar/enviar mudanças: {str(e)}"
        print(error_message)
        return {'error': error_message}