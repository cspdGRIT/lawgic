from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    # LLM — set LLM_PROVIDER to: anthropic | openai | groq | google | cohere | nvidia | ollama
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = ""          # optional override; if blank, provider default is used
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    COHERE_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    # Auth
    GOOGLE_CLIENT_ID: str = ""
    # Mobile OTP login — SMS_PROVIDER: console (dev, logs the code) | android_gateway (open-source, self-hosted)
    SMS_PROVIDER: str = "console"
    SMS_GATEWAY_URL: str = ""       # e.g. http://192.168.1.20:8080 — your android-sms-gateway instance
    SMS_GATEWAY_LOGIN: str = ""
    SMS_GATEWAY_PASSWORD: str = ""
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    OTP_MAX_ATTEMPTS: int = 5
    # Legal data
    INDIAN_KANOON_API_KEY: str = ""
    # Payments
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    SECRET_KEY: str = "change-me-in-production-must-be-at-least-32-chars-long"
    DATABASE_URL: str = "postgresql+asyncpg://lawgic:lawgic_dev_pass@localhost:5432/lawgic"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15          # short-lived access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ENVIRONMENT: str = "development"
    REDIS_URL: str = ""                            # optional: redis://localhost:6379/0
    LLM_CACHE_TTL_SECONDS: int = 3600             # cache identical LLM responses for 1 hour
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:3001", "http://localhost:5174"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
