from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn
from app.ai_agent.qdrant import QdrantIngestionService
from dotenv import load_dotenv
from typing import List
from app.ai_agent.agent import AppointmentAgent

load_dotenv()  # loads from .env
from app import app


@app.get("/", response_class=HTMLResponse)
def index():
    return open("static/chat.html", "r", encoding="utf-8").read()


@app.post("/api/chat", response_class=HTMLResponse)
async def chat_endpoint(message: str = Form(...)):
    # Echo the user message
    user_html = f'<div class="user msg">{message}</div>'
    agent: AppointmentAgent = app.state.appointment_agent

    # bot logic
    reply_text = agent.get_response(message)
    bot_html = f'<div class="bot msg">{reply_text}</div>'

    # Return both messages so they append to chat
    return HTMLResponse(bot_html)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
