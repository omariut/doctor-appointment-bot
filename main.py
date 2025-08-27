from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def index():
    return open("static/chat.html", "r", encoding="utf-8").read()

@app.post("/api/chat", response_class=HTMLResponse)
async def chat_endpoint( message: str = Form(...)):
    # Echo the user message
    user_html = f'<div class="user msg">{message}</div>'
    
    # bot logic
    reply_text = "Hello! Tell me doctor's name and I will help you to book an appointment."
    bot_html = f'<div class="bot msg">{reply_text}</div>'
    
    # Return both messages so they append to chat
    return HTMLResponse(user_html + bot_html)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
