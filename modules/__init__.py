"""
jirgram modules package
Contains all modular components for the Telegram client
"""

__version__ = "1.0.0"
__author__ = "jirgram team"

# Import main modules for easier access
from .database import MessageDatabase
from .ghost_mode import GhostModeHandler
from .anti_delete import AntiDeleteHandler
from .message_history import MessageHistoryHandler

__all__ = [
    'MessageDatabase',
    'GhostModeHandler',
    'AntiDeleteHandler',
    'MessageHistoryHandler',
]
