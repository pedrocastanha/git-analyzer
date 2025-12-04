from pathlib import Path
from typing import Callable
from watchdog.observers import Observer
from src.watcher.global_file_watcher import GlobalDebouncedFileWatcher


class FileWatcherManager:
    def __init__(self, repo_path: str, callback: Callable, quiet_mode: bool = False):
        self.repo_path = Path(repo_path)
        self.callback = callback
        self.quiet_mode = quiet_mode
        self.observer = None
        self.event_handler = None

    def start(self):
        self.event_handler = GlobalDebouncedFileWatcher(
            callback=self.callback,
            debounce_seconds=5.0,
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
            print(f"Debounce configurado para {self.event_handler.debounce_seconds}s")

    def stop(self):
        if self.observer:
            if self.event_handler and self.event_handler.global_timer:
                self.event_handler.global_timer.cancel()

            self.observer.stop()
            self.observer.join()
            if not self.quiet_mode:
                print("File watcher parado!")