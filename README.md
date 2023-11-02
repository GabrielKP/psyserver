# psyserver

A server to host online studies on.

## Run

```sh
# 1. set up conda environment
conda create -n psyserver python=3.11
conda activate psyserver

# 2. install package
pip install psyserver

# 3. create psyserver folder
mkdir server
cd server

# 3. create example config/structure
psyserver init

# 4. configure server
# open psyserver.toml with your editor of choice, e.g. vim
vim psyserver.toml

# 5. run server
psyserver run
```

## Configuration

The server is configured in the file `psyserver.toml`.
This file has to be in the directory from which you call `psyserver run`.

The configuration has two groups:

1. psyserver
2. uvicorn

### psyserver config

```toml
[psyserver]
studies_dir = "studies"
data_dir = "data"
```

Here you can configure following fields:

- `studies_dir`: path to directory which contains studies. Any directory inside will be reachable via the url. E.g. a study in `<studies_dir>/exp_cute/index.html` will have the url `<host>:<port>/exp_cute/index.html`.
- `data_dir`: directory in which study data is saved. E.g. data submissions to the url `<host>:<port>/exp_cute/save` will be saved in `<data_dir>/exp_cute/`. Has to be different from `studies_dir`.

### uvicorn config

```toml
[uvicorn]
host = "127.0.0.1"
port = 5000
log_level = "info"
```

This configures the uvicorn instance runnning the server. You can specify the `host`, `port` and https.
For all possible keys, go to the [uvicorn settings documentation](https://www.uvicorn.org/settings/).

## How to save data to psyserver

Participant data sent to the server needs to adhere to a certain format.

We recommend using jquery to post the data.

Generally, data is sent to `/<study>/save`.

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
