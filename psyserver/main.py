import json
import os
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Union

import requests
from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing_extensions import Annotated

from psyserver.db import get_increment_study_count_db, set_study_count_db
from psyserver.settings import Settings, get_settings_toml

NOT_FOUND_HTML = """\
<div style="display:flex;flex-direction:column;justify-content:center;
text-align:center;"><h1>404 - Not Found</h1></div>
"""


class StudyData(BaseModel, extra="allow"):
    participantID: str | None = None
    h_captcha_response: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "participantID": "debug_1",
                    "condition": "1",
                    "experiment1": [2, 59, 121, 256],
                    "experiment2": ["yes", "maybe", "yes"],
                }
            ]
        }
    }


class StudyDataCsv(BaseModel):
    participantID: str
    trialdata: List[Dict]
    fieldnames: List[str] | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "participantID": "debug_1",
                    "trialdata": [
                        {"trial": 1, "condition": "1", "response": 2},
                        {"trial": 2, "condition": "1", "response": 59},
                        {"trial": 3, "condition": "1", "response": 121},
                        {"trial": 4, "condition": "1", "response": 256},
                    ],
                }
            ]
        }
    }


def create_app() -> FastAPI:
    # open filebrowser
    filebrowser_path = shutil.which("filebrowser")
    if filebrowser_path is None:
        print("CRITICAL: Filebrowser not found. Please install filebrowser.")
    else:
        subprocess.Popen(
            [filebrowser_path, "-c", "filebrowser.toml", "-r", "data"],
            stdout=subprocess.PIPE,
        )

    # server
    app = FastAPI()
    settings = get_settings_toml()

    @app.post("/{study}/save")
    async def save_data(
        study: str,
        study_data: StudyData,
        settings: Annotated[Settings, Depends(get_settings_toml)],
    ) -> Dict[str, Union[bool, str]]:
        """Save submitted json object to file."""
        ret_json: Dict[str, Union[bool, str]] = {"success": True}
        data_dir = os.path.join(settings.data_dir, study)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        ret_json["status"] = ""

        # Deal with participantID
        participantID = ""
        if study_data.participantID is not None:
            participantID = f"{study_data.participantID}_"
            study_data_to_save = dict(study_data)
        else:
            ret_json["status"] += (
                " Entry 'participantID' not provided. Saved data only with timestamp."
            )
            study_data_to_save = dict(study_data)
            study_data_to_save.pop("participantID")

        # Deal with hcaptcha response
        if study_data.h_captcha_response is not None:
            if settings.h_captcha_secret is None:
                ret_json["status"] += " h_captcha_verification: secret missing"
                study_data_to_save["h_captcha_verification"] = "secret missing"
            else:
                response = requests.post(
                    settings.h_captcha_verify_url,
                    data=dict(
                        secret=settings.h_captcha_secret,
                        response=study_data.h_captcha_response,
                    ),
                )
                if response.status_code == 200:
                    suc = response.json()["success"]
                    study_data_to_save["h_captcha_verification"] = (
                        "verified" if suc else "unverified"
                    )
                else:
                    study_data_to_save["h_captcha_verification"] = "verification failed"

        else:
            ret_json["status"] += " h_captcha_verification: h_captcha_response missing"
            study_data_to_save["h_captcha_verification"] = "h_captcha_response missing"

        if ret_json["status"] == "":
            ret_json.pop("status")

        # Save data
        now = str(datetime.now())[:19].replace(":", "-").replace(" ", "_")
        filepath = os.path.join(data_dir, f"{participantID}{now}.json")

        with open(filepath, "w") as f_out:
            json.dump(study_data_to_save, f_out)
        return ret_json

    @app.post("/{study}/save_audio")
    async def save_audio(
        study: str,
        participantID: Annotated[str, Form()],
        audioID: Annotated[str, Form()],
        form_data: Annotated[UploadFile, File()],
        settings: Annotated[Settings, Depends(get_settings_toml)],
    ) -> Dict[str, Union[bool, str]]:
        """Save audio data uploaded as UploadFile."""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{participantID}_{audioID}_{timestamp}.webm"

        data_dir = os.path.join(settings.data_dir, study, "audio")
        os.makedirs(data_dir, exist_ok=True)

        with open(os.path.join(data_dir, filename), "wb") as f_out:
            f_out.write(await form_data.read())
        return {"success": True, "filename": filename}

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse("favicon.ico")

    @app.get("/{study}/get_count")
    def get_increment_study_count(study: str):
        count, error = get_increment_study_count_db(study)
        if error is not None:
            return {"success": False, "count": None, "error": error}
        return {"success": True, "count": count}

    @app.get("/{study}/set_count/{count}")
    def set_study_count(study: str, count: int):
        error = set_study_count_db(study, count)
        if error is not None:
            return {"success": False, "error": error}
        return {"success": True}

    # studies
    app.mount("/", StaticFiles(directory=settings.studies_dir, html=True), name="exp1")

    @app.exception_handler(404)
    async def custom_404_handler(_, __):
        if settings.redirect_url is not None:
            return RedirectResponse(settings.redirect_url)
        return HTMLResponse(NOT_FOUND_HTML)

    return app
