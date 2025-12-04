from typing import Optional, Callable
import sys
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style


# Estilo visual do menu de completions (inspirado no Claude Code)
COMPLETION_STYLE = Style.from_dict({
    # Menu dropdown
    'completion-menu': 'bg:#1e1e2e #cdd6f4',           # Fundo escuro, texto claro
    'completion-menu.completion': 'bg:#1e1e2e #cdd6f4', # Item normal
    'completion-menu.completion.current': 'bg:#45475a #f5e0dc bold',  # Item selecionado

    # Meta text (descrição à direita)
    'completion-menu.meta': 'bg:#1e1e2e #6c7086 italic',
    'completion-menu.meta.current': 'bg:#45475a #f5c2e7 italic',

    # Scrollbar
    'scrollbar.background': 'bg:#313244',
    'scrollbar.button': 'bg:#585b70',
})


# Exceção customizada para Ctrl+C duplo
class DoubleCtrlCExit(Exception):
    """Levantada quando usuário pressiona Ctrl+C duas vezes."""
    pass


class InteractiveInput:
    """
    Sistema de input interativo usando prompt_toolkit.

    FUNCIONALIDADES:
    ┌────────────────────────────────────────────────────────────┐
    │ Recurso              │ Como Usar                           │
    ├──────────────────────┼─────────────────────────────────────┤
    │ Menu de comandos     │ Digite "/" → abre dropdown          │
    │ Filtrar comandos     │ Digite "/an" → filtra para analyze  │
    │ Navegar              │ Setas ↑↓ para mover                 │
    │ Selecionar           │ Enter ou Tab                        │
    │ Cancelar             │ ESC                                 │
    │ Histórico            │ Ctrl+R para buscar                  │
    └────────────────────────────────────────────────────────────┘
    """

    def __init__(self, completer, flag_checker: Optional[Callable] = None):
        """
        Inicializa o input interativo.

        Args:
            completer: Completer do prompt_toolkit (GitcastCompleter)
            flag_checker: Callable que retorna comando simulado ou None
        """
        self.flag_checker = flag_checker
        self.is_tty = sys.stdin.isatty()
        self.completer = completer

        # Controle de Ctrl+C duplo
        self._last_ctrl_c_time = 0
        self._ctrl_c_timeout = 2.0  # Segundos entre Ctrl+C para considerar "duplo"

        # Criar sessão apenas se for um terminal real
        if self.is_tty:
            # Configurar key bindings customizados
            kb = self._create_key_bindings()

            # Criar sessão com autocomplete e histórico
            self.session = PromptSession(
                completer=completer,
                # Autocomplete em tempo real conforme digita
                complete_while_typing=True,
                # Ctrl+R para buscar no histórico de comandos
                enable_history_search=True,
                key_bindings=kb,
                vi_mode=False,  # Modo emacs (padrão, mais intuitivo)
                # Processamento de completion em thread separada (não trava UI)
                complete_in_thread=True,
                # Estilo visual do menu
                style=COMPLETION_STYLE,
            )
        else:
            # Não criar session quando não é terminal (evita warnings)
            self.session = None

    def _create_key_bindings(self) -> KeyBindings:
        """
        Cria key bindings customizados para o prompt.

        KEY BINDINGS CONFIGURADOS:
        - /: Insere "/" E abre o menu de comandos automaticamente
        - Ctrl+C: Primeiro avisa, segundo sai do programa
        - ESC: Fecha menu ou limpa input
        - Tab: Aceita completion selecionada
        - Enter: Confirma comando
        - ↑↓: Navega entre completions

        Returns:
            KeyBindings: Configuração de teclas
        """
        kb = KeyBindings()

        # Referência ao self para usar dentro dos handlers
        input_handler = self

        @kb.add('/')
        def handle_slash(event):
            """
            "/" → Insere a barra E abre o menu de completions.

            POR QUE ISSO É NECESSÁRIO:
            - complete_while_typing só mostra menu se já há texto
            - "/" sozinho não dispara o autocomplete automaticamente
            - Este binding FORÇA a abertura do menu imediatamente
            """
            buffer = event.app.current_buffer

            # 1. Insere o "/" no texto
            buffer.insert_text('/')

            # 2. Força abertura do menu de completions
            #    select_first=False = não auto-seleciona, deixa usuário escolher
            buffer.start_completion(select_first=False)

        @kb.add('c-c')  # Ctrl+C
        def handle_ctrl_c(event):
            """
            Ctrl+C → Sistema de saída com confirmação.

            COMPORTAMENTO:
            - Primeiro Ctrl+C: Mostra aviso e limpa input
            - Segundo Ctrl+C (dentro de 2s): Sai do programa
            """
            current_time = time.time()

            if current_time - input_handler._last_ctrl_c_time < input_handler._ctrl_c_timeout:
                # Ctrl+C duplo detectado → levanta exceção para sair
                raise DoubleCtrlCExit()
            else:
                # Primeiro Ctrl+C → avisa e reseta
                input_handler._last_ctrl_c_time = current_time
                print("\n⚠️  Pressione Ctrl+C novamente para sair...")

                # Limpa o buffer atual
                event.app.current_buffer.reset()

        @kb.add('escape')
        def handle_escape(event):
            """
            ESC → Fecha menu ou limpa input.
            - Se menu aberto: fecha o menu
            - Se menu fechado: limpa toda a linha
            """
            buffer = event.app.current_buffer

            if buffer.complete_state:
                # Menu aberto → fecha
                buffer.cancel_completion()
            else:
                # Sem menu → limpa tudo
                buffer.reset()

        return kb

    async def get_input(self, prompt_text: str) -> Optional[str]:
        """
        Captura input do usuário com autocomplete e histórico (ASYNC).

        Antes de mostrar o prompt, checa se há flags ativas
        (ex: notificação clicada) e simula comando se necessário.

        Args:
            prompt_text: Texto do prompt a ser exibido

        Returns:
            Comando digitado pelo usuário ou None se cancelado
        """
        # Checar flag antes de pedir input
        if self.flag_checker:
            simulated = self.flag_checker()
            if simulated:
                print(f"{prompt_text}{simulated}")
                return simulated

        # Se não for terminal, usar input() simples (sem warnings)
        if not self.is_tty:
            try:
                print(prompt_text, end='', flush=True)
                result = input()
                return result.strip()
            except (KeyboardInterrupt, EOFError):
                return None

        # Mostrar prompt interativo (versão async!)
        try:
            # patch_stdout evita conflito com prints assíncronos do file watcher
            with patch_stdout():
                result = await self.session.prompt_async(prompt_text)
                return result.strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C ou Ctrl+D - retorna None
            return None
