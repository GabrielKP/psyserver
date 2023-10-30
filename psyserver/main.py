import os
import json
from typing import Union, Dict, List
from typing_extensions import Annotated

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


from psyserver import Settings, get_settings_toml


class ExperimentData(BaseModel, extra="allow"):
    id: str


class ExperimentDataCsv(BaseModel, extra="allow"):
    id: str
    trialdata: List[Dict] | None = None


app = FastAPI()


# @app.post("/{experiment}/save/csv")
# async def save_data(experiment: str, experiment_data: ExperimentDataCsv):
#     id = experiment_data.id
#     trialdata = experiment_data.trialdata

#     data_dir = os.path.join("data", experiment)
#     if not os.path.exists(data_dir):
#         os.makedirs(data_dir)

#     with open(os.path.join(data_dir, f"{id}.json"), "w") as f_out:
#         json.dump(experiment_data, f_out)
#     return {"status": "saved"}


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

    with open(os.path.join(data_dir, f"{id}.json"), "w") as f_out:
        json.dump(experiment_data, f_out)
    return {"status": "saved"}


settings = get_settings_toml()

app.mount(
    "/", StaticFiles(directory=settings.experiments_dir, html=True), name="exp1"
)
