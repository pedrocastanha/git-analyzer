import asyncio
import sys
import git
from src.config import ConfigManager
from src.core.graph import create_graph
from src.cli.ui import CLI


class GitAIAgent:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.config_manager = ConfigManager(repo_path)
        self.cli = CLI(self.config_manager)

        self.workflow = create_graph()
        self.graph = self.workflow.compile()

        self.active = True

        print(f"GitAIAgent initialized for repository at {self.repo_path}")
        print(f"Provider: {self.config_manager.get('ai_provider')}")

    async def analyze_changes(self):
        print("Iniciando análise de mudanças no repositório...")

        initial_state = {
            "messages": [],
            "diff": None,
            "analysis": None,
            "commit_message": None,
            "patch": None,
            "current_action": "analyze",
            "user_confirmation": True,
            "error": None,
            "repo_path": self.repo_path,
            "config": self.config_manager.config,
        }

        result = await self.graph.ainvoke(initial_state)

        if result.get("error"):
            print(f"\n❌ {result['error']}")
            return

        print(
            "\nℹ️  Análise concluída! As sugestões acima devem ser aplicadas manualmente.\n"
        )

    async def deep_analyze(self):
        print("\n" + "=" * 80)
        print("🔍 ANÁLISE PROFUNDA - Multi-Agent Code Review")
        print("=" * 80)
        print("Os agentes Crítico e Construtivo irão discutir as mudanças...")
        print("Aguarde, isso pode levar alguns minutos.\n")

        initial_state = {
            "messages": [],
            "diff": None,
            "analysis": None,
            "commit_message": None,
            "patch": None,
            "current_action": "deep_analyze",
            "user_confirmation": None,
            "error": None,
            "repo_path": self.repo_path,
            "config": self.config_manager.config,
        }

        try:
            result = await self.graph.ainvoke(initial_state)
        except Exception as e:
            print(f"\n❌ Erro durante a execução: {str(e)}")
            import traceback

            traceback.print_exc()
            return

        if result.get("error"):
            print(f"\n{result['error']}")
            return

        print("\nℹ️  Use as recomendações acima para aplicar as mudanças manualmente.\n")

    async def commit_and_push(self):
        """Executa o grafo de commit"""
        language = self.config_manager.get("language", "pt")

        print("\n📤 " + ("Iniciando commit e push..." if language == "pt" else "Starting commit and push..."))
        print("=" * 60)

        initial_state = {
            "messages": [],
            "diff": None,
            "analysis": None,
            "commit_message": None,
            "patch": None,
            "current_action": "commit",
            "user_confirmation": None,
            "error": None,
            "repo_path": self.repo_path,
            "config": self.config_manager.config,
        }

        result = await self.graph.ainvoke(initial_state)

        if result.get("error"):
            print(f"\n{result['error']}")
            return

        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"

        while True:
            print(f"\n✅ " + ("Mensagem de commit:" if language == "pt" else "Commit message:"))
            print(f"   {GREEN}{result['commit_message']}{RESET}\n")

            if language == "pt":
                confirm = input("Confirmar commit e push? (s/n): ").strip().lower()
            else:
                confirm = input("Confirm commit and push? (y/n): ").strip().lower()

            if confirm in ["s", "y", "yes", "sim"]:
                result["user_confirmation"] = True
                await self.graph.ainvoke(result)
                break
            elif confirm in ["n", "no", "não", "nao"]:
                if language == "pt":
                    want_suggestion = input("\nDeseja sugerir melhorias na mensagem? (s/n): ").strip().lower()
                else:
                    want_suggestion = input("\nWould you like to suggest improvements? (y/n): ").strip().lower()

                if want_suggestion in ["s", "y", "yes", "sim"]:
                    if language == "pt":
                        suggestion = input(f"\n{YELLOW}💡 Digite sua sugestão:{RESET}\n   ").strip()
                    else:
                        suggestion = input(f"\n{YELLOW}💡 Enter your suggestion:{RESET}\n   ").strip()

                    if not suggestion:
                        print("⚠️  " + ("Sugestão vazia. Cancelando..." if language == "pt" else "Empty suggestion. Cancelling..."))
                        break

                    result = await self._refine_commit_message(result, suggestion)

                    if result.get("error"):
                        print(f"\n{result['error']}")
                        break
                else:
                    print("❌ " + ("Operação cancelada." if language == "pt" else "Operation cancelled."))
                    break
            else:
                print("⚠️  " + ("Opção inválida. Digite 's' para sim ou 'n' para não." if language == "pt" else "Invalid option. Type 'y' for yes or 'n' for no."))

    async def split_commit_and_push(self):
        """Divide diffs grandes em commits menores e lógicos."""
        language = self.config_manager.get("language", "pt")
        
        print("\n✂️  " + ("Analisando mudanças para dividir em commits..." if language == "pt" else "Analyzing changes to split into commits..."))
        print("=" * 60)
        
        from src.core.nodes import get_diff_node, split_diff_node, generate_split_commits_node, execute_split_commits_node
        
        # 1. Obter o diff
        state = {
            "messages": [],
            "diff": None,
            "split_commits": None,
            "user_confirmation": None,
            "error": None,
            "repo_path": self.repo_path,
            "config": self.config_manager.config,
        }
        
        state = {**state, **(await get_diff_node(state))}
        
        if state.get("error") or not state.get("diff"):
            print(f"\n❌ {state.get('error', 'No diff found')}")
            return
        
        # 2. Dividir o diff em grupos
        state = {**state, **(await split_diff_node(state))}
        
        if state.get("error") or not state.get("split_commits"):
            print(f"\n❌ {state.get('error', 'Could not split diff')}")
            return
        
        # 3. Gerar mensagens de commit para cada grupo
        state = {**state, **(await generate_split_commits_node(state))}
        
        if state.get("error"):
            print(f"\n❌ {state['error']}")
            return
        
        # 4. Mostrar preview e pedir confirmação
        print("\n📋 " + ("Commits propostos:" if language == "pt" else "Proposed commits:"))
        print("=" * 60)
        
        for i, commit in enumerate(state["split_commits"], 1):
            print(f"\n{i}. {commit['message']}")
            print(f"   Arquivos: {', '.join(commit['files'])}")
        
        print("\n" + "=" * 60)
        
        if language == "pt":
            confirm = input("\nConfirmar e executar estes commits? (s/n): ").strip().lower()
        else:
            confirm = input("\nConfirm and execute these commits? (y/n): ").strip().lower()
        
        if confirm not in ["s", "y", "yes", "sim"]:
            print("❌ " + ("Operação cancelada." if language == "pt" else "Operation cancelled."))
            return
        
        # 5. Executar os commits
        state["user_confirmation"] = True
        state = {**state, **(await execute_split_commits_node(state))}
        
        if state.get("error"):
            print(f"\n❌ {state['error']}")
        else:
            print("\n✅ " + ("Todos os commits foram executados!" if language == "pt" else "All commits executed!"))

    async def _refine_commit_message(self, current_state: dict, suggestion: str) -> dict:
        from src.providers.chains import ChainManager
        from src.providers.llms import LLMManager
        from src.core.nodes import extract_llm_content

        language = self.config_manager.get("language", "pt")

        print("\n🔄 " + ("Refinando mensagem de commit..." if language == "pt" else "Refining commit message..."))

        try:
            provider = current_state["config"].get("ai_provider", "gemini")
            llm = LLMManager.get_llm(provider, current_state["config"])
            chain = ChainManager.get_refine_commit_message_chain(llm, language)

            response = await chain.ainvoke({
                "current_message": current_state['commit_message'],
                "user_suggestion": suggestion,
                "diff": current_state['diff'][:3000]
            })

            refined_message = extract_llm_content(response.content).strip()
            refined_message = refined_message.strip('"').strip("'")

            current_state["commit_message"] = refined_message
            return current_state

        except Exception as e:
            error_msg = (f"Erro ao refinar mensagem: {str(e)}" if language == "pt" else f"Error refining message: {str(e)}")
            print(f"❌ {error_msg}")
            return {**current_state, "error": error_msg}

    async def run(self):
        """Loop principal"""
        if self.config_manager.is_first_run():
            self.cli.first_time_setup()

        self.cli.print_welcome()

        while self.active:
            try:
                command = self.cli.get_command()

                if command == "analyze":
                    await self.analyze_changes()
                elif command == "danalyze":
                    await self.deep_analyze()
                elif command == "up":
                    await self.commit_and_push()
                elif command == "split-up":
                    await self.split_commit_and_push()
                elif command == "mermaid":
                    print(self.graph.get_graph().draw_mermaid())
                elif command == "config":
                    self.cli.configure()
                elif command == "details":
                    self.cli.get_details()
                elif command == "exit":
                    print("👋 Até logo!")
                    self.active = False
                elif command:
                    print(f"❓ Comando desconhecido: '{command}'")

            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                self.active = False
            except Exception as e:
                print(f"❌ Erro: {e}")


def main():
    try:
        agent = GitAIAgent()
        asyncio.run(agent.run())
    except git.exc.InvalidGitRepositoryError:
        print("❌ Não é um repositório Git.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
