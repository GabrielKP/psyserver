import tomllib
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


DEFAULT_CONFIG_NAME = "psyserver.toml"


class Settings(BaseSettings):
    studies_dir: str = "studies"
    data_dir: str = "data"
    redirect_url: str | None = "https://www.example.com"


def default_config_path() -> Path:
    return Path.cwd() / DEFAULT_CONFIG_NAME


@lru_cache()
def get_settings_toml(config_path: str | Path | None = None):
    """Returns the settings from the given config.

    Parameters
    ----------
    config_path : str | None, default = `None`
        Path to a configuration file. If `None`, then configuration in
        the current directory is used.
    """

    if config_path is None:
        config_path = default_config_path()
    with open(config_path, "rb") as configfile:
        config = tomllib.load(configfile)

    return Settings(**config["psyserver"])
