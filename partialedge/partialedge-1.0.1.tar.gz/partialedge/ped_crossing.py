import logging

from partialedge.graph import graph_window as gw
from partialedge.algorithm import ped_algorithm as alg


def run_crossing_sample():
    # setup logging
    logger = logging.getLogger("ped")
    logger.setLevel(logging.INFO - 3)

    # create test class for SHPED with name "sample"
    algorithm = alg.CrossingResolutionAlgorithm("sample", logger=logger)

    # create new random graph
    # algorithm.create_graph(10, 20, layout="spring")

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

    # open windows
    source.show()

    # close matplotlib resources
    source.close()
    result.close()


if __name__ == "__main__":
    run_crossing_sample()
