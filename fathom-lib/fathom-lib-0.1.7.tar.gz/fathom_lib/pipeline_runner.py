from typing import Callable, Dict, Hashable, Iterable, List, Tuple

import joblib
from copy import deepcopy
import networkx as nx
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.tree import DecisionTreeClassifier

from fathom_lib.component_autogeneration.sklearn.generate_ui_components import try_numeric
from fathom_lib.component_autogeneration.submodules import import_class
from fathom_lib.datasources import DataFrame
from fathom_lib.transformers.pandasify import Pandasify
from fathom_lib.transformers.sparkify import Sparkify
from fathom_lib.pipeline_data import PipelineData
from fathom_lib.utils import (
    Callback,
    Severity,
    build_graph,
    example_callback,
    extract_data_for_many_edges,
    extract_field,
    extract_unique_edge_outputs,
    iter_edges_data,
)


class Storage:
    def __init__(self):
        self.store = {}

    def save(self, key: Hashable, obj):
        self.store[key] = obj

    def load(self, key: Hashable):
        return self.store[key]

    def load_many(self, keys: Iterable[Hashable]) -> List:
        return [self.load(key) for key in keys]

    def clear(self):
        self.store.clear()


class Transformer(BaseEstimator, TransformerMixin):
    def __init__(self, n):
        self.n = n

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame, y=None):
        return X


class Picklable:
    def save(self, path: str):
        joblib.dump(self, path)

    @staticmethod
    def load(path: str):
        return joblib.load(path)


