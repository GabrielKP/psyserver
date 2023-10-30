import argparse
import tomllib
from functools import lru_cache
from pathlib import Path

import uvicorn
from pydantic_settings import BaseSettings

DEFAULT_CONFIG_NAME = "psyserver.toml"


class Settings(BaseSettings):
    experiments_dir: str = "experiments"
    data_dir: str = "data"


def main():
    parser = argparse.ArgumentParser(
        prog="psyserver",
        description=("A server for hosting online experiments."),
    )
    subparsers = parser.add_subparsers(
        title="commands",
        required=True,
    )

    # run command
    parser_run = subparsers.add_parser("run", help="run the server")
    parser_run.add_argument(
        "--config",
        type=str,
        default=None,
        help="path to a configuration file.",
    )
    parser_run.set_defaults(func=run)

    # config command
    parser_config = subparsers.add_parser(
        "config", help="create an example configuration file"
    )
    parser_config.add_argument(
        "--config",
        type=str,
        default=None,
        help="path for configuration file.",
    )
    parser_config.set_defaults(func=save_example_config)

    # parse arguments
    args = parser.parse_args()

    # run command
    args.func(config_path=args.config)


def default_config_path():
    return Path.cwd() / DEFAULT_CONFIG_NAME


@lru_cache()
def get_settings_toml(config_path: str | None = None):
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


def save_example_config(config_path: str | None = None):
    """Returns an example configuration into the given path.

    Parameters
    ----------
    config_path : str | None, default = `None`
        Path to a configuration file. If `None`, then configuration in
        the current directory is used.
    """

    if config_path is None:
        config_path = default_config_path()

    example_config_str = """title = "psyserver config"

[psyserver]
experiments_dir = "experiments"
data_dir = "data"

[uvicorn]
host = "127.0.0.1"
port = 5000
log_level = "info"
"""

    if config_path is None:
        config_path = default_config_path()
    with open(config_path, "w") as configfile:
        configfile.write(example_config_str)
    print(f"Saved example configuration to {config_path}")

    return 0


def run(config_path: str | None = None):
    """Runs the server given config.

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

    uvicorn_config = uvicorn.Config("psyserver.main:app", **config["uvicorn"])
    server = uvicorn.Server(uvicorn_config)
    server.run()
