from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
