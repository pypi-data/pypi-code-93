"""Class for a feyn Model. A feyn Model is a composition of mathematical functions from some input features to an output."""

import json
from pathlib import Path
from typing import AnyStr, TextIO, Union, Iterable, Optional, Dict, List

import numpy as np

import _feyn
import feyn

from pandas import DataFrame

from ._base_reporting_mixin import BaseReportingMixin
from ._plots_mixin import PlotsMixin
from ._interactivemixin import InteractiveMixin

from ._compatibility import supports_interactivity

# Update this number whenever there are breaking changes to save/load
# (or to_dict/from_dict). Then use it intelligently in Model.load.
SCHEMA_VERSION = "2020-02-07"

PathLike = Union[AnyStr, Path]


class Model(
    _feyn.Model,
    BaseReportingMixin,
    PlotsMixin,
    InteractiveMixin if supports_interactivity() else object,
):
    """
    A Model represents a single mathematical equation which can be used for predicting.

    The constructor is for internal use.
    """

    def __init__(self, size: int):
        """Construct a new 'Model' object."""
        super().__init__(size)

        self.loss_value = np.nan
        self.age = 0

    # TODO: Typing!
    def predict(self, X: DataFrame) -> np.ndarray:
        """
        Calculate predictions based on input values.

        >>> model.predict({ "age": [34, 78], "sex": ["male", "female"] })
        [True, False]

        Arguments:
            X {DataFrame} -- The input values as a pandas.DataFrame.

        Returns:
            np.ndarray -- The calculated predictions.
        """
        if type(X).__name__ == "dict":
            for k in X:
                if type(X[k]).__name__ == "list":
                    X[k] = np.array(X[k])

        # Magic support for pandas Series
        if type(X).__name__ == "Series":
            X = {idx: np.array([X[idx]]) for idx in X.index}

        # Magic support for pandas DataFrame
        if type(X).__name__ == "DataFrame":
            X = {col: X[col].values for col in X.columns}

        return super()._query(X, None)

    @property
    def edges(self) -> int:
        """Get the total number of edges in the graph representation of this model."""
        return super().edge_count

    @property
    def depth(self) -> int:
        """Get the depth of the graph representation of the model."""
        return self[-1].depth

    @property
    def target(self) -> str:
        """Get the name of the output node. Does the same as 'output'"""
        return self.output

    @property
    def features(self):
        """Get the name of the input features of the model. Does the same as 'inputs'"""
        return self.inputs

    @property
    def output(self) -> str:
        """Get the name of the output node."""
        return self[-1].name

    @property
    def inputs(self):
        """Get the name of the input features of the model."""
        return [i.name for i in self if i.spec.startswith("in:")]

    def save(self, file: Union[PathLike, TextIO]) -> None:
        """
        Save the `Model` to a file-like object.

        The file can later be used to recreate the `Model` with `Model.load`.

        Arguments:
            file -- A file-like object or path to save the model to.
        """
        as_dict = self._to_dict(include_state=True)
        as_dict["version"] = SCHEMA_VERSION

        if isinstance(file, (str, bytes, Path)):
            with open(file, mode="w") as f:
                json.dump(as_dict, f)
        else:
            json.dump(as_dict, file)

    @staticmethod
    def load(file: Union[PathLike, TextIO]) -> "Model":
        """
        Load a `Model` from a file.

        Usually used together with `Model.save`.

        Arguments:
            file -- A file-like object or a path to load the `Model` from.

        Returns:
            Model -- The loaded `Model`-object.
        """
        if isinstance(file, (str, bytes, Path)):
            with open(file, mode="r") as f:
                as_dict = json.load(f)
        else:
            as_dict = json.load(file)

        return Model._from_dict(as_dict)

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return other.__hash__() == self.__hash__()

    def __contains__(self, item: str):
        return item in [interaction.name for interaction in self]

    def fit(self, data: DataFrame, loss_function=_feyn.DEFAULT_LOSS, sample_weights=None):
        """
        Fit this specific `Model` with the given data set.

        Arguments:
            data -- Training data including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.
            loss_function -- Name of the loss function or the function itself. This is the loss function to use for fitting. Can either be a string or one of the functions provided in `feyn.losses`.
            sample_weights -- An optional numpy array of weights for each sample. If present, the array must have the same size as the data set, i.e. one weight for each sample

        """

        # Magic support for pandas DataFrame
        if type(data).__name__ == "DataFrame":
            data = {col: data[col].values for col in data.columns}

        length = len(list(data.values())[0])

        # Create a sequence of indices from the permuted data of length n_samples
        permutation = np.random.permutation(length)
        data = {key: values[permutation] for key, values in data.items()}

        if sample_weights is not None:
            # Normalise the sample_weights
            sample_weights = np.multiply(list(sample_weights), 1 / max(sample_weights))
            # Also permute the sample_weights
            sample_weights = sample_weights[permutation]

        loss_function = feyn.losses._get_loss_function(loss_function)
        if not hasattr(loss_function, "c_derivative"):
            raise ValueError(
                "Loss function cannot be used for fitting, since it doesn't have a corresponding c derivative"
            )

        self._fit(data, loss_function, sample_weights)

    def _fit(self, data, loss_function, sample_weights=None):
        out_reg = self[-1]
        Y = data[out_reg.name]

        out_reg._loss = loss_function.c_derivative

        predictions = super()._query(data, Y, sample_weights)
        losses = loss_function(Y.astype(float), predictions)
        if sample_weights is not None:
            losses *= sample_weights
        self.loss_value = np.mean(losses)

        return self.loss_value

    def _to_dict(self, include_state=False):
        nodes = []
        links = []
        for ix in range(len(self)):
            interaction = self[ix]
            node = {
                "id": interaction._index,
                "spec": interaction.spec,
                "location": interaction._latticeloc,
                "peerlocation": interaction._peerlocation,
                "legs": len(interaction.sources),
                "strength": interaction._strength,
                "name": interaction.name,
            }
            if include_state:
                node["state"] = interaction.state._to_dict()

            nodes.append(node)
            for ordinal, src in enumerate(interaction.sources):
                if src != -1:
                    links.append(
                        {"source": src, "target": interaction._index, "ord": ordinal}
                    )

        return {"directed": True, "multigraph": True, "nodes": nodes, "links": links}


    def _repr_svg_(self):
        return feyn._current_renderer(self)

    def _repr_html_(self):
        return feyn._current_renderer(self)

    @staticmethod
    def _from_dict(mdict):
        sz = len(mdict["nodes"])
        model = Model(sz)
        for ix, node in enumerate(mdict["nodes"]):
            interaction = _feyn.Interaction(
                node["spec"], node["location"], node["peerlocation"], node["name"]
            )
            interaction.state._from_dict(node["state"])
            model[ix] = interaction

        for edge in mdict["links"]:
            interaction = model[edge["target"]]
            ord_int = edge["ord"]
            interaction._set_source(ord_int, edge["source"])
        return model

    def sympify(self, signif: int = 6, symbolic_lr=False, include_weights=True):
        """
        Convert the model to a sympy expression.
        This function requires sympy to be installed.

        Arguments:
            signif -- the number of significant digits in the parameters of the model
            symbolic_lr -- express logistic regression wrapper as part of the expression

        Returns:
            expression -- a sympy expression

        """
        return feyn.tools.sympify_model(
            self,
            signif=signif,
            symbolic_lr=symbolic_lr,
            include_weights=include_weights,
        )

    def _get_string_representation(self) -> str:
        """Gets a string representation of a model, such as 'gaussian(x0, x1)'.

        Returns:
            str -- A string representation of a model
        """
        expressions = []
        for i in self:
            if "in:" in i.spec:
                expressions.append(i.name)
            elif "out:" in i.spec:
                expressions.append(i.name)
            else:
                function = i.spec.split("cell:")[1].split("->")[0]
                if len(i.sources) > 1:
                    function = function.replace("(i,i)", "(__x0__, __x1__)")
                else:
                    function = function.replace("(i)", "(__x0__)")
                expressions.append(function)

        for ix, i in enumerate(self):
            if "in:" in i.spec:
                continue
            elif "out:" in i.spec:
                continue

            if len(i.sources) > 0:
                expressions[ix] = expressions[ix].replace(
                    "__x0__", expressions[i.sources[0]]
                )
            if len(i.sources) > 1:
                expressions[ix] = expressions[ix].replace(
                    "__x1__", expressions[i.sources[1]]
                )

        return expressions[-2]  # Return the node before the output node
