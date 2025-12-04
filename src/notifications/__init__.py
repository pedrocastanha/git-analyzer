"""Notifications Package - Sistema de notificacoes e sugestoes da IA"""

from .notification_manager import NotificationManager
from .suggestion_builder import SuggestionBuilder, Suggestion, SuggestionType
from .interactive_menu import InteractiveMenu
from .action_executor import ActionExecutor

__all__ = [
    "NotificationManager",
    "SuggestionBuilder",
    "Suggestion",
    "SuggestionType",
    "InteractiveMenu",
    "ActionExecutor",
]
