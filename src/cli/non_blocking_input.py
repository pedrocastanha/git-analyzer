import sys
import select
import threading
from typing import Optional, Callable


class NonBlockingInput:
    def __init__(self, check_callback: Optional[Callable[[], Optional[str]]] = None):
        """
        Args:
            check_callback: Função chamada periodicamente. Se retornar string,
                          simula input daquela string.
        """
        self.check_callback = check_callback
        self.is_windows = sys.platform.startswith('win')

    def get_input(self, prompt: str = "", timeout: float = 0.5) -> Optional[str]:
        """Pega input do usuário com checagens periódicas.

        🎓 CONCEITO: Input com timeout usando select

        FUNCIONAMENTO:
        1. Mostra prompt
        2. A cada `timeout` segundos, checa se stdin tem dados
        3. Se tiver dados, lê input
        4. Se não tiver, chama check_callback para verificar flags
        5. Repete até ter input

        Args:
            prompt: Prompt a mostrar
            timeout: Intervalo de checagem (segundos)

        Returns:
            String digitada pelo usuário ou string simulada via callback
        """
        if self.is_windows:
            # Windows: fallback simples
            return self._get_input_windows(prompt)

        # Linux/Mac: select com timeout
        return self._get_input_unix(prompt, timeout)

    def _get_input_unix(self, prompt: str, timeout: float) -> Optional[str]:
        """Input não-bloqueante para Unix/Linux usando select."""
        print(prompt, end='', flush=True)

        while True:
            # Checa callback antes de cada select
            if self.check_callback:
                simulated = self.check_callback()
                if simulated is not None:
                    # Callback retornou comando simulado!
                    print(simulated)  # Mostra o que foi "digitado"
                    return simulated

            # Espera até timeout por input em stdin
            ready, _, _ = select.select([sys.stdin], [], [], timeout)

            if ready:
                # Stdin tem dados - usuário digitou algo
                return sys.stdin.readline().strip()

            # Timeout - loop continua, checará callback novamente

    def _get_input_windows(self, prompt: str) -> str:
        """Fallback para Windows - input bloqueante normal.

        🎓 CONCEITO: Limitação do Windows

        Windows não suporta select() em stdin.
        Alternativas:
        - msvcrt.kbhit() + msvcrt.getch() (complexo)
        - Threading + queue (overhead)
        - Input bloqueante (mais simples)

        Por enquanto usamos input() normal no Windows.
        """
        return input(prompt)


def create_non_blocking_input_with_flag(flag_checker: Callable[[], bool], flag_command: str) -> NonBlockingInput:
    def check_callback() -> Optional[str]:
        if flag_checker():
            return flag_command
        return None

    return NonBlockingInput(check_callback=check_callback)
