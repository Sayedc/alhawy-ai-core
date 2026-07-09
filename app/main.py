from fastapi import FastAPI

app = FastAPI(
    title="Alhawy AI Core",
    version="0.1.0-alpha"
)

@app.get("/")
def health():
    return {
        "name": "Alhawy AI Core",
        "version": "0.1.0-alpha",
        "status": "running"
    }
