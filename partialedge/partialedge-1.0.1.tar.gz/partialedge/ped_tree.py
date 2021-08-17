import logging

from partialedge.graph import graph_window as gw
from partialedge.algorithm import ped_algorithm as alg


def run_tree_sample():
    # setup logging
    logger = logging.getLogger("ped")
    logger.setLevel(logging.INFO - 3)

    # create test class for SPED with name "sample"
    algorithm = alg.TreeAlgorithm("sample", logger=logger)

    # create new random graph with tree intersection
    # algorithm.create_graph(10, 20)

    # load existing graph
    algorithm.load_graph_from_graph_file(file_path="resources/sample/json/source/sample.json")

    # perform algorithm
    algorithm.perform_algorithm()

    # write result to resources/sample
    algorithm.export_source_graph(dir_path="resources/sample/json/source")
    algorithm.export_json_result(dir_path="resources/sample/json/result")
    algorithm.export_image_source(dir_path="resources/sample/image/source")
    algorithm.export_image_result(dir_path="resources/sample/image/result")

    # create window for source graph
    algorithm.set_edges_full()
    source = gw.GraphWindow()
    source.draw_graph(algorithm.graph)

    # create window for result
    algorithm.set_edges_partial()
    result = gw.GraphWindow()
    result.draw_graph(algorithm.graph)

    # create window for intersection graph
    intersection = gw.GraphWindow()
    intersection.draw_graph(algorithm.intersection_graph)

    # open windows
    source.show()

    # close matplotlib resources
    source.close()
    result.close()
    intersection.close()


if __name__ == "__main__":
    run_tree_sample()
