<div align="center">

# PsyServer

## A server to host your online studies on.

</div>

<p align="center">
<a href="https://github.com/psf/black/blob/main/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://pypi.org/project/black/"><img alt="PyPI" src="https://img.shields.io/pypi/v/black"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

PsyServer is a simple, easy to setup server on which you can host your online studies safely and conveniently without committing to a certain framework to code the experiments. Eliminate the need to put excessive time into setting up backends and servers!

## Setup

To setup a fully functional server to host studies on, you will require following things:

1. A host machine to run the server on
2. Installing PsyServer
3. Get a domain (optional)
4. Setup HTTPS (optional)
5. Run the Server

### Host machine

### PsyServer Setup

PsyServer comes as a python package, meaning that installing it is as easy as installing a python package!

```sh
# 1. create psyserver folder
mkdir server
cd server

# 2. set up conda environment (optional)
conda create -n psyserver python=3.11
conda activate psyserver

# 3. install package
pip install psyserver

# 4. create example config/structure
psyserver init

# 5. configure server
# open psyserver.toml with your editor of choice, e.g. vim
vim psyserver.toml

# 6. run server
psyserver run
```

### Domain Name

### HTTPS

To setup up a https server, you can use a reverse proxy or setup the uvicorn instance running

### Running setup

Systemd

## Configuration

`psyserver.toml` configures the server.
This file has to be in the directory from which `psyserver run` is called.

The configuration has two groups:

1. psyserver: all PsyServer configuratons
2. uvicorn: Uvicorn configurations

### psyserver config

```toml
[psyserver]
studies_dir = "studies"
data_dir = "data"
redirect_url = "https://www.example.com"
```

- `studies_dir`: path to directory which contains studies. Any directory inside will be reachable via the url. E.g. a study in `<studies_dir>/exp_cute/index.html` will have the url `<host>:<port>/exp_cute/index.html`.
- `data_dir`: directory in which study data is saved. E.g. data submissions to the url `<host>:<port>/exp_cute/save` will be saved in `<data_dir>/exp_cute/`. Has to be different from `studies_dir`.
- `redirect_url`: Visitors will be redirected to this url when accessing routes that are not found.

### uvicorn config

```toml
[uvicorn]
host = "127.0.0.1"
port = 5000
```

Here configures the uvicorn instance runnning the server. For example, uou can specify the `host`, `port` and https configurations.
For all possible options, use the commands in the [uvicorn settings documentation](https://www.uvicorn.org/settings/) without `--`.

## How to save data to psyserver

To save participant data to the server it has to be sent in the json format of a POST request.
The POST request can be made to `/<study>/save` which saves data as a json file, or `/<study>/save/csv` which save data as a csv file.
Upon succesful saving, a json object `{success: true}` is returned.

### Save as json

```js
// example data
participant_data = {
  id: "debug_1",
  condition: "1",
  experiment1: [2, 59, 121, 256],
  // ...
};
// post data to server
$.ajax({
  url: "/exp_cute/save",
  type: "POST",
  data: JSON.stringify(participant_data),
  contentType: "application/json",
  success: () => {
    console.log("Saving successful");
    // success function
  },
}).fail(() => {
  console.log("ERROR with $.post()");
});
```

**Note that you need to call `JSON.stringify` on your data**. Without this, you will get an `unprocessable entity` error.

### Save as csv

If you want to save your data as `.csv`, you can call `/<study>/save/csv`.

The transmitted `json` object is required to have following parameters:

- `id`: The participant id, used as a filename.
- `trialdata`: A list of dict-like objects. The keys of the first row of this list is used to determine the csv header. If new keys are encountered, an `422 - unprocessable entity` error will be raised.
- `fieldnames`: A list of strings containing the names . Keys encountered in trialdata will be saved in this order. This field is useful if you have varying keys in `trialdata`, and do not want to modify the first entry to have all keys.

#### Example without fieldnames

```js
// example data
participant_data = {
  id: "debug_1",
  trialdata: [
    { trial: 1, time: 120230121, correct: true },
    { trial: 2, time: 120234001, correct: false },
    { trial: 3, time: 120237831, correct: true },
    // ....
  ],
};
// post data to server
$.ajax({
  url: "/exp_cute/save/csv",
  type: "POST",
  data: JSON.stringify(participant_data),
  contentType: "application/json",
  success: () => {
    console.log("Saving successful");
    // success function
  },
}).fail(() => {
  console.log("ERROR with $.post()");
});
```

Will be saved as `<data_dir>/exp_cute/debug_1_CURRENTDATETIME.csv`:

```csv
trial,time,correct
1,120230121,true
2,120234001,false
3,120237831,true
```

#### Example with fieldnames

This

```js
// example data
participant_data = {
  id: "debug_1",
  trialdata: [
    { trial: 1, time: 120230121, correct: true },
    { trial: 2, time: 120234001, correct: false, extra: "field" },
    { trial: 3, time: 120237831, correct: true },
    // ....
  ],
  fieldnames: ["trial", "time", "correct", "extra"],
};
// post data to server
$.ajax({
  url: "/exp_cute/save/csv",
  type: "POST",
  data: JSON.stringify(participant_data),
  contentType: "application/json",
  success: () => {
    console.log("Saving successful");
    // success function
  },
}).fail(() => {
  console.log("ERROR with $.post()");
});
```

Will be saved as `<data_dir>/exp_cute/debug_1_CURRENTDATETIME.csv`:

```csv
trial,time,correct,extra
1,120230121,true,,
2,120234001,false,field
3,120237831,true,
```

## Development

### Setup

```sh
# 1. set up conda environment
conda create -n psyserver python=3.11
conda activate psyserver

# 2. clone
git clone git@github.com:GabrielKP/psyserver.git
cd psyserver

# 3. install in editor mode
pip install -e .
```

### Testing

```sh
# normal test
pytest . -v

# coverage
coverage run -m pytest
# html report
coverage html
```
