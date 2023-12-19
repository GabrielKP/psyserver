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

NOT_FOUND_HTML = """\
<div style="display:flex;flex-direction:column;justify-content:center;text-align:center;"><h1>404 - Not Found</h1></div>
"""


class StudyData(BaseModel, extra="allow"):
    study_id: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "debug_1",
                    "condition": "1",
                    "experiment1": [2, 59, 121, 256],
                    "experiment2": ["yes", "maybe", "yes"],
                }
            ]
        }
    }


class StudyDataCsv(BaseModel):
    id: str
    trialdata: List[Dict]
    fieldnames: List[str] | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "debug_1",
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

        study_id = ""
        if study_data.study_id is not None:
            study_id = f"{study_data.study_id}_"
        else:
            ret_json[
                "status"
            ] = "Entry 'study_id' not provided. Saved data only with timestamp."
        now = str(datetime.now())[:19].replace(":", "-").replace(" ", "_")
        filepath = os.path.join(data_dir, f"{study_id}{now}.json")

        with open(filepath, "w") as f_out:
            json.dump(dict(study_data), f_out)
        return ret_json

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse("favicon.ico")

    @app.get("/{study}/get_condition")
    def get_condition(
        study: str,
        settings: Annotated[Settings, Depends(get_settings_toml)],
    ):
        filepath = os.path.join(settings.data_dir, study, "conditions.json")
        if not os.path.exists(filepath):
            return {"success": False, "status": "no condition config"}

        try:
            with open(filepath, "r") as f_condition_config_in:
                conditions: Dict[str | int, int] = json.load(f_condition_config_in)
                if conditions == {}:
                    return {"success": False, "status": "no conditions in config"}
                # find condition with most open spots
                try:
                    chosen_condition = sorted(
                        list(conditions.items()), key=lambda x: -x[1]
                    )[0][0]

                    # update condition config
                    conditions[chosen_condition] -= 1

                except IndexError:
                    return {"success": False, "status": "condition config is invalid"}

            with open(filepath, "w") as f_condition_config_out:
                # write condition config
                json.dump(conditions, f_condition_config_out)
        except json.JSONDecodeError:
            return {
                "success": False,
                "status": "Concurrency limitation in get_condition implementation",
            }

        return {"success": True, "condition": chosen_condition}

    # studies
    app.mount("/", StaticFiles(directory=settings.studies_dir, html=True), name="exp1")

    @app.exception_handler(404)
    async def custom_404_handler(_, __):
        if settings.redirect_url is not None:
            return RedirectResponse(settings.redirect_url)
        return HTMLResponse(NOT_FOUND_HTML)

    return app
