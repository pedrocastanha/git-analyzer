import asyncio
import sys
import git

from src.config import ConfigManager
from src.core.graph import create_analysis_graph, create_commit_graph


class GitAIAgent:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.config_manager = ConfigManager(repo_path)

        self.analysis_graph = create_analysis_graph()
        self.commit_graph = create_commit_graph()

        self.active = True

        print(f"GitAIAgent initialized for repository at {self.repo_path}")
        print(f"Provider: {self.config_manager.get('ai_provider')}")

    async def analyze_changes(self):
        print("Iniciando análise de mudanças no repositório...")

        initial_state = {
            'messages': [],
            'diff': None,
            'analysis': None,
            'commit_message': None,
            'patch': None,
            'current_action': 'analyze',
            'user_confirmation': None,
            'error': None,
            'repo_path': self.repo_path,
            'config': self.config_manager.config
        }

        config = {"configurable": {"thread_id": "analyze_thread"}}

        result = await self.analysis_graph.invoke(initial_state, config)

        if result.get('error'):
            print(f"\n{result['error']}")

        if not result.get('analysis'):
            print("\n📭 Nenhuma mudança para analisar.")
            return

        print("\n" + "=" * 60)
        print(result['analysis'])
        print("=" * 60)

        choice = input("\nDeseja melhorias sugeridas? (s/n): ").strip().lower()
        result['user_confirmation'] = (choice == 's')

        if result['user_confirmation']:
            result = await self.analysis_graph.invoke(result, config)

            if result.get('patch'):
                print("\nPatch gerado:\n")
                print(result['patch'][:500] + "..." if len(result['patch']) > 500 else result['patch'])

                apply = input("\n🔨 Aplicar este patch? (s/n): ").strip().lower()
                result['user_confirmation'] = (apply == 's')

                if result['user_confirmation']:
                    await self.analysis_graph.invoke(result, config)
            else:
                print("\n✅ Nenhuma melhoria automática necessária.")

    async def commit_and_push(self):
        """Executa o grafo de commit"""
        print("\n📤 Iniciando commit e push...")
        print("=" * 60)

        initial_state = {
            'messages': [],
            'diff': None,
            'analysis': None,
            'commit_message': None,
            'patch': None,
            'current_action': 'commit',
            'user_confirmation': None,
            'error': None,
            'repo_path': self.repo_path,
            'config': self.config_manager.config
        }

        config = {"configurable": {"thread_id": "commit_thread"}}

        result = await self.commit_graph.invoke(initial_state, config)

        if result.get('error'):
            print(f"\n{result['error']}")
            return

        print(f"\n✅Mensagem sugerida: {result['commit_message']}.")

        confirm = input("\n✅ Confirmar commit e push? (s/n): ").strip().lower()
        result['user_confirmation'] = (confirm == 's')

        if result['user_confirmation']:
            await self.commit_graph.invoke(result, config)

    def configure(self):
        """Menu de configuração"""
        print("\n⚙️  Configuração")
        print("=" * 60)
        print("1. Escolher provider de IA")
        print("2. Configurar API keys")
        print("3. Ver configuração")
        print("0. Voltar")
        print("=" * 60)

        choice = input("\nEscolha: ").strip()

        if choice == '1':
            print("\nProviders:")
            print("  1. Claude")
            print("  2. OpenAI")
            print("  3. Ollama")
            print("  4. Gemini")

            p = input("\nEscolha: ").strip()
            providers = {'1': 'claude', '2': 'openai', '3': 'ollama', '4': 'gemini'}

            if p in providers:
                self.config_manager.set('ai_provider', providers[p])
                self.config_manager.save_config()
                print(f"✅ Provider: {providers[p]}")

        elif choice == '2':
            provider = self.config_manager.get('ai_provider')
            key_name = f'{provider}_api_key' if provider != 'ollama' else 'ollama_url'

            if provider != 'ollama':
                key = input(f"{provider.upper()} API Key: ").strip()
                if key:
                    self.config_manager.set(key_name, key)
                    self.config_manager.save_config()
                    print("✅ API Key configurada!")

        elif choice == '3':
            print("\n📋 Configuração atual:")
            for k, v in self.config_manager.config.items():
                if 'api_key' in k and v:
                    v = v[:8] + "..." + v[-4:]
                print(f"  {k}: {v}")

    async def run(self):
        """Loop principal"""
        print("\n🤖 Git AI Agent (LangGraph) ativado!")
        print("=" * 60)
        print("Comandos:")
        print("  analyze - Analisa código")
        print("  up      - Commit e push")
        print("  config  - Configurações")
        print("  exit    - Sair")
        print("=" * 60)

        while self.active:
            try:
                command = input("\n🎯 castanha123> ").strip().lower()

                if command == "analyze":
                    await self.analyze_changes()
                elif command == "up":
                    await self.commit_and_push()
                elif command == "config":
                    self.configure()
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