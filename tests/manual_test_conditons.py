from multiprocessing import Pool

import requests


def req(idx):
    res = requests.api.get("http://127.0.0.1:5000/exp_cute/get_condition")
    print(f"{idx} {res.text}")


if __name__ == "__main__":
    with Pool(30) as p:
        p.map(req, list(range(30)))
