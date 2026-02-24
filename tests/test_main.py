import json
import os
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import requests

from psyserver.settings import get_settings_toml

cute_exp_html_start = """\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>How cute?</title>
  </head>
"""


def test_exp_cute_index(client):
    response = client.get("/exp_cute/")
    assert response.status_code == 200
    assert response.text[:100] == cute_exp_html_start


def test_save_data_json1(client):
    example_data = {
        "participantID": "debug_1",
        "condition": "1",
        "experiment1": [2, 59, 121, 256],
    }
    mock_open_exp_data = mock_open()
    mock_datetime = Mock()
    mock_datetime.now = Mock(return_value="2023-11-02_01:49:39.905657")
    with (
        patch("psyserver.main.open", mock_open_exp_data, create=False),
        patch("psyserver.main.datetime", mock_datetime),
    ):
        response = client.post("/exp_cute/save", json=example_data)
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "status": " h_captcha_verification: h_captcha_response missing",
    }
    written_data = "".join(
        [_call.args[0] for _call in mock_open_exp_data.mock_calls[2:-1]]
    )
    example_data["h_captcha_response"] = None
    example_data["h_captcha_verification"] = "h_captcha_response missing"
    written_json = json.loads(written_data)
    for key, value in written_json.items():
        assert value == example_data[key]
    mock_open_exp_data.assert_called_once_with(
        "data/studydata/exp_cute/debug_1_2023-11-02_01-49-39.json", "w"
    )


def test_save_data_json2(client):
    """no id, saving with timestamp instead."""
    example_data = {
        "wrong_id_field": "debug_1",
        "condition": "1",
        "experiment1": [2, 59, 121, 256],
    }
    mock_open_exp_data = mock_open()
    mock_datetime = Mock()
    mock_datetime.now = Mock(return_value="2023-11-02_01:49:39.905657")
    with (
        patch("psyserver.main.open", mock_open_exp_data, create=False),
        patch("psyserver.main.datetime", mock_datetime),
    ):
        response = client.post("/exp_cute/save", json=example_data)
    assert response.status_code == 200
    assert response.json()["success"]

    written_data = "".join(
        [_call.args[0] for _call in mock_open_exp_data.mock_calls[2:-1]]
    )
    example_data["h_captcha_response"] = None
    example_data["h_captcha_verification"] = "h_captcha_response missing"
    written_json = json.loads(written_data)
    for key, value in written_json.items():
        assert value == example_data[key]
    mock_open_exp_data.assert_called_once_with(
        "data/studydata/exp_cute/2023-11-02_01-49-39.json", "w"
    )


def test_get_count_new_study(client):
    """Get the count for a study not in the table yet"""
    response = client.get("/test/get_count")
    assert response.status_code == 200
    assert response.json()["success"]
    assert response.json()["count"] == 0


def test_set_count_new_study(client):
    """Set the count for a study not in the table yet"""
    response = client.get("/test/set_count/5")
    assert response.status_code == 200
    assert response.json()["success"]

    response = client.get("/test/get_count")
    assert response.status_code == 200
    assert response.json()["success"]
    assert response.json()["count"] == 5


def test_get_count_increment(client):
    """Check whether count increments automatically"""
    client.get("/test/set_count/1")
    response = client.get("/test/get_count")
    assert response.status_code == 200
    assert response.json()["success"]
    assert response.json()["count"] == 1

    response = client.get("/test/get_count")
    assert response.status_code == 200
    assert response.json()["success"]
    assert response.json()["count"] == 2


def test_set_count_invalid_count(client):
    """Check whether invalid inputs throw the correct error."""

    response = client.get("/test/set_count/hi")
    print(response.json())
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "int_parsing"

    # test that correct input still works afterwards
    response = client.get("/test/set_count/2")
    assert response.status_code == 200
    assert response.json()["success"]

    response = client.get("/test/get_count")
    assert response.status_code == 200
    assert response.json()["success"]
    assert response.json()["count"] == 2


def test_save_data_json_h_captcha_no_secret_key(client):
    example_data = {
        "participantID": "debug_1",
        "condition": "1",
        "experiment1": [2, 59, 121, 256],
        "h_captcha_response": "valid-response",
    }

    # control data saving
    mock_open_exp_data = mock_open()
    mock_datetime = Mock()
    mock_datetime.now = Mock(return_value="2023-11-02_01:49:39.905657")

    # set secret key
    with (
        patch("psyserver.main.open", mock_open_exp_data, create=False),
        patch("psyserver.main.datetime", mock_datetime),
    ):
        response = client.post("/exp_cute/save", json=example_data)
    print(response.text)
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "status": " h_captcha_verification: secret missing",
    }
    written_data = "".join(
        [_call.args[0] for _call in mock_open_exp_data.mock_calls[2:-1]]
    )
    assert json.loads(written_data)["h_captcha_verification"] == "secret missing"
    mock_open_exp_data.assert_called_once_with(
        "data/studydata/exp_cute/debug_1_2023-11-02_01-49-39.json", "w"
    )


def test_save_data_json_h_captcha_verified(client):
    example_data = {
        "participantID": "debug_1",
        "condition": "1",
        "experiment1": [2, 59, 121, 256],
        "h_captcha_response": "valid-response",
    }

    # load config to test its url and use later to replace
    mock_default_config_path = Mock(
        return_value=Path.cwd() / "psyserver" / "example" / "psyserver.toml"
    )
    with patch("psyserver.settings.default_config_path", mock_default_config_path):
        settings = get_settings_toml()

    # ensure h_captcha verification is replaced with mock
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json = Mock(return_value={"success": True})
    mock_request_post = Mock(return_value=mock_resp)

    # control data saving
    mock_open_exp_data = mock_open()
    mock_datetime = Mock()
    mock_datetime.now = Mock(return_value="2023-11-02_01:49:39.905657")

    # set secret key
    settings.h_captcha_secret = "secret key!"
    mock_get_settings = Mock(return_value=settings)
    with (
        patch("psyserver.main.open", mock_open_exp_data, create=False),
        patch("psyserver.main.datetime", mock_datetime),
        patch("psyserver.settings.get_settings_toml", mock_get_settings),
        patch("psyserver.main.requests.post", mock_request_post),
    ):
        response = client.post("/exp_cute/save", json=example_data)
    assert response.status_code == 200
    assert response.json() == {"success": True}
    written_data = "".join(
        [_call.args[0] for _call in mock_open_exp_data.mock_calls[2:-1]]
    )
    assert json.loads(written_data)["h_captcha_verification"] == "verified"
    mock_open_exp_data.assert_called_once_with(
        "data/studydata/exp_cute/debug_1_2023-11-02_01-49-39.json", "w"
    )


def test_save_audio_without_session_dir(client):
    """Save audio without session_dir — should default to {study}/audio/."""
    mock_open_audio = mock_open()
    mock_datetime = Mock()
    mock_datetime.now = Mock(
        return_value=Mock(strftime=Mock(return_value="20231102_014939"))
    )
    with (
        patch("psyserver.main.open", mock_open_audio, create=False),
        patch("psyserver.main.datetime", mock_datetime),
    ):
        response = client.post(
            "/exp_cute/save_audio",
            files={"audio_data": ("participant_1.webm", b"fake-audio", "audio/webm")},
        )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["filename"] == "participant_1_20231102_014939.webm"
    mock_open_audio.assert_called_once_with(
        os.path.join(
            "data",
            "studydata",
            "exp_cute",
            "audio",
            "participant_1_20231102_014939.webm",
        ),
        "wb",
    )


def test_save_audio_with_session_dir(client):
    """Save audio with session_dir — should nest under {study}/{session_dir}/audio/."""
    mock_open_audio = mock_open()
    mock_datetime = Mock()
    mock_datetime.now = Mock(
        return_value=Mock(strftime=Mock(return_value="20231102_014939"))
    )
    with (
        patch("psyserver.main.open", mock_open_audio, create=False),
        patch("psyserver.main.datetime", mock_datetime),
    ):
        response = client.post(
            "/exp_cute/save_audio",
            files={"audio_data": ("participant_1.webm", b"fake-audio", "audio/webm")},
            data={"session_dir": "screening"},
        )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["filename"] == "participant_1_20231102_014939.webm"
    mock_open_audio.assert_called_once_with(
        os.path.join(
            "data",
            "studydata",
            "exp_cute",
            "screening",
            "audio",
            "participant_1_20231102_014939.webm",
        ),
        "wb",
    )


def test_save_data_json_h_captcha_failed_response(client):
    example_data = {
        "participantID": "debug_1",
        "condition": "1",
        "experiment1": [2, 59, 121, 256],
        "h_captcha_response": "valid-response",
    }

    # load config to test its url and use later to replace
    mock_default_config_path = Mock(
        return_value=Path.cwd() / "psyserver" / "example" / "psyserver.toml"
    )
    with patch("psyserver.settings.default_config_path", mock_default_config_path):
        settings = get_settings_toml()

    # ensure h_captcha verification is replaced with mock
    mock_resp = Mock()
    mock_resp.status_code = 403
    mock_resp.json = Mock(return_value={"success": False})
    mock_request_post = Mock(return_value=mock_resp)

    # control data saving
    mock_open_exp_data = mock_open()
    mock_datetime = Mock()
    mock_datetime.now = Mock(return_value="2023-11-02_01:49:39.905657")

    # set secret key
    settings.h_captcha_secret = "secret key!"
    mock_get_settings = Mock(return_value=settings)
    with (
        patch("psyserver.main.open", mock_open_exp_data, create=False),
        patch("psyserver.main.datetime", mock_datetime),
        patch("psyserver.settings.get_settings_toml", mock_get_settings),
        patch("psyserver.main.requests.post", mock_request_post),
    ):
        response = client.post("/exp_cute/save", json=example_data)
    assert response.status_code == 200
    assert response.json() == {"success": True}
    written_data = "".join(
        [_call.args[0] for _call in mock_open_exp_data.mock_calls[2:-1]]
    )
    assert json.loads(written_data)["h_captcha_verification"] == "verification failed"
    mock_open_exp_data.assert_called_once_with(
        "data/studydata/exp_cute/debug_1_2023-11-02_01-49-39.json", "w"
    )
