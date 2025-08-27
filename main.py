from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def index():
    return open("static/chat.html", "r", encoding="utf-8").read()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
