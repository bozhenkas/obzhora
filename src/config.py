from typing import Dict, Any, List
from pydantic import SecretStr, PostgresDsn, computed_field, model_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

VK_API_URL = "https://api.vk.com/method/"


class Settings(BaseSettings):
    bot_token: SecretStr
    vk_token: SecretStr

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str

    redis_host: str
    redis_port: int

    CURATORS: str = ""
    curators_list: List[int] = Field(default_factory=list)  # type: ignore

    @model_validator(mode='after')
    def parse_curators_list(self) -> 'Settings':
        if self.CURATORS:
            try:
                self.curators_list = [int(item.strip()) for item in self.CURATORS.split(',')]
            except (ValueError, TypeError):
                raise ValueError("CURATORS в .env файле должен быть списком чисел, разделенных запятой.")
        return self

    @computed_field
    @property
    def postgres_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    @computed_field
    @property
    def vk_default_data(self) -> Dict[str, Any]:
        return {
            "access_token": self.vk_token.get_secret_value(),
            "v": "5.131",
        }

    model_config = SettingsConfigDict(extra='ignore')


config = Settings()
