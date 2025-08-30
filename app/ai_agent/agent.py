from langchain_google_genai import ChatGoogleGenerativeAI
from app.ai_agent.prompts import chat_prompt
from app.ai_agent.qdrant import QdrantIngestionService
from app.ai_agent.tools import save_appointment
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

    @traceable(name="hospital-assistant-session")
    def get_response(self, user_message: str, session_id: str):
        docs = self.get_docs(user_message)

        doctors_text = "\n".join([doc.page_content for doc in docs])
        llm_with_tools = self.gemini_2_5_flash_llm.bind_tools([save_appointment])
        chain = chat_prompt | llm_with_tools
        messages = [HumanMessage(content=user_message)]
        # add chat history to messages
        chat_history = self.chat_history.get(session_id)

        response = chain.invoke(
            {
                "doctors": doctors_text,
                "user_message": messages,
                "today": datetime.now().strftime("%Y-%m-%d"),
                "chat_history": chat_history,
            }
        )

        if response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                selected_tool = {"save_appointment": save_appointment}[
                    tool_call["name"].lower()
                ]
                tool_msg = selected_tool.invoke(tool_call)
                messages.append(tool_msg)

            response = llm_with_tools.invoke(get_buffer_string(messages))
        self.chat_history.extend(session_id, [messages[0], response])
        return response.content

    def get_docs(self, user_message: str):
        results = self.qdrant.search(user_message)
        return results
