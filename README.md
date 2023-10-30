# psyserver

A server to host online experiments on.

## Run

```sh
# 1. set up conda environment
conda create -n psyserver python=3.11
conda activate psyserver

# 2. install package
pip install psyserver

# 3. create example config
psyserver config

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
experiments_dir = "experiments"
data_dir = "data"
```

Here you can configure following fields:

- `experiments_dir`: path to directory which contains experiments. Any directory inside will be reachable via the url. E.g. an experiment in `<experiments_dir>/exp_cute/index.html` will have the url `<host>:<port>/exp_cute/index.html`.
- `data_dir`: directory in which experiment data is saved. Has to be different from `experiments_dir`. E.g. data submissions to `<host>:<port>/exp_cute/save` will be saved in `<data_dir>/exp_cute/`

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

Generally, data is sent to `/<experiment>/save`.

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

## Development setup

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
