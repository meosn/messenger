from fastapi import FastAPI

from .routes.socket import router


app = FastAPI()
app.include_router(router)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "WebSocket server is running"
    }
