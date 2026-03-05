import os

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="backend.env", case_sensitive=False, extra="ignore")

    # here database fields are empty, because the pydantic automatically finds it. Thats very cool :)
    db_host: str = '127.0.0.1'
    db_port: int = 5432
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    db_password: str
    db_user: str
    db_name: str
    debug: bool = os.environ.get("DEBUG")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")


    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @computed_field
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

settings = Settings()
