import getpass
import shutil
import subprocess
import sys
from pathlib import Path
from subprocess import CalledProcessError

from psyserver.db import create_studies_table


def replace_paths_unit_file(project_dir: Path):
    """Replaces python path and psyserver path in unit file example."""

    unit_file_path = project_dir / "psyserver.service"
    with open(unit_file_path, "r") as f_unit_file:
        unit_file = f_unit_file.read()

    python_path = sys.executable
    script_path = str(Path(__file__).parent)
    unit_file = unit_file.replace("/path/to/python", python_path)
    unit_file = unit_file.replace("/path/to/psyserver_package", script_path)
    unit_file = unit_file.replace("/path/to/psyserver_dir", str(project_dir))

    with open(unit_file_path, "w") as f_unit_file:
        f_unit_file.write(unit_file)

    return 0


def init_dir(no_filebrowser: bool = False):
    """Initializes the directory structure."""

    # copy example
    dest_dir = Path.cwd()
    source_dir = Path(__file__).parent / "example"

    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)

    # replace the paths
    replace_paths_unit_file(dest_dir)

    # Create the studies sqlite file
    create_studies_table()

    # init filebrowser
    filebrowser_path = shutil.which("filebrowser")
    if filebrowser_path is None:
        print(
            "Filebrowser not found. Install it by running: "
            "curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash"
        )
    elif no_filebrowser:
        print("Skipping filebrowser initialization.")
    else:
        print("Initializing filebrowser...")
        try:
            subprocess.run(
                [
                    filebrowser_path,
                    "config",
                    "init",
                    "-c",
                    "filebrowser.toml",
                    "-r",
                    "data",
                ],
                stdout=subprocess.PIPE,
            ).check_returncode()
            print("Administrator account:")
            admin_username = input("Username: ")
            admin_password = getpass.getpass()

            subprocess.run(
                [
                    filebrowser_path,
                    "users",
                    "add",
                    admin_username,
                    admin_password,
                    "--perm.admin",
                ],
                stdout=subprocess.PIPE,
            ).check_returncode()
        except CalledProcessError:
            print("Error with filebrowser init. Aborting.")
            # TODO: cleanup failed init attempt.
            return 1

    print(f"Initialized example server to {dest_dir}.")

    return 0
