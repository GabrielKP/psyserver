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

# 5. run server
psyserver run

```

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
