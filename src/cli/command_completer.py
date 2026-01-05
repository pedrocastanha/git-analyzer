from typing import Dict, Iterable
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


class GitcastCompleter(Completer):
    COMMANDS: Dict[str, str] = {
        "analyze": "Analisa mudanças no código",
        "danalyze": "Análise profunda com multi-agentes",
        "up": "Commit e push automático",
        "split-up": "Divide diff em commits menores",
        "suggestions": "Mostra sugestões da IA",
        "config": "Menu de configurações",
        "usage": "Mostra estatísticas de uso",
        "mermaid": "Visualiza grafo do workflow",
        "details": "Detalhes de todos os comandos",
        "exit": "Sair do gitcast"
    }

    def get_completions(
        self,
        document: Document,
        complete_event
    ) -> Iterable[Completion]:
        text = document.text_before_cursor.strip()

        if text == "/" or text == "":
            filter_text = ""
        elif text.startswith("/"):
            filter_text = text[1:]
        else:
            filter_text = text

        if text.startswith("/"):
            start_position = -len(text)
        else:
            start_position = -len(filter_text)

        for cmd, description in self.COMMANDS.items():
            if cmd.startswith(filter_text.lower()):
                yield Completion(
                    text=cmd,
                    start_position=start_position,
                    display=f"/{cmd}",
                    display_meta=description,
                    style="class:completion-item",
                    selected_style="class:completion-item-selected"
                )
