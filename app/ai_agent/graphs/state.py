from typing import Annotated, List, Any, Optional
from langgraph.graph import MessagesState
from datetime import datetime


class AgentState(MessagesState):
    user_message: str
    response: Optional[Any]
