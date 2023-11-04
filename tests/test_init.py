import os


def test_init_command():
    # check that files exist
    assert os.path.exists("data")
    assert os.path.exists("studies")
    assert os.path.exists("studies/exp_cute")
    assert os.path.exists("studies/exp_cute/index.html")
    assert os.path.exists("studies/exp_cute/main_script.js")
    assert os.path.exists("favicon.ico")
    assert os.path.exists("log_config.toml")
    assert os.path.exists("psyserver.toml")
    assert os.path.exists("psyserver.service")

    # check that file correctness for psyserver.service
    with open("psyserver.service", "r") as f_unit_file:
        unit_file = f_unit_file.read()

        assert "/path/to/python" not in unit_file
        assert "/path/to/psyserver" not in unit_file
