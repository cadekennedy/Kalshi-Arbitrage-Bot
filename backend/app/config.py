from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kalshi_api_key: str = ""
    kalshi_private_key_path: str = ""
    trading_mode: str = "paper"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
