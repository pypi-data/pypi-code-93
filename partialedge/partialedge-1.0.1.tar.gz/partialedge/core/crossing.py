import logging

from partialedge.structure.data_structure import FULL_LENGTH_STUB

DEFAULT_LOGGER_NAME = "ped"
VERBOSITY_LEVEL_GENERAL = logging.INFO - 4
VERBOSITY_LEVEL_CANDIDATE = logging.INFO - 6
VERBOSITY_LEVEL_CROSSING = logging.INFO - 5

logging.basicConfig(format="%(message)s\n", level=logging.INFO)


def calculate_symmetric_homogeneous(intersection_graph, logger=logging.getLogger(DEFAULT_LOGGER_NAME)):
    """
    This algorithm iterates over every crossing and stores the longer stub, that resolves that crossing.
    The minimum of these resolving stubs is the maximal SHPED stub value.

    :param intersection_graph: graph used to detect crossings
    :return: MaxSHPED stub length
    """
    resolving_stubs = [FULL_LENGTH_STUB]

    logger.log(VERBOSITY_LEVEL_GENERAL, "Crossing Resolution edge calculation")

    for edge in intersection_graph.edges:
        logger.log(VERBOSITY_LEVEL_CROSSING, "Examining intersection of {} and {}".format(edge.nodes[0], edge.nodes[1]))
        intersection1 = edge.nodes[0].intersect(edge.nodes[1])
        intersection2 = edge.nodes[1].intersect(edge.nodes[0])
        candidate_stub_value = max(intersection1[0], intersection2[0])
        logger.log(VERBOSITY_LEVEL_CANDIDATE, "SHPED stub value can be at most {:.5f}\n".format(candidate_stub_value))

        resolving_stubs.append(candidate_stub_value)

    result = min(resolving_stubs)
    logger.log(VERBOSITY_LEVEL_GENERAL, "SHPED resulting stub value: {:.5f}\n".format(result))
    return result
