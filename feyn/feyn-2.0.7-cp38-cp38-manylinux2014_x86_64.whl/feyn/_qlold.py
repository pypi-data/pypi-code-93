"""Classes and functions to interact with a remote QLattice."""
from os import cpu_count
from typing import Dict, List, Optional, Set, Iterable, Union, Callable

import _feyn
import numpy as np
import requests
from pandas import DataFrame

import feyn
from feyn import Model
from feyn._typings import check_types
from feyn.losses import _get_loss_function
from ._config import DEFAULT_SERVER, Config
from ._httpclient import HttpClient
from ._register import RegisterCollection
from feyn._validation import validate_data

class QLOld:
    """Class for representing a remote QLattice connection."""

    def __init__(self, cfg: Config):
        """Construct a new 'QLattice' object."""
        headers = {
            "Authorization": f'Bearer {cfg.api_token or "none"}',
            "User-Agent": f"feyn/{feyn.__version__}",
        }

        self._qlattice_id = cfg.qlattice
        self._qlattice_server = cfg.server.rstrip("/")
        api_base_url = f"{self._qlattice_server}/api/v1/qlattice/{self._qlattice_id}"
        self._http_client = HttpClient(api_base_url, headers)

        self._load_qlattice()

        self._registers = RegisterCollection(self)

    def __repr__(self):
        return "<Abzu QLattice[%i,%i] '%s'>" % (
            self.width,
            self.height,
            self._http_client.api_base_url,
        )


    @property
    def registers(self):
        """
        The RegisterCollection of the QLattice

        The RegisterCollection is used to find, create and remove registers from the QLattice.
        """
        return self._registers

    @check_types()
    def sample_models(
        self,
        input_names: Iterable[str],
        output_name: str,
        kind: str = "regression",
        stypes: Optional[Dict[str, str]] = None,
        max_complexity: int = 10,
        query_string: Optional[str] = None,
        function_names: Optional[List[str]] = None,
    ) -> List[Model]:
        """
        Sample models from the QLattice simulator. The QLattice has a probability density for generating different models, and this function samples from that density.

        Arguments:
            input_names {List[str]} -- The names of the input features.
            output_name {str} -- The name of the output feature.

        Keyword Arguments:
            kind {str} -- Specify the kind of models that are sampled. One of ["classification", "regression"]. (default: {"regression"})
            stypes {Optional[Dict[str, str]]} -- An optional map from feature names to semantic types. (default: {None})
            max_complexity {int} -- The maximum complexity for sampled models. Currently the maximum number of edges that the graph representation of the models has. (default: {10})
            query_string {Optional[str]} -- An optional query string for specifying specific model structures. (default: {None})
            function_names {Optional[List[str]]} -- A list of function names to use in the QLattice simulation. Defaults to all available functions being used. (default: {None})

        Raises:
            TypeError: if inputs don't match the correct type.
            ValueError: if input_names contains duplicates.
            ValueError: if max_complexity is negative.
            ValueError: if kind is not a regressor or classifier.
            ValueError: if function_names is not recognised.

        Returns:
            List[Model] -- The list of sampled models.
        """

        if len(input_names) == 0:
            raise ValueError("input_names cannot be empty.")
        if len(list(input_names)) != len(set(input_names)):
            raise ValueError("input_names must consist of only unique values.")
        if max_complexity <= 0:
            raise ValueError(
                f"max_complexity must be greater than 0, but was {max_complexity}."
            )

        stypes = stypes or {}
        stypes[output_name] = _kind_to_output_stype(kind)

        if output_name not in input_names:
            input_names = [*input_names, output_name]

        regmap = {}
        for reg in input_names:
            stype = stypes.get(reg, "f")

            if stype in ["cat", "categorical"]:
                stype = "c"
            if stype in ["float", "numerical"]:
                stype = "f"
            if stype in ["bool"]:
                stype = "b"
            if reg == output_name:
                pattern = f"out:*(*)->{stype}"
            else:
                pattern = f"in:*({stype})->*"

            regmap[reg] = pattern

        if function_names:
            specs = _build_spec_list(function_names)
        else:
            specs = _feyn.get_specs()

        models_json = self._generate(specs, regmap, max_complexity, query_string or "")
        return list(
            filter(
                lambda m: m.edge_count <= max_complexity, _models_from_json(models_json)
            )
        )

    @check_types()
    def update(self, models: Union[Model, Iterable[Model]]) -> None:
        """Update QLattice with learnings from a list of models. When updated, the QLattice learns to produce models that are similar to what is included in the update. Without updating, the QLattice will keep generating models with a random structure.

        Arguments:
            models {Union[Model, Iterable[Model]]} -- The models to use in a QLattice update.

        Raises:
            TypeError: if inputs don't match the correct type.
        """

        if isinstance(models, Model):
            models = [models]

        resp = self._http_client.post(
            "/update", json={"graphs": [m._to_dict() for m in models]}
        )

        resp.raise_for_status()

    def reset(self, random_seed: int = -1) -> None:
        """Clear all learnings in this QLattice.

        Keyword Arguments:
            random_seed {int} -- If not -1, seed the qlattice and feyn random number generator to get reproducible results. (default: {-1})
        """
        req = self._http_client.post("/reset", json={"seed": random_seed})
        req.raise_for_status()

        if random_seed != -1:
            np.random.seed(random_seed)
            _feyn.srand(random_seed)

        self._load_qlattice()

    @check_types()
    def auto_run(
        self,
        data: DataFrame,
        output_name: str,
        kind: str = "regression",
        stypes: Optional[Dict[str, str]] = None,
        n_epochs: int = 10,
        threads: Union[int, str] = "auto",
        max_complexity: int = 10,
        query_string: Optional[str] = None,
        loss_function: Optional[Union[str, Callable]] = None,
        criterion: Optional[str] = None,
        sample_weights: Optional[Iterable[float]] = None,
        function_names: Optional[List[str]] = None,
        starting_models: Optional[List[feyn.Model]] = None,
    ) -> List[feyn.Model]:
        """A convenience function for running the QLattice simulator for many epochs. This process can be interrupted with a KeyboardInterrupt, and you will get back the best models that have been found thus far. Roughly equivalent to the following:

        >>> models = []
        >>> for i in range(n_epochs):
        >>>     models += ql.sample_models(data, output_name, kind, stypes, max_complexity, query_string, function_names)
        >>>     models = feyn.fit_models(models, data, loss_function, criterion, None, sample_weights)
        >>>     models = feyn.prune_models(models)
        >>>     best = feyn.best_diverse_models(models)
        >>>     ql.update(best)

        Arguments:
            data {Iterable} -- The data to train models on. Feature names are inferred from the columns (pd.DataFrame) or keys (dict) of this variable.
            output_name {str} -- The name of the output feature.

        Keyword Arguments:
            kind {str} -- Specify the kind of models that are sampled. One of ["classification", "regression"]. (default: {"regression"})
            stypes {Optional[Dict[str, str]]} -- An optional map from feature names to semantic types. (default: {None})
            n_epochs {int} -- Number of training epochs. (default: {10})
            threads {int} -- Number of concurrent threads to use for fitting. If a number, that many threads are used. If "auto", set to your CPU count - 1. (default: {"auto"})
            max_complexity {int} -- The maximum complexity for sampled models. (default: {10})
            query_string {Optional[str]} -- An optional query string for specifying specific model structures. (default: {None})
            loss_function {Optional[Union[str, Callable]]} -- The loss function to optimize models for. If None (default), 'MSE' is chosen for regression problems and 'binary_cross_entropy' for classification problems. (default: {None})
            criterion {Optional[str]} -- Sort by information criterion rather than loss. Either "aic", "bic" or None. (default: {None})
            sample_weights {Optional[Iterable[float]]} -- An optional numpy array of weights for each sample. If present, the array must have the same size as the data set, i.e. one weight for each sample. (default: {None})
            function_names {Optional[List[str]]} -- A list of function names to use in the QLattice simulation. Defaults to all available functions being used. (default: {None})
            starting_models {Optional[List[feyn.Model]]} -- A list of preexisting feyn models you would like to start finding better models from. The inputs and output of these models should match the other arguments to this function. (default: {None})

        Raises:
            TypeError: if inputs don't match the correct type.

        Returns:
            List[feyn.Model] -- The best models found during this run.
        """
        validate_data(data, kind, output_name, stypes)

        if loss_function is None:
            output_type = _kind_to_output_stype(kind)
            loss_function = _get_loss_function(output_type)

        if threads == "auto":
            found_cpus = cpu_count()
            if found_cpus is None:
                threads = 4
            else:
                threads = found_cpus - 1

        # TODO: Make immutable copy of starting models
        models = starting_models or []
        m_count = len(models)

        try:
            for i in range(n_epochs):
                new_sample = self.sample_models(
                    data,
                    output_name,
                    kind,
                    stypes,
                    max_complexity,
                    query_string,
                    function_names,
                )
                models += new_sample
                m_count += len(new_sample)

                models = feyn.fit_models(
                    models, data, loss_function, criterion, None, sample_weights
                )
                models = feyn.prune_models(models)

                feyn.show_model(
                    models[0],
                    f"Epoch no. {i+1} - Tried {m_count} models - Best loss: {models[0].loss_value:.2e}",
                    update_display=True,
                )

                best = feyn.best_diverse_models(models)
                self.update(best)
            return best
        except KeyboardInterrupt:
            return feyn.best_diverse_models(models)
        except Exception as ex:
            raise ex

    def _generate(
        self,
        specs: List[str],
        registers: Dict[str, str],
        max_complexity: int,
        query_string: str,
    ) -> Dict:
        req = self._http_client.post(
            "/generate",
            json={
                "specs": specs,
                "registers": registers,
                "max_complexity": max_complexity,
                "query": query_string,
            },
        )

        if req.status_code == 422:
            raise ValueError(req.text)

        req.raise_for_status()

        return req.json()

    def _load_qlattice(self):
        req = self._http_client.get("/")

        # The purpose of this special handling is to create a channel for messaging the user about issues that we have somehow
        # failed to consider beforehand.
        if req.status_code == 400:
            raise ConnectionError(req.text)

        req.raise_for_status()

        qlattice = req.json()

        self.width = qlattice["width"]
        self.height = qlattice["height"]

    def _remove_community_qlattice(self):
        # Utility for system testing
        resp = requests.post(
            f"{self._qlattice_server}/api/v1/qlattice/community/delete",
            headers=self._http_client.headers,
            json={"qlattice_id": self._qlattice_id},
            timeout=20,
        )
        resp.raise_for_status()


