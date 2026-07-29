from fastapi import APIRouter, Request

from app.telegram.handlers import handle_update

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(request: Request):

    update = await request.json()

    await handle_update(update)

    return {"ok": True}
