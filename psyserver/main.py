import csv
import json
import os
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Union

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing_extensions import Annotated

from psyserver.settings import Settings, get_settings_toml
from psyserver.db import get_increment_study_count_db, set_study_count_db

NOT_FOUND_HTML = """\
<div style="display:flex;flex-direction:column;justify-content:center;text-align:center;"><h1>404 - Not Found</h1></div>
"""


class StudyData(BaseModel, extra="allow"):
    participantID: str | None = None

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
        p_filebrowser = subprocess.Popen(
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

        participantID = ""
        if study_data.participantID is not None:
            participantID = f"{study_data.participantID}_"
            study_data_to_save = dict(study_data)
        else:
            ret_json["status"] = (
                "Entry 'participantID' not provided. Saved data only with timestamp."
            )
            study_data_to_save = dict(study_data)
            study_data_to_save.pop("participantID")
        now = str(datetime.now())[:19].replace(":", "-").replace(" ", "_")
        filepath = os.path.join(data_dir, f"{participantID}{now}.json")

        with open(filepath, "w") as f_out:
            json.dump(study_data_to_save, f_out)
        return ret_json

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
