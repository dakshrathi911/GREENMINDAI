from fastapi import FastAPI

app = FastAPI(title="GreenMind AI")


@app.get("/")
def home():
    return {
        "message": "GreenMind AI backend is running!",
        "status": "online"
    }