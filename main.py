from fastapi import FastAPI, Form, Request, Response, Depends
from fastapi.responses import HTMLResponse
import uvicorn
from app.ai_agent.qdrant import QdrantIngestionService
from dotenv import load_dotenv
from typing import List
from app.ai_agent.agent import AppointmentAgent
import uuid

load_dotenv()  # loads from .env
from app import app


async def get_session_id(request: Request):
    # check if session already has an id
    if "session_id" not in request.session:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id

    return request.session["session_id"]


@app.get("/", response_class=HTMLResponse)
def index():
    return open("static/chat.html", "r", encoding="utf-8").read()


@app.post("/api/chat", response_class=HTMLResponse)
async def chat_endpoint(
    request: Request,
    message: str = Form(...),
    session_id: str = Depends(get_session_id),
):
    agent: AppointmentAgent = app.state.appointment_agent
    # bot logic
    reply_text = agent.get_response(message, session_id)
    bot_html = f'<div class="bot msg">{reply_text}</div>'

    # Return both messages so they append to chat
    return HTMLResponse(bot_html)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