def _kind_to_output_stype(kind: str) -> str:
    """Parse kind into an output spec for the QLattice."""
    if kind in ["regression", "regressor"]:
        return "f"
    if kind in ["classification", "classifier"]:
        return "b"
    raise ValueError(
        "Model kind not understood. Please choose either a 'regression' or a 'classification'."
    )


def _models_from_json(model_dict: dict) -> Set[Model]:
    nodemap = {node["id"]: node for node in model_dict["nodes"]}

    ## Add the links to the nodes themselves.
    # TODO: Change wire format to avoud this conversion
    for node in nodemap.values():
        node["links"] = [None, None]

    for link in model_dict["links"]:
        source_id = link["source"]
        target_node = nodemap[link["target"]]
        ord_int = int(link["ord"])
        target_node["links"][ord_int] = source_id

    new_models = set()

    out_ids = [n["id"] for n in nodemap.values() if n["spec"].startswith("out:")]
    for out_id in out_ids:
        # The following algorithm builds a 1D array of nodes
        # that preserverves execution order
        nodelist = []
        current = [out_id]
        while len(current) > 0:
            node_id = current.pop(0)
            if node_id in nodelist:
                nodelist.remove(node_id)
            nodelist.insert(0, node_id)

            for pred_id in nodemap[node_id]["links"]:
                if pred_id is not None:
                    current.append(pred_id)

        # Convert the list of ids to a list of nodes
        nodelist = [nodemap[nodeid] for nodeid in nodelist]
        new_models.add(_build_model(nodelist))

    return new_models


