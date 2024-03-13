from pydantic import PostgresDsn, Field, FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from typing import Tuple, Type


class Config(BaseSettings):
    postgres_dsn: PostgresDsn = Field(
        default='postgresql://user:pass@localhost:5432/foobar',
        env='POSTGRES_DSN',
        alias='POSTGRES_DSN'
    )

    default_comment_types_config_path: FilePath = Field(
        default='default-comment-types.json',
        env='DEFAULT_COMMENT_TYPES_CONFIG_PATH',
        alias='DEFAULT_COMMENT_TYPES_CONFIG_PATH'
    )

    storage_path: str = Field(
        default='storage/',
        env='STORAGE_PATH',
        alias='STORAGE_PATH'
    )

    model_config = SettingsConfigDict(env_file=".env")

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return dotenv_settings, env_settings, init_settings


def load_config() -> Config:
    return Config()