class PipelineRunner(BaseEstimator, TransformerMixin, Picklable):
    """
    Assumption: there is only 1 data source and only 1 final estimator in which's predictions
    we are interested
    """

    # TODO: make it a legitimate sklearn pipeline so that it can be composed with others
    def __init__(self, nodes: Dict, edges: List[Tuple[str, str]], callback: Callable):
        self.callback = Callback(callback)
        with self.callback(step_type="init runner"):
            self.graph = build_graph(nodes, edges)
            self.storage = Storage()
            if not nx.is_directed_acyclic_graph(self.graph):
                raise ValueError("Constructed graph is not a DAG")

    def fit(self, X, y=None, **fit_params):
        return self._run(X, should_fit_at_each_step=True, method="fit", y_required=True)

    def fit_transform(self, X, y=None, **fit_params):
        return self._run(
            X, should_fit_at_each_step=True, method="fit_transform", y_required=True
        )

    # def fit_predict(self, X, y=None, **fit_params):
    #     return self._run(X, should_fit_at_each_step=True, method="fit_predict", y_required=True)

    def predict(self, X, **predict_params):
        return self._run(
            X, should_fit_at_each_step=False, method="predict", y_required=False
        )

    def predict_proba(self, X, **predict_params):
        return self._run(
            X, should_fit_at_each_step=False, method="predict_proba", y_required=False
        )

    def predict_log_proba(self, X, **predict_params):
        return self._run(
            X,
            should_fit_at_each_step=False,
            method="predict_log_proba",
            y_required=False,
        )

    def _add_params_from_node(self, node_id, pipeline_params, deep):
        cls = self._get_step(node_id)
        cls_params = cls.get_model_params(deep)
        for key, value in cls_params.items():
            pipeline_params[cls._get_model_name() + "_" + node_id + "__" + key] = value

    def get_params(self, deep=True):
        params = {}
        first_node, *middle_nodes, last_node = nx.topological_sort(self.graph)
        for node_id in middle_nodes:
            self._add_params_from_node(node_id, params, deep)
        self._add_params_from_node(last_node, params, deep)
        return params

    def get_most_recent_final_model(self):
        first_node, *middle_nodes, last_node = nx.topological_sort(self.graph)
        return self._get_step(last_node).get_final_model()

    def get_most_recent_data(self):
        first_node, *middle_nodes, last_node = nx.topological_sort(self.graph)
        params = self._collect_method_params(last_node, y_required=True)
        return params["pipeline_data"]

    def _run(self, X, should_fit_at_each_step: bool, method: str, y_required: bool):
        with self.callback(step_type=method):
            self.storage.clear()
            # cannot run a pipeline with less than 2 components
            if len(self.graph.nodes) <= 1:
                return None
            # when it is 2 components assume the second is an estimator
            # TODO: this is perhaps a wrong assumption
            elif len(self.graph.nodes) == 2:
                first_node, last_node = nx.topological_sort(self.graph)
                middle_nodes = []
            else:
                first_node, *middle_nodes, last_node = nx.topological_sort(self.graph)

            with self.callback(step_type="step", node_id=first_node):
                self.initialize_first_node_with_data(
                    X, node_id=first_node, y_required=y_required
                )

            for node_id in middle_nodes:
                with self.callback(step_type="step", node_id=node_id):
                    params = self._collect_method_params(node_id, y_required=y_required)
                    if should_fit_at_each_step:
                        self._get_step(node_id).fit(**params)
                    self._compute_output_data(node_id, params)

            with self.callback(step_type="step", node_id=last_node):
                params = self._collect_method_params(last_node, y_required=y_required)
                last_step = self._get_step(last_node)
                if method == "fit":
                    self._evaluate(last_step, method, params)
                    return self
                elif (
                    method == "predict"
                    or method == "predict_proba"
                    or method == "predict_log_proba"
                ):
                    result = self._evaluate(last_step, method, params)
                    prediction_columns = [
                        col
                        for col in result.data.columns.values
                        if col.startswith(last_step._get_model_name() + ".predict")
                    ]
                    return result.data[prediction_columns]
                else:
                    return self._evaluate(last_step, method, params)

    def _evaluate(self, step, method: str, params: Dict):
        compute_func = getattr(step, method)  # e.g. step.fit_transform
        return compute_func(**params)

    def _compute_output_data(self, node_id, params):
        step = self._get_step(node_id)
        out_edges = self.graph.out_edges(node_id)
        for edge in iter_edges_data(self.graph, out_edges):
            result = self._evaluate(step, "transform", params)
            self.storage.save(key=edge.get("out") + edge.get("in"), obj=result)

    def _get_step(self, node_id):
        """Returns wrapped transformer or estimator associated with given node"""
        return self.graph.nodes[node_id]["step"]

    def initialize_first_node_with_data(self, X, node_id, y_required: bool):
        # TODO: is X a proper name? Better `df`?
        out_edges = sorted(self.graph.out_edges(node_id))  # TODO: is sorted necessary?
        for edge in iter_edges_data(self.graph, out_edges):
            step = self._get_step(node_id)
            if y_required and step.y_columns == []:
                raise KeyError("Y columns must be specified!")
            pipeline_data = PipelineData(
                # TODO: maybe reset index of X here ?
                data=X.copy(),
                X_columns=step.X_columns,
                y_columns=step.y_columns,
                additional_columns=step.additional_columns,
            )
            self.storage.save(key=edge.get("out") + edge.get("in"), obj=pipeline_data)

    def _collect_method_params(self, node_id, y_required: bool):
        params = {}
        in_edges = sorted(
            set(self.graph.in_edges(node_id))
        )  # TODO: is sorted necessary?

        return_data = None
        for edge in iter_edges_data(self.graph, in_edges):
            if return_data == None:
                return_data = deepcopy(
                    self.storage.load(edge.get("out") + edge.get("in"))
                )
            else:
                new_data = self.storage.load(edge.get("out") + edge.get("in"))
                if (
                    (len(new_data.data) == len(return_data.data))
                    and (return_data.y_columns == return_data.y_columns)
                    and (
                        return_data.additional_columns == return_data.additional_columns
                    )
                ):  # Check if same amount of rows and y and additional columns
                    return_data.data.reset_index(drop=True, inplace=True)
                    new_data.data.reset_index(drop=True, inplace=True)

                    return_data.data = pd.concat(
                        [return_data.data, new_data.get_X_data()], axis=1
                    )
                    return_data.X_columns = list(return_data.X_columns) + list(
                        new_data.X_columns
                    )
                else:
                    raise Exception("Datasets are not compatible!")
        if y_required and return_data.y_columns == []:
            raise KeyError("Y columns must be specified!")
        params["pipeline_data"] = return_data
        return params


