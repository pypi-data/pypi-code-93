from typing import Any, Dict, List, Union
import numpy as np
import pandas as pd


def fake_integer(n):
    return np.random.randint(-1000, 1000, n)


def fake_boolean(n):
    return np.random.random(n) > 0.5


def fake_number(n):
    return np.random.normal(0, 100, n)


def fake_datetime(n):
    start_u = 0
    end_u = 1599000000000000000
    return pd.to_datetime(np.random.randint(start_u, end_u, n))


def fake_category(
    n, p=(0.49, 0.29, 0.21, 0.01), c=("Medium", "Low", "High", "Unknown")
):
    if not p:
        # default probabilities
        p = p
    c = c
    return np.random.choice(c, size=n, p=p).astype("str")


def random_normal(n, mu=0, sigma=0.1):
    mu, sigma = 0, 0.1  # mean and standard deviation
    rn: Union[int, float, complex] = np.random.normal(mu, sigma, n)
    return rn


mapping = {
    "integer": fake_integer,
    "boolean": fake_boolean,
    "number": fake_number,
    "datetime": fake_datetime,
    "duration": None,
    "any": fake_category,
    "string": fake_category,
}


def generate_fake_dataframe(schema, n, null=False):
    df = pd.DataFrame()
    for field in schema["fields"]:
        if field["name"] == "timestamp":
            df[field["name"]] = fake_datetime(n)
        else:
            df[field["name"]] = mapping[field["type"]](n)
            if (
                null
                and field["type"] not in ("integer", "datetime")
                and field["name"] not in ("id")
            ):
                df[field["name"]][np.random.random(df.shape[0]) > 0.9] = np.nan
    return df
