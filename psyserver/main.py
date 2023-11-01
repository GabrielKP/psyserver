import csv
import os
import json
from datetime import datetime
from typing import Union, Dict, List
from typing_extensions import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


from psyserver import Settings, get_settings_toml


class ExperimentData(BaseModel, extra="allow"):
    id: str


class ExperimentDataCsv(BaseModel):
    id: str
    trialdata: List[Dict] | None = None
    fieldnames: List[str] | None = None


app = FastAPI()


@app.post("/{experiment}/save/csv")
async def save_data(experiment: str, experiment_data: ExperimentDataCsv):
    id = experiment_data.id
    trialdata = experiment_data.trialdata
    fieldnames = experiment_data.fieldnames

    data_dir = os.path.join("data", experiment)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    now = str(datetime.now())[:19].replace(":", "-")

    fieldnames = fieldnames or trialdata[0].keys()
    with open(os.path.join(data_dir, f"{id}_{now}.json"), "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        try:
            for row in trialdata:
                writer.writerow(row)
        except ValueError as err:
            error_msg = f"Trialdata contains non-specified key: {err}"
            return HTTPException(status_code=422, detail=error_msg)

    return {"status": "saved"}


@app.post("/{experiment}/save")
async def save_data(
    experiment: str,
    experiment_data: ExperimentData,
    settings: Annotated[Settings, Depends(get_settings_toml)],
):
    id = experiment_data.id

    data_dir = os.path.join(settings.data_dir, experiment)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    now = str(datetime.now())[:19].replace(":", "-")

    with open(os.path.join(data_dir, f"{id}_{now}.json"), "w") as f_out:
        json.dump(dict(experiment_data), f_out)
    return {"status": "saved"}


settings = get_settings_toml()

app.mount(
    "/", StaticFiles(directory=settings.experiments_dir, html=True), name="exp1"
)
