# config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./coffetime.db")

    # Server
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")

    # Domain settings - добавьте значения по умолчанию
    domain: str = os.getenv("DOMAIN", "localhost")
    www_domain: str = os.getenv("WWW_DOMAIN", "www.localhost")
    email: str = os.getenv("EMAIL", "admin@localhost")

    # Files
    upload_path: str = os.getenv("UPLOAD_PATH", "./app/coffeeshop/static/images")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "5242880"))

    # Redis (for cart storage)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    cart_ttl: int = int(os.getenv("CART_TTL", "86400"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "info")

    class Config:
        env_file = ".env"


settings = Settings()
