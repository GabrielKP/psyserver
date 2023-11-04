import argparse

from .run import run_server
from .init import init_dir


__version__ = "0.2.0+dev.1"


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
    parser_run.set_defaults(func=run_server)

    # config command
    parser_config = subparsers.add_parser(
        "init", help="create an example psyserver directory"
    )
    parser_config.add_argument(
        "--no-unit-file",
        type=str,
        action="store_true",
        help="do not place the unit file in ~/.config/systemd/user/",
    )
    parser_config.set_defaults(func=init_dir)

    # parse arguments
    args = parser.parse_args()

    # run command
    if args.func == init_dir:
        return args.func(no_unit_file=args.no_unit_file)
    args.func(config_path=args.config)


if __name__ == "__main__":
    main()
