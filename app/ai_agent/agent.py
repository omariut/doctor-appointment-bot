# simple prompt using langchain
from dotenv import load_dotenv
load_dotenv()  # loads from .env

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


class AppointmentAgent:
    def __init__(self):
        self.gemini_2_5_flash_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    