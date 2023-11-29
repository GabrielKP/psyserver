import shutil
import sys
from pathlib import Path


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


def init_dir(no_unit_file: bool = False):
    """Initializes the directory structure."""

    dest_dir = Path.cwd()
    source_dir = Path(__file__).parent / "example"

    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)

    replace_paths_unit_file(dest_dir)

    print(f"Initialized example server to {dest_dir}.")

    return 0
