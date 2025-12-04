import select
import sys
from typing import Optional, Callable


class NonBlockingInput:
    def __init__(self, check_callback: Optional[Callable[[], Optional[str]]] = None):
        self.check_callback = check_callback
        self.is_windows = sys.platform.startswith('win')

    def get_input(self, prompt: str = "", timeout: float = 0.5) -> Optional[str]:
        if self.is_windows:
            return self._get_input_windows(prompt)

        return self._get_input_unix(prompt, timeout)

    def _get_input_unix(self, prompt: str, timeout: float) -> Optional[str]:
        print(prompt, end='', flush=True)

        while True:
            if self.check_callback:
                simulated = self.check_callback()
                if simulated is not None:
                    print(simulated)
                    return simulated

            ready, _, _ = select.select([sys.stdin], [], [], timeout)

            if ready:
                return sys.stdin.readline().strip()


    def _get_input_windows(self, prompt: str) -> str:
        return input(prompt)


def create_non_blocking_input_with_flag(flag_checker: Callable[[], bool], flag_command: str) -> NonBlockingInput:
    def check_callback() -> Optional[str]:
        if flag_checker():
            return flag_command
        return None

    return NonBlockingInput(check_callback=check_callback)
