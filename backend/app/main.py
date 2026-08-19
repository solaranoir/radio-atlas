# backend/app/main.py

from fastapi import FastAPI

from app.logging.logger import configure_logging

configure_logging()

app = FastAPI(
    title="SolaraSphere: Radio Atlas API",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
