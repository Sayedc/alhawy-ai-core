from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    return {
        "status": "ok",
        "data": data
    }
