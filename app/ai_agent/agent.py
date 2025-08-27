# simple prompt using langchain
from dotenv import load_dotenv
load_dotenv()  # loads from .env

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .prompts import PROMPT
from .context import CONTEXT

class AppointmentAgent:
    def __init__(self):
        self.gemini_2_5_flash_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    
    def get_response(self, user_message: str):
        prompt = PROMPT.format(user_message=user_message, **CONTEXT)
        return self.gemini_2_5_flash_llm.invoke(prompt).content