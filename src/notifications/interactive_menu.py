from typing import List, Optional
from .suggestion_builder import Suggestion, SuggestionType


class InteractiveMenu:
    """Menu interativo"""

    def __init__(self, language: str = "pt"):
        self.language = language

    def show_suggestions(self, suggestions: List[Suggestion]) -> Optional[int]:
        if not suggestions:
            if self.language == "pt":
                print("\nNenhuma sugestao no momento.\n")
            else:
                print("\nNo suggestions at the moment.\n")
            return None

        print("\n" + "=" * 80)
        if self.language == "pt":
            print(f"SUGESTOES DA IA: {len(suggestions)}")
        else:
            print(f"AI SUGGESTIONS: {len(suggestions)}")
        print("=" * 80 + "\n")

        for idx, suggestion in enumerate(suggestions, 1):
            self._print_suggestion(idx, suggestion)
            print()

        print("=" * 80)
        if self.language == "pt":
            print(f"\n[1-{len(suggestions)}] Executar | [0] Ignorar | [d] Detalhes")
            choice = input("\nSua escolha: ").strip().lower()
        else:
            print(f"\n[1-{len(suggestions)}] Execute | [0] Ignore | [d] Details")
            choice = input("\nYour choice: ").strip().lower()

        if choice == "0":
            return None

        if choice == "d":
            self._show_details(suggestions)
            return self.show_suggestions(suggestions)

        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(suggestions):
                selected = suggestions[choice_num - 1]
                if not selected.auto_executable:
                    if not self._confirm_action(selected):
                        return None
                return choice_num - 1
            else:
                print("Opcao invalida!")
                return self.show_suggestions(suggestions)
        except ValueError:
            print("Opcao invalida!")
            return self.show_suggestions(suggestions)

    def _print_suggestion(self, index: int, suggestion: Suggestion):
        emoji = suggestion.get_emoji()
        priority_stars = "*" * suggestion.priority

        if suggestion.priority >= 4:
            color = "\033[91m"
        elif suggestion.priority >= 3:
            color = "\033[93m"
        else:
            color = "\033[92m"

        reset = "\033[0m"

        print(f"{color}[{index}] {emoji} {suggestion.title}{reset}")
        print(f"    {priority_stars} | {suggestion.description[:80]}...")

        if suggestion.type == SuggestionType.COMMIT:
            msg = suggestion.data.get("message", "")
            if msg:
                print(f"    MSG: {msg}")
        elif suggestion.type == SuggestionType.FIX_ERROR:
            file_info = suggestion.data.get("file")
            line_info = suggestion.data.get("line")
            if file_info:
                print(f"    FILE: {file_info}:{line_info if line_info else '?'}")

    def _show_details(self, suggestions: List[Suggestion]):
        print("\n" + "=" * 80)
        print("DETALHES COMPLETOS")
        print("=" * 80 + "\n")

        for idx, suggestion in enumerate(suggestions, 1):
            print(f"{idx}. {suggestion.get_emoji()} {suggestion.title}")
            print(f"   Tipo: {suggestion.type.value}")
            print(f"   Prioridade: {'*' * suggestion.priority}")
            print(f"   Descricao: {suggestion.description}")
            print(f"   Auto-executavel: {'Sim' if suggestion.auto_executable else 'Nao'}")
            print(f"   Dados: {suggestion.data}")
            print()

        input("\n[Enter para voltar]")

    def _confirm_action(self, suggestion: Suggestion) -> bool:
        print("\n" + "=" * 80)
        print("CONFIRMACAO NECESSARIA")
        print("=" * 80)
        print(f"\nVoce esta prestes a executar:")
        print(f"  {suggestion.get_emoji()} {suggestion.title}")
        print(f"  {suggestion.description}")
        print()

        if self.language == "pt":
            confirm = input("Confirmar? (s/n): ").strip().lower()
            return confirm in ["s", "sim", "y", "yes"]
        else:
            confirm = input("Confirm? (y/n): ").strip().lower()
            return confirm in ["y", "yes", "s", "sim"]

    def show_pending_suggestions_prompt(self, count: int):
        if count == 0:
            return

        print("\n" + "=" * 80)
        if self.language == "pt":
            print(f"Voce tem {count} sugestao(oes) pendente(s)!")
            print("   Digite 'suggestions' para ver")
        else:
            print(f"You have {count} pending suggestion(s)!")
            print("   Type 'suggestions' to view")
        print("=" * 80 + "\n")
