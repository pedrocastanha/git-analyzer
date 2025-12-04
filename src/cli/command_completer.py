from typing import Dict, Iterable
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


class GitcastCompleter(Completer):
    """
    Completer customizado para comandos gitcast.

    Comportamento:
    - Ao digitar "/" → mostra TODOS os comandos (como Claude Code)
    - Ao digitar "/an" → filtra para comandos que começam com "an"
    - Ao digitar "an" → filtra para comandos que começam com "an"
    - Navegação com setas ↑↓, Enter para selecionar, ESC para cancelar
    """

    # Comandos disponíveis com descrições
    # O formato é: comando → descrição curta
    COMMANDS: Dict[str, str] = {
        "analyze": "Analisa mudanças no código",
        "danalyze": "Análise profunda com multi-agentes",
        "up": "Commit e push automático",
        "split-up": "Divide diff em commits menores",
        "suggestions": "Mostra sugestões da IA",
        "config": "Menu de configurações",
        "mermaid": "Visualiza grafo do workflow",
        "details": "Detalhes de todos os comandos",
        "exit": "Sair do gitcast"
    }

    def get_completions(
        self,
        document: Document,
        complete_event
    ) -> Iterable[Completion]:
        """
        Retorna completions baseados no texto digitado.

        LÓGICA DO AUTOCOMPLETE:
        ┌─────────────────────────────────────────────────────┐
        │ Input do Usuário    │ Comportamento                 │
        ├─────────────────────┼───────────────────────────────┤
        │ "/" ou ""           │ Mostra TODOS os comandos      │
        │ "/an" ou "an"       │ Filtra: analyze               │
        │ "/co" ou "co"       │ Filtra: config                │
        └─────────────────────────────────────────────────────┘

        Args:
            document: Documento atual com texto e posição do cursor
            complete_event: Evento de completion (não usado aqui)

        Yields:
            Completion: Cada sugestão de comando que faz match
        """
        # Pega TODO o texto digitado até o cursor
        text = document.text_before_cursor.strip()

        # Determina o filtro baseado no texto
        # Se é "/" sozinho OU vazio → mostra tudo
        # Se começa com "/" → remove o "/" e usa o resto como filtro
        # Senão → usa o texto como filtro
        if text == "/" or text == "":
            filter_text = ""
        elif text.startswith("/"):
            filter_text = text[1:]  # Remove o "/" do início
        else:
            filter_text = text

        # Calcula quantos caracteres "voltar" para substituir
        # Se começou com "/", inclui o "/" na substituição
        if text.startswith("/"):
            start_position = -len(text)  # Substitui "/" + filtro
        else:
            start_position = -len(filter_text)  # Substitui só o texto

        # Gera completions para cada comando que faz match
        for cmd, description in self.COMMANDS.items():
            if cmd.startswith(filter_text.lower()):
                yield Completion(
                    text=cmd,                           # Texto que será inserido
                    start_position=start_position,      # Onde começar a substituir
                    display=f"/{cmd}",                  # Como aparece no menu (com /)
                    display_meta=description,           # Descrição à direita
                    style="class:completion-item",      # Estilo CSS (opcional)
                    selected_style="class:completion-item-selected"  # Quando selecionado
                )
