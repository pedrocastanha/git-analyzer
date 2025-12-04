import platform
import subprocess
import threading
import tempfile
import os
from pathlib import Path


class NotificationManager:
    def __init__(self, app_name: str = "GitCast", default_timeout: int = 3000):
        self.app_name = app_name
        self.system = platform.system()
        self.on_click_callback = None
        self.default_timeout = default_timeout

    def send(self,
             title: str,
             message: str,
            timeout: int = None,
            urgency: str = "normal"
    ) -> bool:
        if timeout is None:
            timeout = self.default_timeout
        try:
            if self.system == "Linux":
                return self._send_linux(title, message, timeout, urgency)
            elif self.system == "Darwin":
                return self._send_macos(title, message)
            elif self.system == "Windows":
                return self._send_windows(title, message, timeout)
            else:
                print(f"Sistema operacional '{self.system}' não suportado para notificações.")
                return False
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")
            return False

    def _send_linux(self, title:str, message: str, timeout: int, urgency: str) -> bool:
        timeout_ms = timeout

        cmd = [
            "notify-send",
            title,
            message,
            f"--app-name={self.app_name}",
            f"--urgency={urgency}",
            f"--expire-time={timeout_ms}",
            "--icon=dialog-information",
            "--category=dev.tools"
        ]

        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0

    def _send_macos(self, title: str, message: str) -> bool:
        message = message.replace('"', '\\"')
        title = title.replace('"', '\\"')

        script = f'''
        display notification "{message}" with title "{title}" subtitle "{self.app_name}"
        '''

        cmd = ["osascript", "-e", script]
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0

    def _send_windows(self, title: str, message: str, timeout: int) -> bool:
        try:
            from winotify import Notification, audio

            toast = Notification(
                app_id=self.app_name,
                title=title,
                msg=message,
                duration="short" if timeout < 5 else "long"
            )

            toast.set_audio(audio.Default, loop=False)

            toast.show()
            return True

        except ImportError:
            return self._send_windows_powershell(title, message)

    def _send_windows_powershell(self, title: str, message: str) -> bool:
        message = message.replace("'", "''")
        title = title.replace("'", "''")

        ps_script = f"""
             [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
             [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

             $template = @"
             <toast>
                 <visual>
                     <binding template="ToastText02">
                         <text id="1">{title}</text>
                         <text id="2">{message}</text>
                     </binding>
                 </visual>
             </toast>
        "@
             $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
             $xml.LoadXml($template)
             $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
             [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{self.app_name}').Show($toast)
             """

        cmd = ["powershell", "-Command", ps_script]
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0

    def send_with_action(
            self,
            title: str,
            message: str,
            on_click_callback=None,
            timeout: int = None
    ):
        self.on_click_callback = on_click_callback

        # Usa timeout configurado se não especificado
        if timeout is None:
            timeout = self.default_timeout

        if self.system == "Linux":
            self._send_linux_with_action(title, message, timeout)
        else:
            self.send(
                title=title,
                message=f"{message}\n\n💡 Digite 'suggestions' no terminal",
                timeout=timeout,
                urgency="normal"  # Mudou de critical para normal
            )

        print("\n" + "=" * 80)
        print(f"🔔 NOTIFICAÇÃO: {title}")
        print(f"   {message}")
        print(f"   💡 Digite 'suggestions' ou clique na notificação")
        print("=" * 80 + "\n")

    def _send_linux_with_action(self, title: str, message: str, timeout: int):
        action_result = self._try_notify_with_action(title, message, timeout)

        if action_result:
            return

        zenity_result = self._try_zenity_notification(title, message)

        if zenity_result:
            return

        self._send_simple_notification(title, message, timeout)

    def _try_notify_with_action(self, title: str, message: str, timeout: int) -> bool:
        try:
            def send_and_wait():
                try:
                    result = subprocess.run(
                        [
                            "notify-send",
                            title,
                            message,
                            f"--app-name={self.app_name}",
                            "--urgency=normal",  # Mudou de critical para normal
                            "--icon=dialog-information",
                            f"--expire-time={timeout}",  # ADICIONAR expire time
                            "-A", "show=💡 Ver Sugestões",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=300,
                    )

                    if "show" in result.stdout.strip():
                        if self.on_click_callback:
                            self.on_click_callback()

                except (subprocess.TimeoutExpired, Exception):
                    pass

            test = subprocess.run(
                ["notify-send", "--help"],
                capture_output=True,
                text=True,
                timeout=1,
            )

            if "--action" not in test.stdout:
                return False

            thread = threading.Thread(target=send_and_wait, daemon=True)
            thread.start()

            return True

        except Exception:
            return False

    def _try_zenity_notification(self, title: str, message: str) -> bool:
        try:
            result = subprocess.run(
                ["which", "zenity"], capture_output=True, timeout=1
            )

            if result.returncode != 0:
                return False

            script_file = Path(tempfile.gettempdir()) / "gitcast_click.sh"
            signal_file = Path(tempfile.gettempdir()) / "gitcast_notification_click"

            script_file.write_text(
                f"""#!/bin/bash
                touch "{signal_file}"
                """
            )
            script_file.chmod(0o755)

            def show_zenity():
                try:
                    subprocess.run(
                        [
                            "zenity",
                            "--notification",
                            f"--text={title}: {message}\n\nClique para ver sugestões",
                            f"--icon=dialog-information",
                        ],
                        timeout=300,
                    )
                except Exception:
                    pass

            if self.on_click_callback:
                monitor_thread = threading.Thread(
                    target=self._monitor_notification_click,
                    args=(signal_file,),
                    daemon=True,
                )
                monitor_thread.start()

            threading.Thread(target=show_zenity, daemon=True).start()

            return True

        except Exception:
            return False

    def _send_simple_notification(self, title: str, message: str, timeout: int):
        cmd = [
            "notify-send",
            title,
            f"{message}\n\n💡 Digite 'suggestions' no terminal",
            f"--app-name={self.app_name}",
            "--urgency=normal",  # Mudou de critical para normal
            f"--expire-time={timeout}",  # Usa timeout configurável
            "--icon=dialog-information",
            "--category=dev.tools",
        ]

        subprocess.run(cmd, capture_output=True)

    def _monitor_notification_click(self, signal_file: Path):
        import time

        for _ in range(300):
            if signal_file.exists():
                if self.on_click_callback:
                    try:
                        self.on_click_callback()
                    except Exception as e:
                        print(f"Erro ao executar callback: {e}")

                signal_file.unlink()
                break

            time.sleep(1)

    def _try_focus_terminal(self):
        if self.system != "Linux":
            return

        try:
            result = subprocess.run(
                ["which", "xdotool"],
                capture_output=True,
                timeout=1
            )

            if result.returncode != 0:
                return

            ppid = os.getppid()

            subprocess.run(
                ["xdotool", "search", "--pid", str(ppid), "windowactivate"],
                capture_output=True,
                timeout=1
            )

        except Exception:
            pass


