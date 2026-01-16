from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    WEATHER_API_KEY: str = ""
    API_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"


settings = Settings()
