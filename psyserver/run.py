import tomllib
from pathlib import Path

import uvicorn

from psyserver.settings import default_config_path


def run_server(config_path: str | Path | None = None):
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

    uvicorn_config = uvicorn.Config(
        "psyserver.main:create_app", factory=True, **config["uvicorn"]
    )
    server = uvicorn.Server(uvicorn_config)
    server.run()


def start():
    pass


def stop():
    pass
