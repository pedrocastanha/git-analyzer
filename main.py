import asyncio
import sys
import git
from src.config import ConfigManager
from src.core.graph import create_graph


class GitAIAgent:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.config_manager = ConfigManager(repo_path)

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

        # Loop de refinamento da mensagem de commit
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
                # Perguntar se quer sugerir melhorias
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

                    # Refinar mensagem com base na sugestão
                    result = await self._refine_commit_message(result, suggestion)

                    if result.get("error"):
                        print(f"\n{result['error']}")
                        break
                else:
                    print("❌ " + ("Operação cancelada." if language == "pt" else "Operation cancelled."))
                    break
            else:
                print("⚠️  " + ("Opção inválida. Digite 's' para sim ou 'n' para não." if language == "pt" else "Invalid option. Type 'y' for yes or 'n' for no."))

    async def _refine_commit_message(self, current_state: dict, suggestion: str) -> dict:
        """Refina a mensagem de commit com base na sugestão do usuário"""
        from src.providers.llm_providers import LLMProvider
        from langchain_core.messages import HumanMessage

        language = self.config_manager.get("language", "pt")

        print("\n🔄 " + ("Refinando mensagem de commit..." if language == "pt" else "Refining commit message..."))

        try:
            llm = LLMProvider.create(current_state["config"], "refine_commit_message")

            if language == "pt":
                prompt = f"""Você precisa refinar uma mensagem de commit com base em uma sugestão do usuário.

Mensagem de commit atual:
{current_state['commit_message']}

Sugestão do usuário:
{suggestion}

Diff original:
{current_state['diff'][:3000]}

IMPORTANTE:
- Mantenha a mensagem concisa (máximo 72 caracteres)
- Siga o formato Conventional Commits
- Incorpore a sugestão do usuário
- Retorne APENAS a nova mensagem de commit, sem explicações

Nova mensagem de commit:"""
            else:
                prompt = f"""You need to refine a commit message based on a user's suggestion.

Current commit message:
{current_state['commit_message']}

User's suggestion:
{suggestion}

Original diff:
{current_state['diff'][:3000]}

IMPORTANT:
- Keep the message concise (maximum 72 characters)
- Follow Conventional Commits format
- Incorporate the user's suggestion
- Return ONLY the new commit message, without explanations

New commit message:"""

            response = await llm.ainvoke([HumanMessage(content=prompt)])

            from src.core.nodes import extract_llm_content
            refined_message = extract_llm_content(response.content).strip()

            # Remove possíveis quotes ou aspas
            refined_message = refined_message.strip('"').strip("'")

            # Atualiza o estado com a nova mensagem
            current_state["commit_message"] = refined_message
            return current_state

        except Exception as e:
            error_msg = (f"Erro ao refinar mensagem: {str(e)}" if language == "pt" else f"Error refining message: {str(e)}")
            print(f"❌ {error_msg}")
            return {**current_state, "error": error_msg}

    def first_time_setup(self):
        """Setup inicial interativo"""
        print("\n" + "=" * 60)
        print("🎉 Bem-vindo ao gitcast!")
        print("=" * 60)
        print("\nParece que é sua primeira vez aqui!")
        print("Vamos fazer uma configuração rápida.\n")

        print("=" * 60)
        print("📦 Escolha seu provider de IA:")
        print("=" * 60)
        print("  1. OpenAI (GPT-4, GPT-4o-mini, GPT-3.5)")
        print("  2. Gemini (Google)")
        print("")

        while True:
            provider_choice = input("Escolha (1 ou 2): ").strip()
            if provider_choice in ["1", "2"]:
                break
            print("❌ Opção inválida. Digite 1 ou 2.")

        provider = "openai" if provider_choice == "1" else "gemini"
        self.config_manager.set("ai_provider", provider)

        print(f"\n✅ Provider selecionado: {provider.upper()}")
        print("")

        print("=" * 60)
        print("🔑 Configure sua API Key:")
        print("=" * 60)

        if provider == "openai":
            print("\n💡 Onde conseguir:")
            print("   https://platform.openai.com/api-keys")
            print("")
            api_key = input("Cole sua OpenAI API Key: ").strip()
            if api_key:
                self.config_manager.set("openai_api_key", api_key)
                print("✅ API Key configurada!")
            else:
                print("⚠️  Nenhuma key fornecida. Configure depois com 'config'.")
        else:
            print("\n💡 Onde conseguir:")
            print("   https://aistudio.google.com/app/apikey")
            print("")
            api_key = input("Cole sua Gemini API Key: ").strip()
            if api_key:
                self.config_manager.set("gemini_api_key", api_key)
                print("✅ API Key configurada!")
            else:
                print("⚠️  Nenhuma key fornecida. Configure depois com 'config'.")

        self.config_manager.save_config()

        print("\n" + "=" * 60)
        print("✅ Configuração concluída!")
        print("=" * 60)
        print(
            "\n📚 Dica: Use 'config' para alterar configurações a qualquer momento.\n"
        )

    def configure(self):
        """Menu de configuração"""
        print("\n⚙️  Configuração")
        print("=" * 60)
        print("1. Escolher provider de IA")
        print("2. Configurar API keys")
        print("3. Configurar linguagem de retorno da IA")
        print("4. Ver configuração")
        print("0. Voltar")
        print("=" * 60)

        choice = input("\nEscolha: ").strip()

        if choice == "1":
            print("\nProviders:")
            print("  1. Gemini")
            print("  2. OpenAI")

            p = input("\nEscolha: ").strip()
            providers = {"1": "gemini", "2": "openai"}

            if p in providers:
                self.config_manager.set("ai_provider", providers[p])
                self.config_manager.save_config()
                print(f"✅ Provider: {providers[p]}")

        elif choice == "2":
            provider = self.config_manager.get("ai_provider")
            key_name = f"{provider}_api_key" if provider != "ollama" else "ollama_url"

            if provider != "ollama":
                key = input(f"{provider.upper()} API Key: ").strip()
                if key:
                    self.config_manager.set(key_name, key)
                    self.config_manager.save_config()
                    print("✅ API Key configurada!")

        elif choice == "3":
            print("\nLinguagens disponíveis:")
            print("  1. Português (pt-br)")
            print("  2. Inglês (en)")
            lang_choice = input("\nEscolha: ").strip()
            languages = {"1": "pt", "2": "en"}
            if lang_choice in languages:
                self.config_manager.set("language", languages[lang_choice])
                self.config_manager.save_config()
                print(f"✅ Linguagem configurada: {languages[lang_choice]}")

        elif choice == "4":
            print("\n📋 Configuração atual:")
            for k, v in self.config_manager.config.items():
                if "api_key" in k and v:
                    v = v[:8] + "..." + v[-4:]
                print(f"  {k}: {v}")

    def get_details(self):
        """Mostra detalhes dos comandos"""
        details = {
            "analyze": {
                "icon": "1️⃣",
                "title": "Análise de Mudanças",
                "description": "Este comando ativa um agente de IA que utiliza o provider configurado para analisar as alterações no seu projeto Git. O agente avalia o código, identifica pontos fortes e aponta áreas para melhoria, gerando sugestões de melhorias manuais formatadas em markdown que devem ser aplicadas por você.",
            },
            "danalyze": {
                "icon": "2️⃣",
                "title": "Análise Profunda (Deep Analyze)",
                "description": "O 'danalyze' (Deep Analyze) orquestra uma colaboração entre dois agentes de IA especializados:\n\n"
                "- 🔴 Agente Crítico: Focado em identificar bugs, vulnerabilidades de segurança e falhas de design.\n"
                "- 🟢 Agente Construtivo: Focado em propor otimizações de desempenho, refatoração de código e melhorias na arquitetura.\n\n"
                "Como funciona: Os agentes dialogam em um processo iterativo de revisão de código. O Crítico aponta os problemas, e o Construtivo sugere soluções. Este ciclo continua até que ambos cheguem a um consenso ou atinjam 8 interações. No final, é gerado um Relatório Executivo colorido com todas as mudanças recomendadas, priorizadas e com exemplos de código (vermelho = atual, verde = sugerido).",
            },
            "up": {
                "icon": "3️⃣",
                "title": "Commit e Push Automatizados",
                "description": "Este comando utiliza um agente de IA treinado em 'Conventional Commits' para analisar suas mudanças e gerar uma mensagem de commit concisa e padronizada (máximo 72 caracteres, sem explicações adicionais). Após a sua aprovação, o agente realiza o commit e o push para o repositório remoto, agilizando o seu fluxo de trabalho.",
            },
            "mermaid": {
                "icon": "4️⃣",
                "title": "Visualização do Grafo de Fluxo",
                "description": "Gera e exibe o código no formato Mermaid do grafo de fluxo de trabalho da aplicação. Este recurso é útil para visualizar a arquitetura dos agentes, entender suas interações e depurar o fluxo de execução.",
            },
            "config": {
                "icon": "5️⃣",
                "title": "Configuração Interativa",
                "description": "Abre um menu interativo que permite gerenciar as configurações da aplicação, como:\n\n"
                "- Selecionar o provedor de IA (OpenAI, Gemini, etc.).\n"
                "- Configurar as chaves de API (API Keys).\n"
                "- Visualizar as configurações ativas.",
            },
            "details": {
                "icon": "6️⃣",
                "title": "Detalhes dos Comandos",
                "description": "Exibe esta tela, com a documentação detalhada de todos os comandos disponíveis na ferramenta.",
            },
            "exit": {
                "icon": "7️⃣",
                "title": "Sair",
                "description": "Encerra a sessão atual do agente Git AI e finaliza a aplicação.",
            },
        }

        print("\n📋 Detalhes dos Comandos")
        print("=" * 80)

        for i, (command, info) in enumerate(details.items()):
            print(f"{info['icon']} {info['title']} ({command})")
            print("-" * 80)
            for line in info["description"].split("\n"):
                print(line)

            if i < len(details) - 1:
                print("=" * 80)

    async def run(self):
        """Loop principal"""
        if self.config_manager.is_first_run():
            self.first_time_setup()

        print("\n🤖 Git AI Agent (LangGraph) ativado!")
        print("=" * 60)
        print("Comandos:")
        print("  analyze - Analisa código")
        print("  danalyze - Análise profunda do código")
        print("  up      - Commit e push")
        print("  mermaid - Mostra o código Mermaid do grafo")
        print("  details - Detalhes dos comandos")
        print("  config  - Configurações")
        print("  exit    - Sair")
        print("=" * 60)

        while self.active:
            try:
                command = input("\n🎯 gitcast> ").strip().lower()

                if command == "analyze":
                    await self.analyze_changes()
                elif command == "danalyze":
                    await self.deep_analyze()
                elif command == "up":
                    await self.commit_and_push()
                elif command == "mermaid":
                    print(self.graph.get_graph().draw_mermaid())
                elif command == "config":
                    self.configure()
                elif command == "details":
                    self.get_details()
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
