from fastapi import FastAPI
from app.config import settings
from app.utils.logger import setup_logger
from app.utils.exceptions import global_exception_handler
from app.telegram.webhook import router as telegram_router

logger = setup_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
)

app.include_router(telegram_router)

# 1. إضافة معالج الاستثناءات بعد إنشاء app مباشرة
app.add_exception_handler(Exception, global_exception_handler)

logger.info("Alhawy AI Core started successfully.")

# 2. إضافة الـ Health Endpoint في آخر الملف
@app.get("/")
def health():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }
