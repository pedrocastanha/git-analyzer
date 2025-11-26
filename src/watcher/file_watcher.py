import time
import asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from typing import Callable, Set
from threading import Timer


class DebouncedFileWatcher(FileSystemEventHandler):
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

    def __init__(self, callback: Callable, debounce_seconds: float = 5.0):
        """ Inicializa o watcher.
         Args:
         callback: Função a ser chamada quando arquivo mudar Recebe como parâmetro: file_path (str)
         debounce_seconds: Tempo de espera após última mudança (padrão: 3s)
         """
        super().__init__()
        self.callback = callback
        self.debounce_seconds = debounce_seconds

        self.timers: dict[str, Timer] = {}
        self.last_modified: dict[str, float] = {}

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

        if file_path in self.timers:
            self.timers[file_path].cancel()

        timer = Timer(
            self.debounce_seconds,
            self._execute_callback,
            args=[file_path]
        )
        timer.daemon = True
        timer.start()

        self.timers[file_path] = timer

    def _execute_callback(self, file_path: str):
        if file_path in self.timers:
            del self.timers[file_path]

        try:
            self.callback(file_path)
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")

class FileWatcherManager:
    def __init__(self, repo_path: str, callback: Callable ):
        self.repo_path = Path(repo_path)
        self.callback = callback
        self.observer = None
        self.event_handler = None

    def start(self):
        self.event_handler = DebouncedFileWatcher(self.callback)
        self.observer = Observer()

        self.observer.schedule(
            self.event_handler,
            str(self.repo_path),
            recursive=True
        )

        self.observer.start()
        print(f"Monitorando mudanças em: {self.repo_path}")

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("File watcher parado!")

    def is_running(self) -> bool:
        return self.observer is not None and self.observer.is_alive()