def _build_model(nodelist: List[Dict]):
    nodes = []
    links = []
    node_index = {node["id"]: ix for ix, node in enumerate(nodelist)}

    for ix, node in enumerate(nodelist):
        nodes.append(
            {
                "id": ix,
                "spec": node["spec"],
                "location": node["location"],
                "peerlocation": node["location"],
                "name": node["name"],
                "state": {},
            }
        )
        for ordinal, source_id in enumerate(node["links"]):
            if source_id is not None:
                source = node_index[source_id]
                links.append({"source": source, "target": ix, "ord": ordinal})

    return Model._from_dict({"nodes": nodes, "links": links})


def _build_spec_list(fnames: List[str]) -> List[str]:
    """From a list of function names, build a list of specs for the simulator."""
    all_specs = _feyn.get_specs()

    ret = []
    for spec_str in all_specs:
        if spec_str.startswith("in:") or spec_str.startswith("out:"):
            ret.append(spec_str)
        elif _spec_to_fname(spec_str) in fnames:
            ret.append(spec_str)

    for name in fnames:
        if name not in list(map(_spec_to_fname, ret)):
            raise ValueError(f"{name} is not a valid function name.")

    return ret


def _spec_to_fname(spec: str) -> str:
    """Separate a function name from a QLattice spec."""
    return spec.split(":")[1].split("(")[0]
