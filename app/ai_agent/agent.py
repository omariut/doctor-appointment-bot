# simple prompt using langchain
from dotenv import load_dotenv

load_dotenv()  # loads from .env

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.ai_agent.prompts import PROMPT, chat_prompt
from app.ai_agent.context import CONTEXT
from app.ai_agent.qdrant import QdrantIngestionService
from app.ai_agent.tools import save_appointment
from langchain_core.output_parsers import PydanticToolsParser
from langchain_core.messages import HumanMessage, ToolMessage
from datetime import datetime
from langchain_core.tracers.context import collect_runs
from langsmith.run_helpers import traceable


class AppointmentAgent:
    def __init__(self):
        self.gemini_2_5_flash_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        self.qdrant = QdrantIngestionService()

    @traceable(name="hospital-assistant-session")
    def get_response(self, user_message: str):
        docs = self.get_docs(user_message)

        doctors_text = "\n".join([doc.page_content for doc in docs])
        llm_with_tools = self.gemini_2_5_flash_llm.bind_tools([save_appointment])
        chain = chat_prompt | llm_with_tools
        messages = [HumanMessage(content=user_message)]

        response = chain.invoke(
            {
                "doctors": doctors_text,
                "user_message": messages,
                "today": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        messages.append(response)
        if response.tool_calls:
            for tool_call in response.tool_calls:
                selected_tool = {"save_appointment": save_appointment}[
                    tool_call["name"].lower()
                ]
                tool_msg = selected_tool.invoke(tool_call)
                messages.append(tool_msg)

            followup = llm_with_tools.invoke(messages)
            return followup.content
        return response.content

    def get_docs(self, user_message: str):
        results = self.qdrant.search(user_message)
        return results
