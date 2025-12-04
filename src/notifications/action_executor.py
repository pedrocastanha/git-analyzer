import os

from .suggestion_builder import Suggestion, SuggestionType


class ActionExecutor:
    def __init__(self, agent_ref):
        self.agent = agent_ref
        self.repo_path = agent_ref.repo_path
        self.config = agent_ref.config_manager.config
        self.language = self.config.get("language", "pt")

    async def execute(self, suggestion: Suggestion) -> bool:
        """Executa uma sugestão."""
        print("\n" + "=" * 80)
        if self.language == "pt":
            print(f"🔧 Executando: {suggestion.title}")
        else:
            print(f"🔧 Executing: {suggestion.title}")
        print("=" * 80 + "\n")

        try:
            if suggestion.type == SuggestionType.COMMIT:
                return await self._execute_commit(suggestion)
            elif suggestion.type == SuggestionType.FIX_ERROR:
                return await self._execute_code_change(suggestion, "fix")
            elif suggestion.type == SuggestionType.IMPROVE:
                return await self._execute_code_change(suggestion, "improve")
            elif suggestion.type == SuggestionType.SECURITY:
                return await self._execute_security_fix(suggestion)
            elif suggestion.type == SuggestionType.REFACTOR:
                return await self._execute_code_change(suggestion, "refactor")
            else:
                print(f"Tipo de ação não implementado: {suggestion.type}")
                return False
        except Exception as e:
            print(f"❌ Erro ao executar ação: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def _execute_commit(self, suggestion: Suggestion) -> bool:
        """Executa commit usando o split-up existente."""
        print("📤 Usando comando 'up' para commit...")
        await self.agent.commit_and_push()
        return True

    async def _execute_code_change(self, suggestion: Suggestion, change_type: str) -> bool:
        """
        Executa uma alteração de código (fix, improve ou refactor).

        FLUXO:
        1. Verifica se tem old_code e new_code nos dados
        2. Mostra diff visual (vermelho → verde)
        3. Pede confirmação
        4. Aplica a mudança diretamente no arquivo
        """
        file_path = suggestion.data.get("file")
        old_code = suggestion.data.get("old_code")
        new_code = suggestion.data.get("new_code")
        line = suggestion.data.get("line", "?")

        if not file_path or not old_code or not new_code:
            print(f"📝 Sugestão de {change_type}:")
            print(f"   {suggestion.description}")
            if file_path:
                print(f"   Arquivo: {file_path}:{line}")
            print("\n⚠️  Aplicação manual necessária (dados insuficientes para auto-aplicar)")
            return False

        full_path = os.path.join(self.repo_path, file_path)

        if not os.path.exists(full_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False

        with open(full_path, 'r', encoding='utf-8') as f:
            current_content = f.read()

        if old_code not in current_content:
            print(f"⚠️  Código original não encontrado no arquivo.")
            print(f"   Procurando: {old_code[:100]}...")
            print("\n💡 O código pode ter sido modificado. Verifique manualmente.")
            return False

        self._show_visual_diff(file_path, line, old_code, new_code)

        if self.language == "pt":
            confirm = input("\n✅ Aplicar esta alteração? (s/n): ").strip().lower()
        else:
            confirm = input("\n✅ Apply this change? (y/n): ").strip().lower()

        if confirm not in ["s", "sim", "y", "yes"]:
            if self.language == "pt":
                print("❌ Operação cancelada.")
            else:
                print("❌ Operation cancelled.")
            return False

        new_content = current_content.replace(old_code, new_code, 1)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if self.language == "pt":
            print(f"✅ Alteração aplicada em {file_path}")
        else:
            print(f"✅ Change applied to {file_path}")

        return True

    def _show_visual_diff(self, file_path: str, line: any, old_code: str, new_code: str):
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        CYAN = "\033[96m"
        RESET = "\033[0m"
        DIM = "\033[2m"

        print(f"\n{CYAN}📄 Arquivo: {file_path}:{line}{RESET}")
        print(f"{DIM}{'─' * 60}{RESET}")

        print(f"\n{RED}━━━ REMOVER ━━━{RESET}")
        for line_text in old_code.split('\n'):
            print(f"{RED}- {line_text}{RESET}")

        print(f"\n{GREEN}━━━ ADICIONAR ━━━{RESET}")
        for line_text in new_code.split('\n'):
            print(f"{GREEN}+ {line_text}{RESET}")

        print(f"\n{DIM}{'─' * 60}{RESET}")

    async def _execute_security_fix(self, suggestion: Suggestion) -> bool:
        RED = "\033[91m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"

        print(f"{RED}🔒 ALERTA DE SEGURANÇA{RESET}")
        print(f"{YELLOW}   {suggestion.description}{RESET}")
        print("\n⚠️  Esta é uma correção de segurança crítica!")

        if self.language == "pt":
            confirm = input("\nDeseja aplicar a correção de segurança? (s/n): ").strip().lower()
        else:
            confirm = input("\nApply security fix? (y/n): ").strip().lower()

        if confirm not in ["s", "sim", "y", "yes"]:
            print("❌ Operação cancelada")
            return False

        return await self._execute_code_change(suggestion, "security")
