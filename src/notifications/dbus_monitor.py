import subprocess
import threading
import time
from typing import Callable, Optional


class DBusNotificationMonitor:
    def __init__(self):
        self.monitors = {}
        self.monitor_process: Optional[subprocess.Popen] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False

    def start_monitoring(self):
        if self.running:
            return

        self.running = True

        try:
            self.monitor_process = subprocess.Popen(
                [
                    "gdbus",
                    "monitor",
                    "--session",
                    "--dest",
                    "org.freedesktop.Notifications",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )

            self.monitor_thread = threading.Thread(
                target=self._process_events, daemon=True
            )
            self.monitor_thread.start()

        except FileNotFoundError:
            self.running = False

    def _process_events(self):
        if not self.monitor_process or not self.monitor_process.stdout:
            return

        for line in self.monitor_process.stdout:
            if not self.running:
                break

            if "ActionInvoked" in line:
                try:
                    next_line = next(self.monitor_process.stdout, "")
                    if "uint32" in next_line:
                        parts = next_line.strip().split()
                        if len(parts) >= 2:
                            notif_id = int(parts[1].rstrip(","))

                            if notif_id in self.monitors:
                                callback = self.monitors[notif_id]
                                try:
                                    callback()
                                except Exception as e:
                                    print(f"Erro ao executar callback: {e}")


                except (StopIteration, ValueError):
                    continue

    def register_callback(self, notification_id: int, callback: Callable):
        self.monitors[notification_id] = callback

        if not self.running:
            self.start_monitoring()

        def remove_after_timeout():
            time.sleep(300)
            if notification_id in self.monitors:
                del self.monitors[notification_id]

        threading.Thread(target=remove_after_timeout, daemon=True).start()

    def stop_monitoring(self):
        self.running = False

        if self.monitor_process:
            self.monitor_process.terminate()
            self.monitor_process.wait(timeout=1)

    def __del__(self):
        self.stop_monitoring()


_global_monitor = DBusNotificationMonitor()


def get_monitor() -> DBusNotificationMonitor:
    return _global_monitor
