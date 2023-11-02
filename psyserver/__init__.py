import argparse
import shutil
import tomllib
from functools import lru_cache
from pathlib import Path

import uvicorn
from pydantic_settings import BaseSettings

DEFAULT_CONFIG_NAME = "psyserver.toml"


__version__ = "0.1.1"


class Settings(BaseSettings):
    studies_dir: str = "studies"
    data_dir: str = "data"
    redirect_url: str = "https://www.example.com"


def main():
    parser = argparse.ArgumentParser(
        prog="psyserver",
        description=("A server for hosting online studies."),
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
        "init", help="create an example psyserver directory"
    )
    parser_config.set_defaults(func=init_dir)

    # parse arguments
    args = parser.parse_args()

    # run command
    if args.func == init_dir:
        return args.func()
    args.func(config_path=args.config)


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


def init_dir():
    """Initializes the directory structure."""

    dest_dir = Path.cwd()
    source_dir = Path(__file__).parent.parent / "example"

    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)

    print(f"Initialized example server to {dest_dir}.")

    return 0


def run(config_path: str | Path | None = None):
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
