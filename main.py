import asyncio
import sys
import traceback

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

        result = await self.graph.ainvoke(initial_state)

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
            result = await self.graph.ainvoke(result)

            if result.get('patch'):
                print("\nPatch gerado:\n")
                print(result['patch'][:500] + "..." if len(result['patch']) > 500 else result['patch'])

                apply = input("\n🔨 Aplicar este patch? (s/n): ").strip().lower()
                result['user_confirmation'] = (apply == 's')

                if result['user_confirmation']:
                    await self.graph.ainvoke(result)
            else:
                print("\n✅ Nenhuma melhoria automática necessária.")

    async def deep_analyze(self):
        print("\n" + "=" * 80)
        print("🔍 ANÁLISE PROFUNDA - Multi-Agent Code Review")
        print("=" * 80)
        print("Os agentes Crítico e Construtivo irão discutir as mudanças...")
        print("Aguarde, isso pode levar alguns minutos.\n")

        initial_state = {
            'messages': [],
            'diff': None,
            'analysis': None,
            'commit_message': None,
            'patch': None,
            'current_action': 'deep_analyze',
            'user_confirmation': None,
            'error': None,
            'repo_path': self.repo_path,
            'config': self.config_manager.config
        }

        try:
            result = await self.graph.ainvoke(initial_state)
        except Exception as e:
            print(f"\n❌ Erro durante a execução: {str(e)}")
            import traceback
            traceback.print_exc()
            return

        if result.get('error'):
            print(f"\n{result['error']}")
            return

        conversation = result.get('conversation_history', [])

        if not conversation:
            print("\n📭 Nenhuma análise foi gerada.")
            return

        print("\n" + "=" * 80)
        print("📊 RESUMO DA DISCUSSÃO ENTRE OS AGENTES")
        print("=" * 80)
        print(f"\n💬 Total de mensagens: {len(conversation)}\n")

        for i, msg in enumerate(conversation, 1):
            agent_name = getattr(msg, 'name', 'Agente Desconhecido')
            content = getattr(msg, 'content', '')

            if "Crítico" in agent_name:
                color = '\033[91m'
                emoji = "🔴"
            else:
                color = '\033[92m'
                emoji = "🟢"

            reset = '\033[0m'

            print(f"{emoji} [{i}] {agent_name}")
            print("-" * 80)

            if len(content) > 400:
                print(f"{color}{content[:400]}...{reset}")
                print(f"\n[... {len(content) - 400} caracteres omitidos ...]")
            else:
                print(f"{color}{content}{reset}")

            print("\n")

        print("=" * 80)

        if result.get('analysis'):
            print("\n📋 PLANO DE AÇÃO FINAL")
            print("=" * 80)
            print(result['analysis'])
            print("=" * 80)

        if not result.get('patch'):
            print("\n✅ Análise concluída!")
            print("Os agentes não identificaram necessidade de mudanças automáticas.")
            return

        print("\n📦 PATCH GERADO")
        print("=" * 80)

        patch = result['patch']
        patch_lines = patch.split('\n')

        if len(patch_lines) > 20:
            preview = '\n'.join(patch_lines[:20])
            print(preview)
            print(f"\n... ({len(patch_lines) - 20} linhas restantes)")
        else:
            print(patch)

        print("=" * 80)

        print(f"\n📊 Estatísticas do patch:")
        print(f"   • Total de linhas: {len(patch_lines)}")
        print(f"   • Tamanho: {len(patch)} caracteres")

        apply = input("\n🔨 Deseja aplicar este patch? (s/n): ").strip().lower()

        if apply != 's':
            print("\n⏭️  Patch não aplicado. Análise salva.")
            return

        # Aplicar o patch manualmente (o grafo já terminou, mas o patch está em result['patch'])
        try:
            import os
            os.makedirs("/tmp/ai_git", exist_ok=True)
            patch_file = "/tmp/ai_git/patch.patch"

            # Salva o patch que já está na memória
            with open(patch_file, 'w') as f:
                f.write(result['patch'])

            # Aplica o patch usando git
            repo = git.Repo(self.repo_path)
            repo.git.apply(patch_file)

            print("\n✅ Patch aplicado com sucesso!")
            print("As mudanças foram aplicadas ao seu repositório.")

        except Exception as e:
            print(f"\n❌ Erro ao aplicar patch: {str(e)}")
            import traceback
            traceback.print_exc()

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

        result = await self.graph.ainvoke(initial_state)

        if result.get('error'):
            print(f"\n{result['error']}")
            return

        GREEN = '\033[92m'
        RESET = '\033[0m'

        print(f"\n✅Mensagem sugerida:\n {GREEN}{result['commit_message']}{RESET}.")

        confirm = input("\n✅ Confirmar commit e push? (s/n): ").strip().lower()
        result['user_confirmation'] = (confirm == 's')

        if result['user_confirmation']:
            await self.graph.ainvoke(result)

    def first_time_setup(self):
        """Setup inicial interativo"""
        print("\n" + "=" * 60)
        print("🎉 Bem-vindo ao castanhafodao!")
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
            if provider_choice in ['1', '2']:
                break
            print("❌ Opção inválida. Digite 1 ou 2.")

        provider = 'openai' if provider_choice == '1' else 'gemini'
        self.config_manager.set('ai_provider', provider)

        print(f"\n✅ Provider selecionado: {provider.upper()}")
        print("")

        print("=" * 60)
        print("🔑 Configure sua API Key:")
        print("=" * 60)

        if provider == 'openai':
            print("\n💡 Onde conseguir:")
            print("   https://platform.openai.com/api-keys")
            print("")
            api_key = input("Cole sua OpenAI API Key: ").strip()
            if api_key:
                self.config_manager.set('openai_api_key', api_key)
                print("✅ API Key configurada!")
            else:
                print("⚠️  Nenhuma key fornecida. Configure depois com 'config'.")
        else:
            print("\n💡 Onde conseguir:")
            print("   https://aistudio.google.com/app/apikey")
            print("")
            api_key = input("Cole sua Gemini API Key: ").strip()
            if api_key:
                self.config_manager.set('gemini_api_key', api_key)
                print("✅ API Key configurada!")
            else:
                print("⚠️  Nenhuma key fornecida. Configure depois com 'config'.")

        self.config_manager.save_config()

        print("\n" + "=" * 60)
        print("✅ Configuração concluída!")
        print("=" * 60)
        print("\n📚 Dica: Use 'config' para alterar configurações a qualquer momento.\n")

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
            print("  1. OpenAI")
            print("  2. Gemini")

            p = input("\nEscolha: ").strip()
            providers = {'1': 'openai', '2': 'gemini'}

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
        if self.config_manager.is_first_run():
            self.first_time_setup()

        print("\n🤖 Git AI Agent (LangGraph) ativado!")
        print("=" * 60)
        print("Comandos:")
        print("  analyze - Analisa código")
        print("  danalyze - Análise profunda do código")
        print("  up      - Commit e push")
        print("  config  - Configurações")
        print("  mermaid - Mostra o código Mermaid do grafo")
        print("  exit    - Sair")
        print("=" * 60)

        while self.active:
            try:
                command = input("\n🎯 castanhafodao> ").strip().lower()

                if command == "analyze":
                    await self.analyze_changes()
                elif command == "danalyze":
                    await self.deep_analyze()
                elif command == "up":
                    await self.commit_and_push()
                elif command == "config":
                    self.configure()
                elif command == "mermaid":
                    print(self.graph.get_graph().draw_mermaid())
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