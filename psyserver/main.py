import csv
import json
import os
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
    id: str

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
    app = FastAPI()
    settings = get_settings_toml()

    @app.post("/{study}/save/csv")
    async def save_data_csv(
        study: str,
        study_data: StudyDataCsv,
        settings: Annotated[Settings, Depends(get_settings_toml)],
    ):
        id = study_data.id
        trialdata = study_data.trialdata
        fieldnames = study_data.fieldnames

        data_dir = os.path.join(settings.data_dir, study)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        now = str(datetime.now())[:19].replace(":", "-").replace(" ", "_")
        filepath = os.path.join(data_dir, f"{id}_{now}.csv")

        fieldnames = fieldnames or trialdata[0].keys()
        with open(filepath, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            try:
                for row in trialdata:
                    writer.writerow(row)
            except ValueError as err:
                error_msg = f"Trialdata contains non-specified key: {err}"
                return HTTPException(status_code=422, detail=error_msg)

        return {"success": True}

    @app.post("/{study}/save")
    async def save_data(
        study: str,
        study_data: StudyData,
        settings: Annotated[Settings, Depends(get_settings_toml)],
    ):
        id = study_data.id

        data_dir = os.path.join(settings.data_dir, study)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        now = str(datetime.now())[:19].replace(":", "-").replace(" ", "_")
        filepath = os.path.join(data_dir, f"{id}_{now}.json")

        with open(filepath, "w") as f_out:
            json.dump(dict(study_data), f_out)
        return {"success": True}

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse("favicon.ico")

    # studies
    app.mount("/", StaticFiles(directory=settings.studies_dir, html=True), name="exp1")

    @app.exception_handler(404)
    async def custom_404_handler(_, __):
        if settings.redirect_url is not None:
            return RedirectResponse(settings.redirect_url)
        return HTMLResponse(NOT_FOUND_HTML)

    return app
