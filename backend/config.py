from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    tavily_api_key: str = ""
    unipile_api_key: str = ""
    unipile_account_id: str = ""
    unipile_dsn: str = ""
    resend_api_key: str = ""
    resend_from_email: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    pioneer_api_key: str = ""
    pioneer_model_id: str = ""
    fal_key: str = ""
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/huntagent"
    sync_database_url: str = ""


settings = Settings()
