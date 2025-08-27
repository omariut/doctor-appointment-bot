from app.ai_agent import AppointmentAgent
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.appointment_agent = AppointmentAgent()
    yield


app = FastAPI(lifespan=lifespan)