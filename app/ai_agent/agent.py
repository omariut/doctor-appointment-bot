from langchain_google_genai import ChatGoogleGenerativeAI
from app.ai_agent.prompts import chat_prompt
from app.ai_agent.qdrant import QdrantIngestionService
from app.ai_agent.tools import save_appointment, get_docs
from langchain_core.messages import (
    HumanMessage,
    get_buffer_string,
)
from datetime import datetime
from langsmith.run_helpers import traceable
from app.ai_agent.graphs.agent_graph import AppointmentGraph
from langgraph.checkpoint.memory import InMemorySaver


class AppointmentAgent:
    def __init__(self):
        self.gemini_2_5_flash_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        self.qdrant = QdrantIngestionService()
        self.memory = InMemorySaver()

    @traceable(name="hospital-assistant-session")
    def get_response(self, user_message: str, session_id: str):
        graph = AppointmentGraph(self.gemini_2_5_flash_llm, self.qdrant).build_graph(
            self.memory
        )
        user_message = HumanMessage(content=user_message)
        result = graph.invoke(
            {
                "messages": [user_message],
                "session_id": session_id,
            },
            config={"configurable": {"thread_id": session_id}},
        )
        return result.get("response", "").content
