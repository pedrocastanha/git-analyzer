import time

from langchain_core.callbacks import BaseCallbackHandler


class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"


class StreamingHandler(BaseCallbackHandler):
    def __init__(
        self,
        color: str = Colors.WHITE,
        prefix: str = "",
        show_thinking: bool = True
    ):
        self.color = color
        self.prefix = prefix
        self.show_thinking = show_thinking
        self.token_count = 0
        self.started = False

    def on_llm_start(self, *args, **kwargs):
        if self.show_thinking:
            print(f"\n{Colors.DIM}🤔 Analisando...{Colors.RESET}", end="", flush=True)

    def on_llm_new_token(self, token: str, **kwargs):
        if not self.started:
            print(f"\r{' ' * 20}\r", end="")  # Limpa linha
            if self.prefix:
                print(f"{self.prefix}", end="")
            self.started = True

        print(f"{self.color}{token}{Colors.RESET}", end="", flush=True)
        self.token_count += 1

    def on_llm_end(self, *args, **kwargs):
        print()

    def on_llm_error(self, error: Exception, **kwargs):
        print(f"\n{Colors.RED}❌ Erro: {error}{Colors.RESET}")


class ProgressIndicator:
    SPINNERS = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "bars": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"],
        "arrows": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        "pulse": ["◐", "◓", "◑", "◒"],
    }

    def __init__(self, message: str = "Processando", style: str = "dots"):
        self.message = message
        self.frames = self.SPINNERS.get(style, self.SPINNERS["dots"])
        self.current_frame = 0
        self.running = False

    def show_frame(self):
        frame = self.frames[self.current_frame % len(self.frames)]
        print(f"\r{Colors.CYAN}{frame}{Colors.RESET} {self.message}...", end="", flush=True)
        self.current_frame += 1

    def clear(self):
        print(f"\r{' ' * (len(self.message) + 10)}\r", end="", flush=True)


def print_section_header(title: str, emoji: str = "📋"):
    width = 60
    print()
    print(f"{Colors.CYAN}{'═' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{emoji} {title.upper()}{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * width}{Colors.RESET}")
    print()


def print_code_block(code: str, language: str = "", title: str = ""):
    if title:
        print(f"{Colors.DIM}┌─ {title}{Colors.RESET}")

    print(f"{Colors.DIM}│{Colors.RESET}")

    for line in code.split('\n'):
        print(f"{Colors.DIM}│{Colors.RESET} {Colors.GREEN}{line}{Colors.RESET}")

    print(f"{Colors.DIM}│{Colors.RESET}")
    print(f"{Colors.DIM}└{'─' * 40}{Colors.RESET}")


def print_diff(old_code: str, new_code: str, file_path: str = ""):
    if file_path:
        print(f"\n{Colors.CYAN}📄 {file_path}{Colors.RESET}")

    print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")

    print(f"\n{Colors.RED}{Colors.BOLD}━━━ ANTES ━━━{Colors.RESET}")
    for line in old_code.split('\n'):
        print(f"{Colors.RED}- {line}{Colors.RESET}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}━━━ DEPOIS ━━━{Colors.RESET}")
    for line in new_code.split('\n'):
        print(f"{Colors.GREEN}+ {line}{Colors.RESET}")

    print(f"\n{Colors.DIM}{'─' * 60}{Colors.RESET}")


def print_suggestion_card(
    title: str,
    description: str,
    priority: int,
    suggestion_type: str,
    file_path: str = "",
    line: int = 0
):
    if priority >= 5:
        border_color = Colors.RED
        priority_text = f"{Colors.RED}●●●●●{Colors.RESET}"
    elif priority >= 4:
        border_color = Colors.YELLOW
        priority_text = f"{Colors.YELLOW}●●●●○{Colors.RESET}"
    elif priority >= 3:
        border_color = Colors.CYAN
        priority_text = f"{Colors.CYAN}●●●○○{Colors.RESET}"
    else:
        border_color = Colors.GREEN
        priority_text = f"{Colors.GREEN}●●○○○{Colors.RESET}"

    type_emojis = {
        "commit": "💾",
        "fix_error": "🔧",
        "security": "🔒",
        "improve": "✨",
        "refactor": "♻️",
    }
    emoji = type_emojis.get(suggestion_type, "💡")

    width = 60

    print(f"{border_color}┌{'─' * width}┐{Colors.RESET}")
    print(f"{border_color}│{Colors.RESET} {emoji} {Colors.BOLD}{title[:width-15]}{Colors.RESET} {priority_text} {border_color}│{Colors.RESET}")
    print(f"{border_color}│{Colors.RESET} {Colors.DIM}{description[:width-4]}{Colors.RESET} {border_color}│{Colors.RESET}")

    if file_path:
        location = f"📄 {file_path}:{line}" if line else f"📄 {file_path}"
        print(f"{border_color}│{Colors.RESET} {Colors.CYAN}{location}{Colors.RESET} {border_color}│{Colors.RESET}")

    print(f"{border_color}└{'─' * width}┘{Colors.RESET}")


def print_analysis_stream(text: str, delay: float = 0.0):
    for char in text:
        print(f"{Colors.WHITE}{char}{Colors.RESET}", end="", flush=True)
        if delay > 0:
            time.sleep(delay)

    print()

def print_error_message(message: str):
    print(f"\n{Colors.RED}{Colors.BOLD}❌ Erro: {message}{Colors.RESET}\n")

def print_success_message(message: str):
    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Sucesso: {message}{Colors.RESET}\n")