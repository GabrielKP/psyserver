import pytest
from fastapi.testclient import TestClient

from psyserver.init import init_dir
from psyserver.main import create_app
from psyserver.settings import get_settings_toml


@pytest.fixture(autouse=True)
def change_test_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_dir(no_filebrowser=True)
    get_settings_toml.cache_clear()


@pytest.fixture()
def app(change_test_dir):
    return create_app()


@pytest.fixture()
def client(change_test_dir, app):
    return TestClient(app)
