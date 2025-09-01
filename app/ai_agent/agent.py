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
from app.ai_agent.history_manager import SessionChatHistory


class AppointmentAgent:
    def __init__(self):
        self.gemini_2_5_flash_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        self.qdrant = QdrantIngestionService()
        self.chat_history = SessionChatHistory()
        self.session_doctors = {}  # session_id → last retrieved doctors

    @traceable(name="hospital-assistant-session")
    def get_response(self, user_message: str, session_id: str):
        # Bind both tools
        llm = self.gemini_2_5_flash_llm
        llm_with_tools = llm.bind_tools([save_appointment, get_docs])
        chain = chat_prompt | llm_with_tools

        # Load chat + doctors memory
        chat_history = self.chat_history.get(session_id)
        doctors_context = self.session_doctors.get(session_id, "")

        messages = [HumanMessage(content=user_message)]

        # Run model with whatever doctor info we already know with tools
        response = chain.invoke(
            {
                "doctors": doctors_context,
                "user_message": user_message,
                "today": datetime.now().strftime("%Y-%m-%d"),
                "chat_history": chat_history,
            }
        )

        # Handle tool calls
        if response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                tool_map = {
                    "save_appointment": save_appointment,
                    "get_docs": get_docs,
                }
                selected_tool = tool_map[tool_call["name"].lower()]
                tool_msg = selected_tool.invoke(tool_call)
                messages.append(tool_msg)

                if tool_call["name"].lower() == "get_docs":
                    doctors_context = tool_msg.content
                    self.session_doctors[session_id] = doctors_context

            # Re-run model with updated doctor info with tools
            chain = chat_prompt | llm
            response = chain.invoke(
                {
                    "doctors": doctors_context,
                    "user_message": get_buffer_string(messages),
                    "today": datetime.now().strftime("%Y-%m-%d"),
                    "chat_history": chat_history,
                }
            )

        # Save chat history
        self.chat_history.extend(session_id, [messages[0], response])
        return response.content
