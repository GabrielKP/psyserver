import pytest

from fastapi.testclient import TestClient

from psyserver.init import init_dir
from psyserver.main import create_app


@pytest.fixture(autouse=True)
def change_test_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_dir()


@pytest.fixture()
def app(change_test_dir):
    return create_app()


@pytest.fixture()
def client(change_test_dir, app):
    return TestClient(app)
