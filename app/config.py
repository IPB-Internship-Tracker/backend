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
    password_reset_token_expire_minutes: int = 30
    password_reset_url_base: str = "http://localhost:5173/reset-password"
    algorithm: str = "HS256"
    port: int = 8000
    upload_dir: str = "uploads"
    upload_max_bytes: int = 5 * 1024 * 1024

    email_notifications_enabled: bool = False
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str = "IPB Internship & Career Tracker"
    smtp_use_tls: bool = True
    smtp_timeout_seconds: int = 10

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def database_url(self) -> str:
        password = quote_plus(self.db_pass)
        return (
            f"postgresql+psycopg://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
