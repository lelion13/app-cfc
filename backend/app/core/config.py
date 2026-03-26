from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    jwt_secret: str
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    # Secreto para POST /auth/bootstrap (primer Admin). Debe ser largo; en producción obligatorio si no hay usuarios.
    setup_token: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [v.strip() for v in self.cors_origins.split(",") if v.strip()]


settings = Settings()  # type: ignore[call-arg]