def prepare_class_for_pipeline(cls, **params):
    return Sparkify(Pandasify(cls), **params)


def get_nodes_dict(graph_details: Dict) -> Dict:
    nodes_names_dict = {}
    for node_id, node in graph_details["nodes"].items():
        nodes_names_dict[node_id] = node["name"]
    return nodes_names_dict


def make_pipeline_from_dict(
    graph_details: Dict, callback: callable = None, catch_exceptions_to_log=True
):
    nodes_dict = {}
    for node_id, node in graph_details["nodes"].items():
        cls = import_class(node["module"], node["name"])
        parameters = {
            k: v for k, v in node["parameters"].items() if v not in ["", None]
        }

        data_columns = {}
        if "data_columns" in node.keys():
            data_columns = node["data_columns"]

        # this is somehow ugly but for tests we don't need to log errors
        # I prefer to have a version of this function that doesn't catch all exceptions which makes it
        # easier to debug
        if not catch_exceptions_to_log:
            nodes_dict[node_id] = prepare_class_for_pipeline(
                cls(**parameters), **data_columns
            )
        else:
            try:
                nodes_dict[node_id] = prepare_class_for_pipeline(
                    cls(**parameters), **data_columns
                )
                if callback:
                    callback(
                        severity=Severity.INFO,
                        step_type="input_validation",
                        node_id=node_id,
                        status="end",
                        error=None,
                    )
            except Exception as e:
                if callback:
                    if hasattr(e, "message"):
                        error_message = str(e.message)
                    else:
                        error_message = str(e)
                    error_type = e.__class__.__name__
                    callback(
                        severity=Severity.ERROR,
                        step_type="input_validation",
                        node_id=node_id,
                        status="error",
                        error=f"{error_type}: {error_message}",
                    )
                return None

    edges = [
        (f"{a}.{b}", f"{c}.{d}")
        for a, b, c, d in set(map(tuple, graph_details["edges"]))
    ]
    return PipelineRunner(nodes=nodes_dict, edges=edges, callback=callback)


if __name__ == "__main__":
    data = pd.DataFrame(
        {"a": [1, 2, 3, 4, 5], "b": list("abcde"), "c": [0, 0, 0, 1, 1]}
    )

    # Case 1
    nodes = {
        "d1": Pandasify(DataFrame()),
        "t1": Pandasify(Transformer(1)),
        "t2": Pandasify(Transformer(2)),
        "t3": Pandasify(Transformer(3)),
    }
    edges = [
        ("d1.a", "t1.X"),
        ("d1.b", "t1.X"),
        ("d1.c", "t3.X"),
        ("t1.transform", "t2.X"),
        ("t1.transform", "t3.X"),
        ("t2.transform", "t3.X"),
    ]

    runner = PipelineRunner(nodes, edges, callback=example_callback)
    # plot_graphviz(runner.graph)

    fit_transformed = runner.fit_transform(data)
    print(f"fit_transformed: {fit_transformed}")
    print(f"{fit_transformed}")

    # Case 2
    nodes = {
        "d1": Pandasify(DataFrame()),
        "t1": Pandasify(Transformer(1)),
        "e1": Pandasify(DecisionTreeClassifier()),
    }
    edges = [
        ("d1.a", "t1.X"),
        ("d1.c", "e1.y"),
        ("t1.transform", "e1.X"),
    ]

    runner = PipelineRunner(nodes, edges, callback=example_callback)
    # plot_graphviz(runner.graph)

    fitted = runner.fit(data)
    print(f"{fitted}")

    prediction_data = data.drop(columns="c")
    predicted = runner.predict(prediction_data)
    print(f"{predicted}")

    # Testing pipeline dumping and loading (after fit)
    runner = PipelineRunner(nodes, edges, callback=example_callback)

    fitted = runner.fit(data)
    print(f"{fitted}")

    runner.save("saved_pipeline_runner_" + str(id(runner)))
    new_runner = PipelineRunner.load("saved_pipeline_runner_" + str(id(runner)))

    prediction_data = data.drop(columns="c")
    predicted = new_runner.predict(prediction_data)
    print(f"Data should be the same as earlier:\n{predicted}")
