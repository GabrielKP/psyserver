import tomllib
from pathlib import Path

import uvicorn

from psyserver.settings import default_config_path


def run_server():
    """Runs the server given config.

    Parameters
    ----------
    config_path : str | None, default = `None`
        Path to a configuration file. If `None`, then configuration in
        the current directory is used.
    """

    config_path = default_config_path()
    with open(config_path, "rb") as configfile:
        config = tomllib.load(configfile)

    # Infuriatingly, variables cannot be passed into the application.
    # Therefore, the path of the config file has to be passed via an .env.

    uvicorn_config = uvicorn.Config(
        "psyserver.main:create_app", factory=True, **config["uvicorn"]
    )
    server = uvicorn.Server(uvicorn_config)
    server.run()
