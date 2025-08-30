from langchain_core.messages.base import BaseMessage
from typing import List
from langchain_core.messages import get_buffer_string


class SessionChatHistory:
    """
    Session-based chat history manager.
    Stores chat history per session_id (e.g., user_id or session token).
    For production, replace with persistent storage.
    """

    def __init__(self):
        self._sessions = {}

    def extend(self, session_id: str, messages: List[BaseMessage]):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].extend(messages)

    def get(self, session_id: str) -> List[BaseMessage]:
        history = get_buffer_string(self._sessions.get(session_id, []))
        return history

    def clear(self, session_id: str):
        if session_id in self._sessions:
            self._sessions[session_id] = []
