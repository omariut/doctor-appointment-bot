from app.ai_agent import AppointmentAgent
from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
import os

from dotenv import load_dotenv

load_dotenv()  # loads from .env


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.appointment_agent = AppointmentAgent()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
