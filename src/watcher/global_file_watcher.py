import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, Set
from threading import Timer

class GlobalDebouncedFileWatcher(FileSystemEventHandler):
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx',
        '.html', '.css', '.scss', '.sass',
        '.java', '.kt', '.go', '.php',
        '.c', '.cpp', '.cc', '.h', '.hpp',
        '.swift', '.m', '.dart',
        '.rb', '.sh', '.sql'
    }

    IGNORED_DIRS = {
        'node_modules',
        'venv', '.venv', 'env', '.env',
        '__pycache__', '.pytest_cache',
        '.git', '.svn', '.hg',
        'dist', 'build', 'target',
        '.idea', '.vscode',
        'coverage', '.coverage',
        '.next', '.nuxt',
        'vendor',
    }

    def __init__(self, callback: Callable, debounce_seconds: float = 3.0, quiet_mode: bool = False):
        """
        Inicializa o watcher de arquivos com debounce.

        CONCEITO - DEBOUNCE:
        O debounce evita que a análise seja disparada múltiplas vezes
        quando o editor salva várias vezes em sequência. Ele espera
        X segundos após a última modificação antes de disparar.

        Args:
            callback: Função async a ser chamada quando detectar mudanças
            debounce_seconds: Tempo de espera após última mudança (padrão: 3s)
            quiet_mode: Se True, suprime logs detalhados
        """
        super().__init__()
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.quiet_mode = quiet_mode

        self.global_timer: Timer | None = None
        self.modified_files: Set[str] = set()
        self.last_modified: dict[str, float] = {}

    def _log(self, message: str, level: str = "info"):
        """Log condicional baseado em quiet_mode.

        Args:
            message: Mensagem a ser exibida
            level: Nível do log ("info", "debug", "error")
        """
        if level == "error":
            print(message)
        elif not self.quiet_mode:
            if level != "debug":
                print(message)

    def should_process_file(self, file_path: str) -> bool:
        path = Path(file_path)

        if path.suffix not in self.SUPPORTED_EXTENSIONS:
            return False

        parts = path.parts
        if any(ignored_dir in parts for ignored_dir in self.IGNORED_DIRS):
            return False

        current_time = time.time()
        last_mod = self.last_modified.get(file_path, 0)

        if current_time - last_mod < 1:
            return False

        self.last_modified[file_path] = current_time
        return True

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        if not self.should_process_file(file_path):
            return

        filename = Path(file_path).name
        if not self.modified_files:
            print(f"\n📝 Arquivo modificado: {filename}")
            print(f"   ⏳ Aguardando {self.debounce_seconds}s para analisar...")

        self.modified_files.add(file_path)
        self._log(f"Arquivo modificado: {file_path}", level="debug")

        if self.global_timer is not None:
            self.global_timer.cancel()

        self.global_timer = Timer(
            self.debounce_seconds,
            self._execute_callback
        )
        self.global_timer.daemon = True
        self.global_timer.start()

    def _execute_callback(self):
        """Executa o callback após o período de debounce.

        Este método é chamado pelo Timer e não recebe argumentos.
        Processa todas as mudanças acumuladas em self.modified_files.
        """
        self.global_timer = None

        try:
            self.callback()
        except Exception as e:
            self._log(f"❌ Erro ao processar mudanças: {e}", level="error")
        finally:
            self.modified_files.clear()


class FileWatcherManager:
    def __init__(self, repo_path: str, callback: Callable, quiet_mode: bool = False):
        self.repo_path = Path(repo_path)
        self.callback = callback
        self.quiet_mode = quiet_mode
        self.observer = None
        self.event_handler = None

    def start(self):
        self.event_handler = GlobalDebouncedFileWatcher(
            self.callback,
            quiet_mode=self.quiet_mode
        )
        self.observer = Observer()

        self.observer.schedule(
            self.event_handler,
            str(self.repo_path),
            recursive=True
        )

        self.observer.start()
        if not self.quiet_mode:
            print(f"Monitorando mudanças em: {self.repo_path}")

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            if not self.quiet_mode:
                print("File watcher parado!")

    def is_running(self) -> bool:
        return self.observer is not None and self.observer.is_alive()