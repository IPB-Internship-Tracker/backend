from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IPB Internship & Career Tracker"

    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str

    secret_key: str
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    port: int = 8000

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def database_url(self) -> str:
        password = quote_plus(self.db_pass)
        return (
            f"postgresql+psycopg://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
