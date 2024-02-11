<div align="center">

# PsyServer

## A server to host your online studies on.

</div>

<p align="center">
<a href="https://github.com/psf/black/blob/main/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://pypi.org/project/black/"><img alt="PyPI" src="https://img.shields.io/pypi/v/black"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

PsyServer is a simple, easy to setup server on which to host online studies safely and conveniently.
It does not require you to commit to a certain framework, and eliminate the need to put excessive time into setting up backends and servers.

## Features

PsyServer uses [Filebrowser](https://filebrowser.org/) to enable easy and safe access to the study code, and study data:

![Server data root](imgs/fb_root.png)

Every study placed into the `studies` folder becomes accessible from the internet.

![Experiment in Filebrowser](imgs/fb_exp_cute.png)
![Experiment available online](imgs/web_exp_cute.png)

Data from the study is saved in the `studydata` folder, which is only accessible via the filebrowser and an account.

Both the studies and studydata folder can easily modified and downloaded from the online interface, eliminating the need for `putty or ssh`.

Filebrowser allows for user management, making collaboration with others easy and convenient.

## Setup

To setup a fully functional server to host studies on, you will require following things:

1. A host machine to run the server on
2. Installing PsyServer
3. Get a domain (optional)
4. Setup HTTPS (optional)
5. Run the Server

### Host machine

A host machine to run the server on will be required. It is highly recommended it is a linux machine.
For example, you can set up an [aws ec2 instance](https://aws.amazon.com/ec2/) for little cost.

### PsyServer Setup

PsyServer itself comes as a python package and is installed as such.
At least python 3.11 is required; it is recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html). Here, we use [conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) ([miniconda installation guide](https://docs.conda.io/projects/miniconda/en/latest/)).
For easy access of files, you need to install [filebrowser] in addition.

```sh
# 1. create psyserver folder
mkdir psyserver
cd psyserver

# 2. set up conda environment (optional)
conda create -n psyserver python=3.11
conda activate psyserver

# 3. install package
pip install psyserver

# 4. install filebrowser
curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash

# 5. create example config/structure.
psyserver init

# 6. configure server (optional)
# open psyserver.toml with your editor of choice, e.g. vim
vim psyserver.toml

# 7. run server
psyserver run
```

### Running setup

Although you could just run psyserver as background job in your console, that would come at the disadvantage that when the server crashes or restarts, psyserver will not brestart automatically.
Thus it is recommended to setup PsyServer as [systemd service](https://github.com/torfsen/python-systemd-tutorial).

The `psyserver init` will create the unitfile `psyserver.service` in your directory.
You need to place that unitfile into a systemd subdirectory:

```sh
$ sudo mv psyserver.service /etc/systemd/system/
$ sudo chown root:root /etc/systemd/system/psyserver.service
$ sudo chmod 644 /etc/systemd/system/psyserver.service
```

Now reload systemctl.

```sh
$ sudo systemctl daemon-reload
```

Start the service.

```sh
$ sudo systemctl start psyserver
```

Check on the service (leave with `Q`).

```sh
$ sudo systemctl status psyserver
● psyserver.service - PsyServer Service.
     Loaded: loaded (/home/ubuntu/.config/systemd/user/psyserver.service; disabled; vendor preset: enabled)
     Active: active (running)
```

Enable the server for autostart.

```sh
$ sudo systemctl enable psyserver
```

For stopping and disabling use:

```sh
$ sudo systemctl stop psyserver
$ sudo systemctl disable psyserver
```

### Domain Name

Using a domain name is recommended, but operation is possible without. Domains can be acquired at websites such as [namecheap](https://www.namecheap.com/).
You will require a domain if you want to use https.

### https

https ensure safe communication between participants and your server. It is highly recommend to set up https.
Setting up https yourself can be quite tricky, it is thus recommended to use Caddy as Reverse Proxy.
A reverse proxy is another application running on your machine which handles the connections from the internet to a server, in this case PsyServer.

1. [Install Caddy](https://caddyserver.com/docs/install#debian-ubuntu-raspbian)
2. [Setup up the Caddy Service](https://caddyserver.com/docs/running#using-the-service)
3. [Setup Caddy as reverse Proxy](https://caddyserver.com/docs/quick-starts/reverse-proxy)

Use this Caddyfile with the default configuration of PsyServer.

```Caddyfile
example.com
{
  reverse_proxy :5000
}

admin.example.com
{
  reverse_proxy :5050
}
```

Replace `example.com` with your `domain`.

Reload Caddy `sudo systemctl reload caddy`.

That's it!

You can also setup uvicorn directly to handle https ([uvicorn https documentation](https://www.uvicorn.org/deployment/#running-with-https)). Settings are set in `psyserver.toml` under `[uvicorn]` with exactly the same keys as the documentation, without the `--`.

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
- `redirect_url`: Visitors will be redirected to this url when accessing routes that are not found. Without this key, a 404 - Not found html will be displayed.

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
The POST request can be made to `/<study>/save` which saves data as a json file.
Upon succesful saving, a json object `{success: true}` is returned.
Provide the `participantID` key such that the saved data will be named with the participantID.

```js
// example data
participant_data = {
  participantID: "debug_1",
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

## Development

### Setup

```sh
# 1. set up conda environment
$ conda create -n psyserver python=3.11
$ conda activate psyserver

# 2. clone
$ git clone git@github.com:GabrielKP/psyserver.git
$ cd psyserver

# 3. install in editor mode
$ pip install -e .
```

### Testing

```sh
# normal test
$ pytest . -v

# coverage
$ coverage run -m pytest
# html report
$ coverage html
```

### Publishing

```sh
$ flit publish
```
