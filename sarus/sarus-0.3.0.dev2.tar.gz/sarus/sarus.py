"""Copyright 2020 Sarus SAS.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Sarus library to leverage sensitive data without revealing them

This lib contains classes and method to browse,
learn from & explore sensitive datasets.
It connects to a Sarus server, which acts as a gateway, to ensure no
results/analysis coming out of this lib are sensitive.
"""
from __future__ import annotations  # noqa: F407

import base64
import datetime
import getpass
import io
import json
import os
import re
import sys
import tarfile
import tempfile
import textwrap
import time
import webbrowser
from io import BytesIO
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import cloudpickle
import matplotlib.pyplot as plt
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from PIL import Image
from requests import Session

import pandas as pd
import tensorflow as tf
from sarus.tensorflow import SarusTensorflowDataset
from tensorflow.keras.models import Model


class Dataset:
    """A class representing a Sarus dataset.

    This class is the interface to the private data. It enables to inspect the
    dataset metadata, manipulate synthetic data locally, prepare processing
    steps and identify the dataset for executing remote private queries.

    Args:
        name: The dataset name.
        id: The dataset id
        client: The Sarus client where the dataset is defined.
        type_metadata: A serialized json holding the dataset metadata.
        marginals: A serialized json holding the dataset marginals.
        URI: The dataset URI.
        human_description: A short human readable description.
        policy:
        transforms:
            A list of transformations to be applied to the original dataset.
    """

    def __init__(
        self,
        name: str,
        id: int,
        client: "Client",
        type_metadata: Optional[str] = None,
        URI: Optional[str] = None,
        human_description: Optional[str] = None,
        marginals: Optional[str] = None,
        policy: Optional[dict] = None,
        transforms: List = [],
    ):
        self.name: str = name
        self.id: int = id
        self.client: "Client" = client
        self.type_metadata: Optional[Dict[str, Any]] = None
        if type_metadata is not None:
            self.type_metadata = json.loads(type_metadata)
        self.URI: Optional[str] = URI
        self.human_description: Optional[str] = human_description
        self._synthetic: Optional[pd.DataFrame] = None
        self._synthetic_rows_number: Optional[int] = None
        self.marginals: Optional[Dict[str, Any]] = None
        if marginals is not None:
            self.marginals = json.loads(marginals)
        self.policy: Optional[dict] = policy

        # We set `unbatch` as the default first transform
        # for a better user experience.
        # TODO remove the default batching on the API side
        if len(transforms) == 0:
            transforms.append(("unbatch", {}))
        self.transforms = transforms

    def _add_transform(self, transform: Tuple[str, Dict]) -> Dataset:
        """Create a new dataset with an additional transform."""
        return Dataset(
            name=self.name,
            id=self.id,
            client=self.client,
            type_metadata=json.dumps(self.type_metadata),
            URI=self.URI,
            human_description=self.human_description,
            marginals=json.dumps(self.marginals),
            policy=self.policy,
            transforms=self.transforms + [transform],
        )

    def split(
        self, split: Union[str, List[str]]
    ) -> Union[Dataset, List[Dataset]]:
        """Get subsets of the Sarus dataset.

        The `split` parameter is a string who specifies a slice of the dataset
        to select. The format is inspired by the format used by Tensorflow
        datasets slices.

        A slice consist of a `start` and an `end` separated by a semi-colon
        wrapped in square brackets. The `start` and `end` are integers,
        optionally followed by a percent sign. If the percent sign is omitted,
        the number indicates a row number. If the percent sign is present, the
        number indicates a proportion of a the dataset to select, the number of
        rows is rounded to the closest lower integer.

        Similar to python slices, an empty `start` value is considered to be the
        first row and an empty `end` value is considered to be the last row.


        >>> sarus_ds.split("[10:40]")  # select rows 10 to 39
        >>> sarus_ds.split("[10:70%]")  # select the first 70% rows but skip
        the first 10 rows
        >>> sarus_ds.split("[:-100]")  # select all but the last 100 rows

        Args:
            split (str): specifies the portion of the dataset to select.

        Returns:
            Dataset: the selected split as a `Dataset`.

        """
        split_list = [split] if isinstance(split, str) else split
        split_pattern = r"^\[(?P<start>|-?\d+%?):(?P<end>|-?\d+%?)\]$"
        split_re = re.compile(split_pattern)

        out_datasets = []
        for spl in split_list:
            match = split_re.match(spl)
            if match is None:
                raise ValueError(
                    f"Could not match the split pattern {spl}. "
                    "Expected pattern is `[start(%):end(%)]`."
                )

            # Get start and end rows
            start_str, end_str = match.group("start"), match.group("end")
            if self.marginals is None:
                raise ValueError("Cannot split dataset as marginals is None.")
            ds_size = int(self.marginals["rows"])
            if start_str == "":
                start = 0
            else:
                num = (
                    int(start_str[:-1]) * ds_size // 100
                    if start_str.endswith("%")
                    else int(start_str)
                )
                start = ds_size + num if num < 0 else num

            if end_str == "":
                end = ds_size
            else:
                num = (
                    int(end_str[:-1]) * ds_size // 100
                    if end_str.endswith("%")
                    else int(end_str)
                )
                end = ds_size + num if num < 0 else num

            # Check consistency
            if start >= end:
                raise ValueError(
                    f"Start ({start}) is greater that end ({end}) "
                    f"in split {spl}"
                )
            if start < 0:
                raise ValueError(
                    f"Start ({start}) is lower that 0 " f"in split {spl}"
                )
            if end > ds_size:
                raise ValueError(
                    f"End ({end}) is greater that the dataset size ({ds_size}) "
                    f"in split {spl}"
                )

            split_transform = ("split", {"start": start, "end": end})
            out_datasets.append(self._add_transform(split_transform))

        if isinstance(split, str):
            return out_datasets[0]
        else:
            return out_datasets

    @property
    def features(self) -> Optional[Dict[str, Dict]]:
        """Features and metadata for the `Dataset`.

        Returns:
            Dict[str, Dict]: a dictionary holding metadata where each key
            is a feature.
        """
        if self.type_metadata is None:
            return None
        features: Dict[str, Dict] = self.type_metadata["features"]
        return features

    def __repr__(self) -> str:
        return f"<Sarus Dataset slugname={self.name} id={self.id}>"

    def as_tensorflow(self) -> SarusTensorflowDataset:
        """Return the corresponding `SarusTensorflowDataset` object.

        This allows to manipulate the Sarus `Dataset` as a Tensorflow dataset.

        Returns:
            SarusTensorflowDataset
        """
        return SarusTensorflowDataset(self)

    @classmethod
    def _from_dict(cls, data: dict, client: "Client") -> "Dataset":
        """Get a dataset from the json data sent by the server.

        Args:
            data (dict): json data returned by the server

            client (Client): client used to get information from the server

        Returns:
            Dataset
        """
        return cls(
            data.get("name"),
            data.get("id"),
            client,
            type_metadata=data.get("type_metadata"),
            marginals=data.get("marginals"),
            URI=data.get("URI"),
            human_description=data.get("human_description"),
        )

    @property
    def epsilon(self) -> float:
        """Retrieve the current value of epsilon from the gateway.

        Returns:
            float: current epsilon value
        """
        resp = self.client.session.get(
            f"{self.client.base_url}/datasets/{self.id}",
        )
        if resp.status_code > 200:
            raise Exception(
                f"Error while retrieving the current value of epsilon. "
                f"Gateway answer was: \n{resp}"
            )
        return float(resp.json()["accesses"][0]["current_epsilon"])

    @property
    def max_epsilon(self) -> float:
        """Retrieve the current value of maximum epsilon from the gateway.

        Returns:
            float: maximum authorized epsilon per privacy policy
        """
        resp = self.client.session.get(
            f"{self.client.base_url}/datasets/{self.id}",
        )
        if resp.status_code > 200:
            raise Exception(
                f"Error while retrieving the current value of epsilon. "
                f"Gateway answer was: \n{resp}"
            )
        return float(resp.json()["accesses"][0]["max_epsilon"])

    def _fetch_synthetic(
        self,
        rows_number: Optional[int] = None,
        force_refresh: bool = False,
        original: bool = True,
    ) -> pa.Table:
        """Return synthetic data as a pyarrow.Table.

        Downloads them if they are not in memory yet or if more rows are
        required.

        Args:
            rows_number (int, optional): number of rows to return
            force_refresh (bool): if True, always fetch from server
            original (bool): if False, get categorical values as integers

        Returns:
            pyarrow.Table: synthetic data
        """
        # Synthetic data has been downloaded
        has_synthetic = (
            self._synthetic is not None
            and self._synthetic_rows_number is not None
        )
        # Enough synthetic data has been downloaded
        if rows_number:
            has_enough_synthetic = (
                has_synthetic and rows_number <= self._synthetic_rows_number
            )
        else:
            has_enough_synthetic = has_synthetic

        if not has_enough_synthetic or force_refresh:
            # Define number of rows to fetch
            if self._synthetic_rows_number is None or rows_number is not None:
                self._synthetic_rows_number = rows_number
            # Define request parameters
            params = {"textual_categories": original}
            if self._synthetic_rows_number is not None:
                params["rows_number"] = self._synthetic_rows_number
            # Fetch synthetic data
            resp = self.client.session.get(
                f"{self.client.base_url}/synthetic_data/{self.id}",
                stream=True,
                params=params,
            )
            if resp.status_code > 200:
                raise Exception(
                    f"Error while retrieving synthetic data. "
                    f"Gateway answer was: \n{resp}"
                )

            self._synthetic = pq.ParquetFile(io.BytesIO(resp.content)).read()
        return self._synthetic

    def _synthetic_as_pd_dataframe(
        self,
        rows_number: Optional[int] = None,
        force_refresh: bool = False,
        original: bool = True,
    ):
        """Return synthetic data as a pandas.DataFrame.

         Args:
            rows_number (int, optional): number of rows to return
            force_refresh (bool): if True, always fetch from server
            original (bool): if False, get categorical values as integers

        Returns:
            pandas.DataFrame: synthetic data
        """
        synthetic_data = self._fetch_synthetic(
            rows_number=rows_number,
            force_refresh=force_refresh,
            original=original,
        )

        synthetic_df = synthetic_data.to_pandas().iloc[:rows_number]

        # Convert images encoded as bytes to 3d arrays
        for feature in self.features:
            dtype = list(feature["type"].keys())[0]
            if dtype == "image":
                synthetic_df[feature["name"]] = synthetic_df[
                    feature["name"]
                ].map(Dataset.decode_image)

        return synthetic_df

    @staticmethod
    def _sarus_features_to_tf_spec(
        features: Dict[str, Any],
    ) -> Dict[str, tf.TensorSpec]:
        """Convert Sarus features to Tensorflow spec."""
        mapping = {
            "categorical": tf.int16,
            "boolean": tf.bool,
            "integer": tf.int32,
            "real": tf.float32,
            "text": tf.string,
            "datetime": tf.int64,
            "image": tf.int16,
        }

        def get_tensorspec(feature) -> tf.TensorSpec:
            """Return the tensorflow spec of a Sarus feature."""
            feature_type = list(feature["type"].keys())[0]
            dtype = mapping[feature_type]
            if feature_type == "image":
                width = feature["type"]["image"]["shape"]["x"]
                height = feature["type"]["image"]["shape"]["y"]
                channels = feature["type"]["image"]["shape"]["z"]
                shape = (None, width, height, channels)
            else:
                shape = (None,)
            return tf.TensorSpec(dtype=dtype, shape=shape)

        return {
            feature["name"]: get_tensorspec(feature) for feature in features
        }

    @staticmethod
    def decode_image(serialized_image: bytes) -> np.ndarray:
        # Need to be careful when decoding images with PIL while encoding with
        # OpenCV. See https://stackoverflow.com/questions/58861577/differences-between-pil-image-open-and-cv2-imdecode
        image = Image.open(io.BytesIO(serialized_image))
        return np.atleast_3d(image)

    @staticmethod
    def _adapt_for_tf(
        batch: Dict[str, Any],
        features: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Convert python data to tensorflow compatible data.

        Convert datetime.datetime to nanoseconds.
        Convert images serialized as bytes by petastorm to 3d arrays.
        """
        for feature in features:
            dtype = list(feature["type"].keys())[0]
            if dtype == "datetime":

                def decode_datetime(datetime_value: datetime.datetime) -> int:
                    return datetime_value.timestamp() * int(1e9)

                batch[feature["name"]] = list(
                    map(decode_datetime, batch[feature["name"]])
                )
            elif dtype == "image":
                batch[feature["name"]] = list(
                    map(Dataset.decode_image, batch[feature["name"]])
                )
        return batch

    def _synthetic_as_tf_dataset(
        self,
        batch_size: int,
        rows_number: Optional[int] = None,
        force_refresh: bool = False,
    ) -> tf.data.Dataset:
        """Return synthetic data as a tensorflow.data.Dataset.

        Args:
            batch_size (int): size of the batches in the dataset
            rows_number (int): number of rows in the dataset
            force_refresh (bool): if True, always fetch from server

        Returns:
            tensorflow.data.Dataset: synthetic data
        """
        # Refresh synthetic data
        self._fetch_synthetic(
            force_refresh=force_refresh,
            original=False,
            rows_number=rows_number,
        )

        # Generator function iterating pyarrow RecordBatches
        def generator() -> Dict[str, List[Any]]:
            synthetic_table = self._fetch_synthetic(original=False)
            synthetic_table = synthetic_table.slice(length=rows_number)
            for batch in synthetic_table.to_batches(max_chunksize=batch_size):
                yield Dataset._adapt_for_tf(
                    batch=batch.to_pydict(),
                    features=self.features,
                )

        tf_signature = Dataset._sarus_features_to_tf_spec(self.features)

        return tf.data.Dataset.from_generator(
            generator, output_signature=tf_signature
        )

    def _plot_marginal_feature(
        self,
        marginal_feature: Dict[str, Any],
        width: float = 1.5,
        heigth: float = 1.5,
    ) -> Optional[str]:
        if "statistics" not in marginal_feature:
            return None

        # text-based representations
        # count for categories
        distrib = marginal_feature["statistics"].get("distribution")
        if distrib:
            html_response = ""
            distrib_s = sorted(distrib, key=lambda x: -x["probability"])
            if len(distrib_s) > 5:
                others_count = len(distrib_s) - 5
                others_sum = sum([x["probability"] for x in distrib_s[5:]])
                distrib_s = distrib_s[0:5]
                distrib_s.append(
                    {
                        "name": f"Other ({others_count})",
                        "probability": others_sum,
                        "class_other": "True",
                    }
                )
            for item in distrib_s:
                html_response += "<div><div class='category "
                if "class_other" in item:
                    html_response += "other"
                html_response += f"''>\
                    {item['name']}\
                  </div>\
                  <div class='number'> {round(100*item['probability'],2)}%\
                  </div>\
                 </div>"
            return html_response

        # Graph-based representation
        _ = plt.figure(figsize=(width, heigth))
        # cumulDistribution for real
        cumul = marginal_feature["statistics"].get("cumulativeDistribution")
        if cumul:
            try:
                plt.fill_between(
                    [vp["value"] for vp in cumul],
                    [vp["probability"] for vp in cumul],
                )
            except Exception:
                pass
        fi = io.BytesIO()
        plt.tight_layout()
        plt.savefig(fi, format="svg")
        plt.clf()
        svg_dta = fi.getvalue()  # this is svg data
        return svg_dta.decode()

    def _to_html(self, display_type: bool = False) -> str:
        """Return a HTML representation of this dataset.

        To be displayedin a Notebook for example.
        We'd like to render something like: https://www.kaggle.com/fmejia21/
        demographics-of-academy-awards-oscars-winners

        Args:
            display_type (bool): if True, display each column type in the html

        Returns:
            str: HTML representation of the dataset
        """
        css = """<style>
        @import url('https://rsms.me/inter/inter.css');
        @supports (font-variation-settings: normal) {
            html {font-family: 'Inter var', sans-serif; }
            table {font-size: 12px; border-collapse: collapse;}
            td, th {
                border: 1px solid rgb(222, 223, 224);
                font-weight: 500;
                color: rgba(0,0,0,0.7);
                padding: 8px;
                vertical-align:top;
                }
            tr.desc>td>div {
                display: flex; width: 140px;
                flex-wrap: wrap;
                justify-content: space-between;
            }
            tr.desc>td {
                border-bottom-width: 4px;
                }
            div.category {
                width: 70px;
                padding: 4px;
                margin-bottom: 4px;
                color: black;
                }
            div.number {
                padding: 4px;
                margin-bottom: 4px;
                color: rgb(0, 138, 188);
                text-align: right;
            }
            td>div:hover {
                background-color: rgba(0,0,0,0.03);
              }
            tr.synthetic {
                font-family: 'Roboto Mono', Monaco, Consolas, monospace;
              }
            tr.synthetic>td {
                padding: 8px 4px;
                color: rgba(0, 0, 0, 0.7);
              }
            div.other {color: rgba(0, 0, 0, 0.4);!important}
         </style>"""

        table = "<table>\
                <thead><tr>\n"
        if self.type_metadata is None:
            raise ValueError(
                "The dataset has no type_metadata, may be pending..."
            )
        try:
            columns = self.type_metadata["features"]
        except Exception:
            raise Exception(
                "Dataset does not have proper typing yet. Maybe pending..."
            )
        for c in columns:
            table += f"<th>{c['name']}</th>\n"

        table += """</thead></tr>
                <tbody>
                <tr class='desc'>"""
        if self.marginals is None:
            raise ValueError(
                "The dataset has no marginals yet, may be pending..."
            )
        try:
            for c in self.marginals["features"]:
                table += f"<td>{self._plot_marginal_feature(c)}</td>\n"
        except Exception:
            raise Exception(
                "Dataset does not have proper marginals yet. Maybe pending..."
            )
        table += "</tr><tr>"
        if display_type:
            for c in columns:
                table += f"<td>{c['type']}</td>\n"

        table += "</tr></tbody></table>"

        return f"<html>{css}<body>\n \
                   {table}\
                 </body></html>"

    def _synthetic_to_html(
        self, rows_number: int = None, force_refresh: bool = False
    ) -> str:
        """Return synthetic data as html.

        Args:
            rows_number (int): number of rows to display

            force_refresh (bool): if True, does not use cached synthetic data

        Returns:
            str: HTML representation of the synthetic data
        """
        synthetic: pd.DataFrame = self._synthetic_as_pd_dataframe(
            rows_number=rows_number, force_refresh=force_refresh
        )
        image_cols = [
            f["name"]
            for f in self.type_metadata["features"]
            if "image" in f["type"]
        ]

        def _image_formatter(im):
            memfile = BytesIO(im)
            img_array = np.load(memfile)
            if img_array.shape[2] == 1:
                img_array = img_array.reshape(
                    img_array.shape[0], img_array.shape[1]
                )
            image_from_array = Image.fromarray(img_array)
            buffered = BytesIO()
            image_from_array.save(buffered, format="png")
            return (
                f'<img src="data:image/png;base64,'
                f'{base64.b64encode(buffered.getvalue()).decode()}">'
            )

        return synthetic.to_html(
            formatters={c: _image_formatter for c in image_cols},
            escape=False,
        )


class Client:
    """A class representing the connection with a Sarus server."""

    def _url_validator(self, url):
        """URL validator.

        From https://stackoverflow.com/questions/7160737/
        python-how-to-validate-a-url-in-python-malformed-or-not
        """
        regex = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|"
            r"[A-Z0-9-]{2,}\.?)|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return re.match(regex, url) is not None

    def __init__(
        self,
        url="http://0.0.0.0:5000",
        google_login=False,
        username=None,
        email=None,
        password=None,
        verify=True,
    ):
        # verify: if False, doesn't check SSL certificate if protocol is https
        # TODO : progress bar self.progress_bar = Progbar(100,
        # stateful_metrics=None)

        if self._url_validator(url):
            self.base_url = url
        else:
            raise Exception("Bad url")
        self.session = Session()
        self.session.verify = verify
        if google_login:
            self._oidc_login()
        else:
            self._credentials_login(username, email, password)

    def _oidc_login(self):
        oidc_login_url = f"{self.base_url}/oidc_login?headless=true"
        try:
            from IPython.display import Javascript, clear_output

            display(  # noqa: F821
                Javascript(f'window.open("{oidc_login_url}");')
            )
            display(clear_output())  # noqa: F821
        except Exception:
            webbrowser.open(oidc_login_url)
        token = getpass.getpass(
            "Logging in via google.\nYou will be redirected to a login page "
            "where you will obtain a token to paste below.\nIf you are not "
            f"redirected automatically, you can visit {oidc_login_url}\n"
        )
        self.session.cookies.set(
            "session", base64.b64decode(token).decode("ascii")
        )
        # just to check that the login is successful
        try:
            self._available_datasets()
        except Exception:
            raise Exception("Error during login: incorrect token")

    def _credentials_login(self, username=None, email=None, password=None):
        if username is not None and email is not None:
            raise ValueError(
                "You shall only specify username or email not both"
            )

        credentials = {}

        if username is not None:
            credentials["username"] = username
        elif email is not None:
            credentials["email"] = email
        else:
            raise ValueError("You should specify username or email")

        if password is not None:
            credentials["password"] = password
        else:
            credentials["password"] = getpass.getpass(
                prompt="Password: ", stream=None
            )

        response = self.session.post(
            f"{self.base_url}/login",
            json=credentials,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 401:
            raise ValueError("Error during login: incorrect credentials")

        # Let `requests` handle unexpected HTTP status codes.
        response.raise_for_status()

    def _available_datasets(self) -> List[str]:
        """List available datasets.

        Returns:
            List[str]: list of available dataset names
        """
        request = self.session.get(f"{self.base_url}/datasets")
        return [ds["name"] for ds in request.json()]

    def list_datasets(self) -> List[Dataset]:
        """List available datasets.

        Returns:
            List[str]: list of available dataset names
        """
        dataset_names = self._available_datasets()
        return sorted(
            map(lambda x: self.dataset(slugname=x), dataset_names),
            key=lambda x: x.name,
        )

    def dataset(self, slugname: str = None, id: int = None) -> Dataset:
        """Fetch a dataset from the Sarus Gateway.

        Either `name` or `id` should be provided. If both are provided, then
        only the `name` is considered.

        Args:
            name (str): the name of the Dataset to fetch
            id (int): the id of the Dataset to fetch.

        Returns:
            Dataset: the fetched Sarus Dataset.

        """
        if slugname:
            return self._fetch_dataset_by_name(slugname)
        else:
            return self._fetch_dataset_by_id(id)

    def _fetch_dataset_by_id(self, id: int) -> Dataset:
        """Fetch a dataset from the Sarus Gateway.

        Args:
            id (int): id of the dataset to be fetched

        Returns:
            an instance of Dataset
        """
        try:
            request = self.session.get(f"{self.base_url}/datasets/{id}")
            dataset = Dataset._from_dict(request.json(), self)
            return dataset
        except Exception:
            raise Exception("Dataset not available")

    def _fetch_dataset_by_name(self, name: str) -> Dataset:
        """Fetch a dataset from the Sarus Gateway.

        Args:
            name (string): name of the dataset to be fetched

        Returns:
            Dataset: an instance of Dataset
        """
        try:
            request = self.session.get(
                f"{self.base_url}/datasets/name/{name}",
            )
            dataset = Dataset._from_dict(request.json(), self)
            return dataset
        except Exception:
            raise Exception("Dataset not available")

    def query(
        self, query: str, target_epsilon: float = 0.0, verbose: bool = True
    ) -> int:
        """Launch remotely an SQL query.

        Args:
            query (String): SQL query

            target_epsilon (float): If set, we stop the training when this
                value is reached

        Returns:
            int: Id of the task
        """
        request = self.session.post(
            f"{self.base_url}/query",
            json={
                "query": query,
                "target_epsilon": target_epsilon,
            },
        )
        if request.status_code > 200:
            if request.status_code == 403:
                raise ValueError(
                    "Query failed with the following error: Privacy budget "
                    "limit exceeded"
                )
            if request.status_code == 404:
                raise ValueError(
                    "Couldn't run the query: wrong table name or unauthorised "
                    "access"
                )
            raise Exception(
                f"Error while sending a query.\
                             Full Gateway answer was:{request}"
            )
        task_id = request.json()["task"]
        dataset_id = request.json()["dataset"]["id"]
        start_eps = request.json()["dataset"]["accesses"][0]["current_epsilon"]
        status = self._poll_query_status(task_id)
        error_message = status.get("error_message", None)
        if error_message is not None:
            raise RuntimeError(
                f"Query failed with the following error:\n"
                f"{textwrap.indent(error_message, '  |')}"
            )
        if verbose:
            ds = self._fetch_dataset_by_id(dataset_id)
            print(
                f"Actual privacy consumption (epsilon): "
                f"{ds.epsilon-start_eps:.03f}"
            )
        return status

    def _fit(
        self,
        transform_def: Callable,
        keras_model_def: Callable,
        x: Dataset = None,
        target_epsilon: float = 0,
        batch_size: int = 64,
        non_DP_training: bool = False,
        dp_l2_norm_clip: Optional[float] = None,
        dp_noise_multiplier: Optional[float] = None,
        dp_num_microbatches: Optional[int] = None,  # default: batch size
        seed: Optional[int] = None,
        verbose: bool = True,
        wait_for_completion: bool = True,
        use_old_fit_method: bool = False,
        **kwargs,
    ) -> int:
        """Launch remotely the training of a model, passed in keras_model_def.

        Args:
            transform_def (callable): transform function
            keras_model_def (callable): function returning the model to train
            x (Dataset): dataset used for training
            target_epsilon (float): If set, we stop the training when this
                value is reached
            batch_size (int): batch size
            non_DP_training (bool): if True, we trigger an additional training
                without DP, to compare performances (the resulting model is NOT
                returned)
            dp_l2_norm_clip (float): max value used to clip the gradients
                during DP-SGD training
            dp_noise_multiplier (float): noise multiplier for DP-SGD
            dp_num_microbatches (int): Number of microbatches (by default,
                equal to batch_size, so we get microbatches of size 1)
            seed (int): The seed to used for resetting any random generators
                prior to the training of the model.
            verbose (bool): if True, prints privacy info at the end
                of the model training
            wait_for_completion (bool): if True waits until the model training
                is finished to return (and displays progress info while waiting)
            use_old_fit_method (bool, default True): Whether to use legacy fit method backend (for testing purposes).
            **kwargs: other kwargs to pass to tensorflow Model.fit() function

        Returns:
            int: Id of the task
        """
        # for retro-compatibility, if y is set, delete it
        if "y" in kwargs:
            del kwargs["y"]
        if (
            dp_num_microbatches is not None
            and batch_size % dp_num_microbatches != 0
        ):
            raise ValueError(
                f"batch_size should be a multiple of dp_num_microbatches, "
                f"got {batch_size} and {dp_num_microbatches}"
            )

        # set the seed
        if seed is not None:
            tf.random.set_seed(seed)

        model: Model = keras_model_def()
        # learn input/output shapes by running predict on the first line of
        #  synthetic data (shapes required to use the SavedModel format)

        # TODO improve when single format is used
        if transform_def:
            model.predict(
                transform_def(
                    x._synthetic_as_tf_dataset(batch_size),
                    features=x.type_metadata["features"],
                ).take(1)
            )
        else:
            model.predict(x._synthetic_as_tf_dataset(batch_size).take(1))

        if verbose:
            print("Uploading the Keras model")
        saved_model = _save_model(model)
        keras_model_resp = self.session.post(
            f"{self.base_url}/tasks_input_blobs",
            data=saved_model,
        )
        if keras_model_resp.status_code > 200:
            raise Exception(
                "Error while uploading the Keras model."
                f"Full Gateway answer was:{keras_model_resp}"
            )
        keras_model_id = keras_model_resp.json()["id"]

        start_eps = x.epsilon

        # WARNING pickled functions require exactly same Python version b/w
        # sender and receiver (currently it is 3.6)
        if verbose:
            print("Uploading the transform definition")
        serialized_transform_def = cloudpickle.dumps(transform_def)
        transform_def_resp = self.session.post(
            f"{self.base_url}/tasks_input_blobs",
            data=serialized_transform_def,
        )
        if transform_def_resp.status_code > 200:
            raise Exception(
                "Error while uploading the transform definition"
                f"Full Gateway answer was:{transform_def_resp}"
            )
        transform_def_id = transform_def_resp.json()["id"]

        fit_endpoint = "fit"

        if use_old_fit_method:
            fit_endpoint = "fit_v1"

        request = self.session.post(
            f"{self.base_url}/{fit_endpoint}",
            json={
                "transform_def_id": transform_def_id,
                "keras_model_id": keras_model_id,
                "x_id": x.id,
                "target_epsilon": target_epsilon,
                "non_DP_training": non_DP_training,
                "batch_size": batch_size,
                "dp_l2_norm_clip": dp_l2_norm_clip,
                "dp_noise_multiplier": dp_noise_multiplier,
                "dp_num_microbatches": dp_num_microbatches,
                "seed": seed,
                "verbose": verbose,
                "wait_for_completion": wait_for_completion,
                **kwargs,
            },
        )
        if request.status_code > 200:
            if request.status_code == 403:
                raise ValueError(
                    "Query failed with the following error: Privacy budget "
                    "limit exceeded"
                )
            raise Exception(
                f"Error while training the model.\
                             Full Gateway answer was:{request}"
            )
        task_id = request.json()["task"]
        if wait_for_completion:
            print(f"Fit launched. Task id: {task_id}")
            status = self._poll_training_status(task_id)
            error_message = status.get("error_message", None)
            if error_message is not None:
                raise RuntimeError(
                    f"Training failed with the following error:\n"
                    f"{textwrap.indent(error_message, '  |')}"
                )
            if verbose:
                print(
                    f"Actual privacy consumption (epsilon): "
                    f"{x.epsilon-start_eps:.03f}"
                )
        return task_id

    def _abort_training(self, id: int):
        """Abort a training on the Sarus Gateway.

        Args:
            id (int): id of the task to abort (provided by the fit method).
        """
        resp = self.session.delete(
            f"{self.base_url}/training_tasks/{id}/abort",
        )
        if resp.status_code != 204:
            raise Exception(
                f"Error while trying to abort task:\n{resp.content}"
            )

    def _training_status(self, id: int) -> dict:
        """Fetch a dataset from the Sarus Gateway.

        Args:
            id (int): id of the task to be queried. It was provided by the fit
            method

        Returns:
            dict: a dict with the status of a training tasks
        """
        request = self.session.get(
            f"{self.base_url}/training_tasks/{id}",
        )
        return request.json()

    def _poll_training_status(self, id: int, timeout: int = 1000) -> dict:
        """Poll & display the status of a training task.

        Args:
            id (int): id of the task to be queried. It was provided by the fit
            method

            timeout (int): in seconds

        Returns:
            dict: The training status at the end of the task

        Raises:
            TimeoutError: if timeout is reached before the training finishes
        """
        offset = 0
        elapsed_time = 0.0
        while elapsed_time < timeout:
            elapsed_time += 0.5
            request = self.session.get(
                f"{self.base_url}/training_tasks/{id}",
                params=dict(offset=offset),
            )
            response_dict = request.json()
            offset = response_dict.get("next_offset", 0)
            if "progress" in response_dict:
                progress = base64.b64decode(
                    response_dict["progress"].encode("ascii")
                ).decode("ascii")
                if progress:
                    sys.stdout.write(progress)
            else:
                # this is the end of the training
                sys.stdout.write("\n")
                return response_dict
            sys.stdout.flush()
            time.sleep(0.5)
        raise TimeoutError(
            "Timeout reached while waiting for the model training to finish."
        )

    def _poll_query_status(self, id: int, timeout: int = 1000) -> dict:
        """Poll & display the status of a query task.

        Args:
            id (int): id of the task to be queried. It was provided by the fit
            method

            timeout (int): in seconds

        Returns:
            dict: The query status at the end of the task

        Raises:
            TimeoutError: if timeout is reached before the query finishes
        """
        offset = 0
        elapsed_time = 0.0
        while elapsed_time < timeout:
            elapsed_time += 0.5
            request = self.session.get(
                f"{self.base_url}/query_tasks/{id}",
                params=dict(offset=offset),
            )
            response_dict = request.json()
            status = response_dict["status"]
            if status != "PENDING":
                return response_dict
            time.sleep(0.5)
        raise TimeoutError(
            "Timeout reached while waiting for the model training to finish."
        )

    def _fetch_model(self, id: int) -> tf.keras.Model:
        """Fetch a trained model from the Sarus Gateway.

        Args:
            id (int): id of the task to be queried. It was provided by the fit
                method

        Returns:
            tf.keras.Model: a Keras model
        """
        response = self.session.get(
            f"{self.base_url}/models/{id}",
        )
        # apparently we need to save to a temp file
        # https://github.com/keras-team/keras/issues/9343
        with tempfile.TemporaryDirectory() as _dir:
            f = tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz")
            f.extractall(_dir)

            return tf.keras.models.load_model(_dir)


def _save_model(model: tf.keras.Model) -> bytes:
    """Convert a keras Model to compressed archive format."""
    with tempfile.TemporaryDirectory() as _dir:
        model.save(_dir)
        with tempfile.TemporaryDirectory() as _second_dir:
            path = os.path.join(_second_dir, "tmpzip")
            with tarfile.open(path, mode="w:gz") as archive:
                archive.add(_dir, recursive=True, arcname="")
            with open(path, "rb") as f:
                ret = f.read()
                return ret
