import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class UsageTracker:
    USAGE_DIR = Path.home() / ".config" / "gitcast"
    USAGE_FILE = USAGE_DIR / "usage.json"

    DEFAULT_USAGE = {
        "first_use": None,
        "total_commits": 0,
        "commands": {}
    }

    def __init__(self):
        self.USAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.usage = self._load()

        if self.usage["first_use"] is None:
            self.usage["first_use"] = datetime.now().isoformat()
            self._save()

    def _load(self) -> Dict[str, Any]:
        if self.USAGE_FILE.exists():
            try:
                with open(self.USAGE_FILE, "r", encoding="utf-8") as f:
                    user_usage = json.load(f)
                    usage = self.DEFAULT_USAGE.copy()
                    usage.update(user_usage)
                    if not isinstance(usage["commands"], dict):
                        usage["commands"] = {}
                    return usage
            except (json.JSONDecodeError, KeyError):
                return self.DEFAULT_USAGE.copy()
        return self.DEFAULT_USAGE.copy()

    def _save(self) -> None:
        with open(self.USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.usage, f, indent=4, ensure_ascii=False)

    def increment_command(self, command: str) -> None:
        commands = self.usage["commands"]
        commands[command] = commands.get(command, 0) + 1
        self._save()

    def increment_commits(self, count: int = 1) -> None:
        self.usage["total_commits"] += count
        self._save()

    def get_stats(self) -> Dict[str, Any]:
        first_use = None
        days_using = 0
        avg_commits_per_day = 0.0

        if self.usage["first_use"]:
            first_use = datetime.fromisoformat(self.usage["first_use"])
            days_using = max(1, (datetime.now() - first_use).days)
            avg_commits_per_day = self.usage["total_commits"] / days_using

        total_commands = sum(self.usage["commands"].values())

        return {
            "first_use": first_use,
            "days_using": days_using,
            "total_commits": self.usage["total_commits"],
            "avg_commits_per_day": round(avg_commits_per_day, 1),
            "commands": self.usage["commands"].copy(),
            "total_commands": total_commands
        }

    def display_stats(self) -> str:
        stats = self.get_stats()

        lines = [
            "",
            "═" * 60,
            "📊 ESTATÍSTICAS DE USO - GITCAST",
            "═" * 60,
        ]

        if stats["first_use"]:
            first_use_str = stats["first_use"].strftime("%d/%m/%Y")
            lines.append(f"📅 Primeiro uso: {first_use_str}")
            lines.append(f"📆 Dias de uso: {stats['days_using']} dia(s)")
        else:
            lines.append("📅 Primeiro uso: Hoje!")

        lines.append("")

        lines.append("🔥 COMMITS")
        lines.append(f"   Total: {stats['total_commits']}")
        lines.append(f"   Média por dia: {stats['avg_commits_per_day']}")
        lines.append("")

        lines.append("📋 COMANDOS USADOS")

        if stats["commands"]:
            sorted_commands = sorted(
                stats["commands"].items(),
                key=lambda x: x[1],
                reverse=True
            )

            max_usage = max(stats["commands"].values()) if stats["commands"] else 1
            bar_width = 20

            for cmd, count in sorted_commands:
                bar_length = int((count / max_usage) * bar_width)
                bar = "█" * bar_length + "░" * (bar_width - bar_length)

                lines.append(f"   {cmd:<12} {bar} {count}x")
        else:
            lines.append("   Nenhum comando usado ainda.")

        lines.append("")
        lines.append(f"   Total de comandos: {stats['total_commands']}")
        lines.append("═" * 60)
        lines.append("")

        return "\n".join(lines)
