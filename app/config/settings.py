# app/config/settings.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Alhawy AI Core"
    VERSION: str = "0.2.0"
    ENVIRONMENT: str = "development"

    # Telegram
    BOT_TOKEN: str

    # Gemini
    GEMINI_API_KEY: str = ""

    # Binance
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    BINANCE_TESTNET: bool = True  # استخدم Testnet للاختبار

    # Trading Settings
    DEFAULT_TRADE_AMOUNT: float = 100.0
    DEFAULT_RISK_PERCENT: float = 2.0
    DEFAULT_TAKE_PROFIT: float = 2.5
    DEFAULT_STOP_LOSS: float = 1.2
    MAX_ACTIVE_TRADES: int = 5

    # Scheduler
    SCAN_INTERVAL_MINUTES: int = 5

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
