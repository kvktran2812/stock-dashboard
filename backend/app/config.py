from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Stock Monitor API"
    VERSION: str = "1.0.0"
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./stock_monitor.db"

    class Config:
        env_file = ".env"  # optional if you want to move DB URL to .env later

settings = Settings()