import os
import tomllib
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

DEFAULT_CONFIG_NAME = "psyserver.toml"


class Settings(BaseSettings):
    studies_dir: str = "data/studies"
    data_dir: str = "data/studydata"
    redirect_url: str | None = None


def default_config_path() -> Path:
    return Path.cwd() / DEFAULT_CONFIG_NAME


@lru_cache()
def get_settings_toml():
    """Returns the settings from the given config."""

    config_path = default_config_path()
    with open(config_path, "rb") as configfile:
        config = tomllib.load(configfile)

    return Settings(**config["psyserver"])
