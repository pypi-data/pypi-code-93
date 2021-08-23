from copy import copy
from .errors import CraftAiError


def _update_paths(paths, idx):
    """ add new path build on idx to all paths """
    if paths:
        return paths + ["{}-{}".format(paths[-1], idx)]
    return [str(idx)]


def _paths(tree, paths=None):
    """ return a raw list of all paths in a tree """
    if paths is None:
        paths = ["0"]
    if "children" in tree:
        current_paths = copy(paths)
        for i, child in enumerate(tree["children"]):
            paths.extend(_paths(child, _update_paths(current_paths, i)))
        return paths
    return paths


def _get_paths(tree):
    """ return a set of all paths in a tree """
    return set(_paths(tree))


def _is_neighbour(path0, path1):
    """
        Boolean function. A neighbour has exactly the same path excepted for the last node
    """
    return path0[:-1] == path1[:-1] and path0 != path1


def _get_neighbours(paths, decision_path):
    """
    Collect all neighbours paths of the given decision path
    param: paths: paths aggregator
    param: decision_path: decision path to get neighbours from
    """
    split = decision_path.split("-")
    neighbours = []
    for step in range(1, len(split) + 1):
        for path in paths:
            if _is_neighbour(path, "-".join(split[:step])):
                neighbours.append(path)
    return neighbours


def extract_output_tree(tree, output_property=None):
    """
    Extract the output decision tree specific for a given output property from a full decision tree.

    This function accepts trees as retrieved from `craft_ai.Client.get_generator_decision_tree`.

    Parameters:
        tree: A tree.
        output_property (optional): If provided, the output property for which the tree predicts
            values, otherwise the first defined tree is retrieved.
    """
    if not isinstance(tree, dict):
        raise CraftAiError(
            """Unable to retrieve the output tree, """
            """the given decision tree format is not a valid, expected a 'dict' got a {}.""".format(
                type(tree)
            )
        )
    if "trees" not in tree:
        raise CraftAiError(
            """Unable to retrieve the output tree, """
            """the given decision tree format is not a valid, no 'trees' property defined."""
        )
    trees = tree["trees"]
    if not output_property:
        output_property = list(trees)[0]
    if output_property not in trees:
        raise CraftAiError(
            """'{}' output tree can't be found in the given decision tree.""".format(
                output_property
            )
        )
        tree = tree["trees"][output_property]
    return trees[output_property]


def extract_decision_paths_from_tree(tree):
    """
    Retrieve all the decision paths from a tree.

    This function accepts trees as retrieved from `craft_ai.Client.get_generator_decision_tree`.

    Parameters:
        tree: A tree.
    Returns: e.g. ['0', '0-0', '0-1']
    """
    return _get_paths(extract_output_tree(tree))


def extract_decision_path_neighbors(
    tree, decision_path, max_depth=None, include_self=False
):
    """
    Retrieve neighbor of a decision path in a tree.

    This function accepts trees as retrieved from `craft_ai.Client.get_generator_decision_tree`.

    Parameters:
        tree: A tree.
        decision_path: string tree path eg. "0-2-1".
        max_depth (int, optional): positive int filter neighbours on their depth,
            default is None.
        include_self (bool, optional): include the given decision_path to the neighbours,
            default is False.
    """
    paths = _get_paths(extract_output_tree(tree))
    if decision_path not in paths:
        raise CraftAiError(
            """Invalid decision path given. """
            """{} not found in tree""".format(decision_path)
        )

    dp_depth = len(decision_path.split("-"))
    neighbours = _get_neighbours(paths, decision_path)
    if max_depth is None:
        max_depth = dp_depth
    if max_depth < 0:
        raise CraftAiError(
            """Invalid max depth given: {} should be None or a positive integer """.format(
                max_depth
            )
        )
    filtered = [n for n in neighbours if len(n.split("-")) <= max_depth]
    if include_self:
        filtered.append(decision_path)
    return filtered
