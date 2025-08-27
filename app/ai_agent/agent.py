# simple prompt using langchain
from dotenv import load_dotenv

load_dotenv()  # loads from .env

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .prompts import PROMPT
from .context import CONTEXT
from .qdrant import QdrantIngestionService


class AppointmentAgent:
    def __init__(self):
        self.gemini_2_5_flash_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        self.qdrant = QdrantIngestionService()

    def get_response(self, user_message: str):
        docs = self.get_docs(user_message)
        context = "\n".join([doc.page_content for doc in docs])
        prompt = PROMPT.format(user_message=user_message, context=context)
        return self.gemini_2_5_flash_llm.invoke(prompt).content

    def get_docs(self, user_message: str):
        results = self.qdrant.search(user_message)
        return results
