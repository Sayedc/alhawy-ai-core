from fastapi import FastAPI
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
)

logger.info("Alhawy AI Core started successfully.")
