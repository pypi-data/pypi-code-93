from typing import Callable, Dict, List, Optional, Tuple

from sklearn.base import BaseEstimator, TransformerMixin

from fathom_lib.component_autogeneration.sklearn.generate_ui_components import try_numeric
from fathom_lib.component_autogeneration.submodules import import_class
from fathom_lib.datasources.download import download_data
from fathom_lib.experimentation.loggers import make_logger
from fathom_lib.pipeline_runner import (
    PipelineRunner,
    Picklable,
    get_nodes_dict,
    prepare_class_for_pipeline,
)
from fathom_lib.runnable.components import Runnable
from fathom_lib.datasources import DataFrame
from fathom_lib.utils import (
    Severity,
    no_callback,
)
from fathom_lib.pandas_utils import generate_fake_dataframe


class Workflow(BaseEstimator, TransformerMixin, Picklable):
    def __init__(
        self,
        nodes: Dict,
        edges: List[Tuple[str, str]],
        callback: Callable,
        data_schema: Dict,
    ):
        (
            self.runnable_nodes,
            self.runnable_edges,
            self.pipeline_nodes,
            self.pipeline_edges,
        ) = self.separate_nodes(nodes, edges)

        self.callback = callback

        self.model_pipeline = PipelineRunner(
            nodes=self.pipeline_nodes, edges=self.pipeline_edges, callback=self.callback
        )

        self.data_schema = data_schema

    def get_data_schema(self):
        return self.data_schema

    def get_model_pipeline(self):
        return self.model_pipeline

    def run(self, context: Dict):
        for node_id, node in self.runnable_nodes.items():
            print(f"Running {node_id} {node}")
            node.run(self.model_pipeline, context)

    def separate_nodes(self, nodes: Dict, edges: List[Tuple[str, str]]):
        runnable_nodes, pipeline_nodes = {}, {}
        runnable_edges, pipeline_edges = edges.copy(), edges.copy()
        for node_id, node in nodes.items():
            if isinstance(node, Runnable):
                runnable_nodes[node_id] = node
                pipeline_edges = delete_edges_with_node(pipeline_edges, node_id)
            else:
                pipeline_nodes[node_id] = node
                runnable_edges = delete_edges_with_node(runnable_edges, node_id)
        return runnable_nodes, runnable_edges, pipeline_nodes, pipeline_edges


def get_node_id(edge_end):
    node_id, _ = edge_end.split(".")
    return node_id


def delete_edges_with_node(edges: List[Tuple[str, str]], node_id):
    return [
        edge
        for edge in edges
        if not ((get_node_id(edge[0]) == node_id) or (get_node_id(edge[1]) == node_id))
    ]


def make_workflow_from_dict(graph_details: Dict, callback: callable = no_callback):
    nodes_dict = {}
    for node_id, node in graph_details["nodes"].items():
        cls = import_class(node["module"], node["name"])
        if "parameters" in node:
            parameters = {
                k: v for k, v in node["parameters"].items() if v not in ["", None]
            }
        else:
            parameters = {}
        print(f"Node {node_id} parameters {parameters}")

        data_columns = {}
        if "data_columns" in node.keys():
            data_columns = node["data_columns"]

        data_mapping = {}
        if "data_mapping" in node.keys():
            data_mapping = node["data_mapping"]

        try:
            cls_instance = cls(**parameters)
            if not isinstance(cls_instance, Runnable):
                if isinstance(cls_instance, DataFrame):
                    dataframe_node_id = node_id
                nodes_dict[node_id] = prepare_class_for_pipeline(
                    cls_instance, **data_columns, data_mapping=data_mapping
                )
            else:
                nodes_dict[node_id] = cls_instance

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
                print(parameters)
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

    data_schema = graph_details["nodes"][dataframe_node_id]["schema_json"]

    return Workflow(
        nodes=nodes_dict, edges=edges, callback=callback, data_schema=data_schema
    )


def validate_pipeline_fake_data(graph_details):
    nodes_names_dict = get_nodes_dict(graph_details)
    log = []

    def callback(
        *, severity: int, step_type=None, node_id=None, status=None, error=None
    ):
        log.append(
            dict(
                severity=severity,
                step_type=step_type,
                node_id=node_id,
                node_name=nodes_names_dict.get(node_id, node_id),
                status=status,
                error=error,
            )
        )

    workflow = make_workflow_from_dict(graph_details, callback)
    if workflow:
        dataset_schema = workflow.get_data_schema()
        pipeline = workflow.get_model_pipeline()
        df_fake = generate_fake_dataframe(dataset_schema, 100)
        try:
            pipeline.fit(df_fake)
            pipeline.predict(df_fake)
        except:
            pass
    return log


def run_workflow(
    graph_details, data_source, logger_local=False, logger_name="MlflowLogger"
):
    nodes_names_dict = get_nodes_dict(graph_details)
    log = []
    logger_params = {}

    def callback(
        *, severity: int, step_type=None, node_id=None, status=None, error=None
    ):
        log.append(
            dict(
                severity=severity,
                step_type=step_type,
                node_id=node_id,
                node_name=nodes_names_dict.get(node_id, node_id),
                status=status,
                error=error,
            )
        )

    workflow = make_workflow_from_dict(graph_details, callback)
    dataframe = download_data(data_source)
    if logger_name == "MlflowLogger":
        # TODO remove the hardcoded paths
        if logger_local:
            logger_params = dict(
                tracking_uri="http://localhost:8010/",
                experiment_name="Test experiment 1",
            )
        else:
            logger_params = dict(
                tracking_uri="http://mlflow:5555/", experiment_name="Test experiment 1"
            )
    logger = make_logger(logger_name, **logger_params)

    context = {"data": dataframe, "logger": logger}
    workflow.run(context)
    return log
