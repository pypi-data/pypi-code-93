import json
import os
import pathlib
from partialedge.exception.ped_exception import PartialEdgeDrawingException
from partialedge.graph import graph_creation as gc
from partialedge.algorithm import ped_algorithm as alg


def run_dir_execution(dir_path, symmetric, homogeneous, logger, json_dir=None, image_dir=None, include_image_source=False):
    if not os.path.isdir(dir_path):
        raise PartialEdgeDrawingException("input path for dir execution does not point to a directory")
    for entry in os.listdir(dir_path):
        if not os.path.isfile(os.path.join(dir_path, entry)) or pathlib.Path(entry).suffix != ".json":
            continue

        set_name = pathlib.Path(entry).stem
        if image_dir is not None:
            image_set_dir = os.path.join(image_dir, set_name)
            os.mkdir(image_set_dir)
        else:
            image_set_dir = None

        set_path = os.path.join(dir_path, entry)
        run_set_execution(set_path, symmetric, homogeneous, logger, json_dir, image_set_dir, include_image_source)


def run_set_execution(file_path, symmetric, homogeneous, logger, json_dir=None, image_dir=None, include_image_source=False):
    with open(file_path, "r") as f:
        graph_list_dict = json.load(f)

    json_results = dict()
    for name, graph_dict in graph_list_dict.items():
        graph = gc.load_graph_from_graph_dict(graph_dict)
        algorithm = alg.CrossingResolutionAlgorithm(name, logger=logger) if homogeneous else alg.TreeDecompositionAlgorithm(name, symmetric, logger=logger)
        algorithm.perform_algorithm_on_graph(graph)

        json_results[name] = algorithm.stats

        if image_dir is not None:
            if not include_image_source:
                algorithm.export_image_result(image_dir)
            else:
                algorithm.export_image_result(os.path.join(image_dir, "result"))
                algorithm.export_image_source(os.path.join(image_dir, "source"))

    if json_dir is not None:
        filename = pathlib.Path(file_path).stem
        with open(os.path.join(json_dir, filename + ".json"), "w") as f:
            f.write(json.dumps(json_results, indent=4, sort_keys=True))


def run_single_execution(file_path, symmetric, homogeneous, logger, json_dir=None, image_dir=None, include_image_source=False):
    with open(file_path, "r") as f:
        graph_dict = json.load(f)

    name = pathlib.Path(file_path).stem
    graph = gc.load_graph_from_graph_dict(graph_dict)
    perform_single_run(graph, name, symmetric, homogeneous, logger, json_dir, image_dir, include_image_source)


def perform_single_run(graph, name, symmetric, homogeneous, logger, json_dir=None, image_dir=None, include_image_source=False):
    algorithm = alg.CrossingResolutionAlgorithm(name, logger=logger) if homogeneous else alg.TreeDecompositionAlgorithm(name, symmetric, logger=logger)
    algorithm.perform_algorithm_on_graph(graph)
    if json_dir is not None:
        algorithm.export_json_result(json_dir)

    if image_dir is not None:
        if not include_image_source:
            algorithm.export_image_result(image_dir)
        else:
            algorithm.export_image_result(os.path.join(image_dir, "result"))
            algorithm.export_image_source(os.path.join(image_dir, "source"))


def import_testset(dir, file):
    with open(os.path.join(dir, file), "r") as f:
        test_set = json.load(f)
    graph_list = [(name, gc.load_graph_from_dicts(graph_dict["nodes"], graph_dict["edges"])) for name, graph_dict in test_set.items()]
    return graph_list

