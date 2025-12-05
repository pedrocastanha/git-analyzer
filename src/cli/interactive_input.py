import sys
import time
import asyncio
from typing import Optional, Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style

COMPLETION_STYLE = Style.from_dict({
    'completion-menu': 'bg:#1e1e2e #cdd6f4',
    'completion-menu.completion': 'bg:#1e1e2e #cdd6f4',
    'completion-menu.completion.current': 'bg:#45475a #f5e0dc bold',

    'completion-menu.meta': 'bg:#1e1e2e #6c7086 italic',
    'completion-menu.meta.current': 'bg:#45475a #f5c2e7 italic',

    'scrollbar.background': 'bg:#313244',
    'scrollbar.button': 'bg:#585b70',
})


class DoubleCtrlCExit(Exception):
    """Levantada quando usuário pressiona Ctrl+C duas vezes."""
    pass


class InteractiveInput:
    def __init__(self, completer, flag_checker: Optional[Callable] = None):
        self.flag_checker = flag_checker
        self.is_tty = sys.stdin.isatty()
        self.completer = completer

        self._last_ctrl_c_time = 0
        self._ctrl_c_timeout = 2.0
        self._exit_requested = False
        self._injected_command = None

        if self.is_tty:
            kb = self._create_key_bindings()

            self.session = PromptSession(
                completer=completer,
                complete_while_typing=True,
                enable_history_search=True,
                key_bindings=kb,
                vi_mode=False,
                complete_in_thread=True,
                style=COMPLETION_STYLE,
            )
        else:
            self.session = None

    def inject_command(self, command: str):
        """
        Injeta um comando para ser executado na próxima iteração.
        Usado quando a notificação é clicada para executar 'suggestions' automaticamente.
        """
        self._injected_command = command

    def _create_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        input_handler = self

        @kb.add('/')
        def handle_slash(event):
            buffer = event.app.current_buffer
            buffer.insert_text('/')

            buffer.start_completion(select_first=False)

        @kb.add('c-c')
        def handle_ctrl_c(event):
            current_time = time.time()

            if current_time - input_handler._last_ctrl_c_time < input_handler._ctrl_c_timeout:
                input_handler._exit_requested = True
                event.app.exit(result='__EXIT__')
            else:
                input_handler._last_ctrl_c_time = current_time
                print("\n⚠️  Pressione Ctrl+C novamente para sair...")

                event.app.current_buffer.reset()

        @kb.add('escape')
        def handle_escape(event):
            buffer = event.app.current_buffer

            if buffer.complete_state:
                buffer.cancel_completion()
            else:
                buffer.reset()

        return kb

    async def get_input(self, prompt_text: str) -> Optional[str]:
        # Verifica se há comando injetado (ex: clique na notificação)
        if self._injected_command:
            cmd = self._injected_command
            self._injected_command = None
            print(f"{prompt_text}{cmd}")
            return cmd

        if self.flag_checker:
            simulated = self.flag_checker()
            if simulated:
                print(f"{prompt_text}{simulated}")
                return simulated

        if not self.is_tty:
            try:
                print(prompt_text, end='', flush=True)
                result = input()
                return result.strip()
            except (KeyboardInterrupt, EOFError):
                return None

        try:
            with patch_stdout():
                prompt_task = asyncio.create_task(
                    self.session.prompt_async(prompt_text)
                )

                while not prompt_task.done():
                    if self._injected_command:
                        cmd = self._injected_command
                        self._injected_command = None
                        prompt_task.cancel()
                        try:
                            await prompt_task
                        except asyncio.CancelledError:
                            pass
                        print(f"\n{prompt_text}{cmd}")
                        return cmd

                    try:
                        result = await asyncio.wait_for(
                            asyncio.shield(prompt_task),
                            timeout=0.1
                        )
                        if result == '__EXIT__' or self._exit_requested:
                            self._exit_requested = False
                            raise DoubleCtrlCExit()
                        return result.strip()
                    except asyncio.TimeoutError:
                        continue

                result = prompt_task.result()

                if result == '__EXIT__' or self._exit_requested:
                    self._exit_requested = False
                    raise DoubleCtrlCExit()

                return result.strip()
        except (KeyboardInterrupt, EOFError):
            return None
        except asyncio.CancelledError:
            return None
