import os
import logging
import inspect
import tempfile
from contextlib import contextmanager
from functools import wraps
from typing import Tuple, Dict, List, Callable

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib


def get_function_params(function):
    return [
        p.name
        for p in inspect.signature(function).parameters.values()
        if p.name != "self"
    ]


def parse_tuple(t: Tuple[str, str]) -> Tuple[Tuple[str, str], Dict[str, str]]:
    """
    >>> t = ("d1.a", "t1.X")
    >>> parse_tuple(t)
    (('d1', 't1'), {'out': 'd1.a', 'in': 't1.X'})
    """
    connected_objs, _ = zip(*map(split_object_and_field, t))
    return connected_objs, {"out": t[0], "in": t[1]}


def split_object_and_field(s: str) -> Tuple[str, str]:
    """
    >>> split_object_and_field("t1.X")
    ('t1', 'X')
    >>> split_object_and_field("t1.23.4.X")
    ('t1.23.4', 'X')
    """
    obj, field = s.rsplit(".", maxsplit=1)
    return obj, field


def extract_field(s: str) -> str:
    """
    >>> extract_field("t1.X")
    'X'
    >>> extract_field("t1.23.4.X")
    'X'
    """
    return split_object_and_field(s)[1]


def join_object_and_field(obj: str, field: str) -> str:
    """
    Inverse of split_object_and_field().
    >>> join_object_and_field("a", "b")
    'a.b'
    """
    return f"{obj}.{field}"


def extract_unique_edge_outputs(multi_edges_data: List[Dict[int, Dict]]) -> List[str]:
    """
    Does not contain duplicates
    >>> l = [
    ...     {0: {"out": "d1.a", "in": "t1.X"}, 1: {"out": "d1.b", "in": "t1.X"}},
    ...     {0: {"out": "d1.a", "in": "t1.X"}, 1: {"out": "d1.b", "in": "t1.X"}},
    ...     {0: {"out": "d1.c", "in": "t3.X"}},
    ... ]
    >>> extract_unique_edge_outputs(l)
    ['d1.a', 'd1.b', 'd1.c']
    """
    return sorted(
        {
            single_edge_data["out"]
            for multi_edge_data in multi_edges_data
            for single_edge_data in multi_edge_data.values()
        }
    )


def extract_data_for_many_edges(
    graph: nx.MultiDiGraph, edges: List[Tuple]
) -> List[Dict[int, Dict]]:
    return [graph.get_edge_data(*edge) for edge in edges]


def iter_edges_data(graph, edges):
    for multi_edge in extract_data_for_many_edges(graph, edges):
        for edge in multi_edge.values():
            yield edge


# TODO: subclass Graph to add some auxiliary methods
def build_graph(nodes: Dict, edges: List[Tuple[str, str]]) -> nx.MultiDiGraph:
    """
    Example o input:
    >>> nodes = {
    ...     "d1": DataSource(),
    ...     "t1": Transformer(1),
    ...     "t2": Transformer(2),
    ...     "t3": Transformer(3),
    ... }
    >>> edges = [
    ...     ("d1.a", "t1.X"),
    ...     ("d1.b", "t1.X"),
    ...     ("d1.c", "t3.X"),
    ...     ("t1.transform", "t2.X"),
    ...     ("t1.transform", "t3.X"),
    ...     ("t2.transform", "t3.X"),
    ... ]
    """
    g = nx.MultiDiGraph()
    for node_id, step in nodes.items():
        g.add_node(node_id, step=step)
    for edge, attrs in map(parse_tuple, edges):
        g.add_edge(*edge, **attrs)
    return g


def plot_graph(g):
    pos = nx.spring_layout(g)
    nx.draw(g, pos=pos)
    nx.draw_networkx_labels(g, pos=pos)
    plt.show()


def plot_graphviz(graph):
    """
    Requires:
     - graphviz installed globally (via software manager)
     - pip install pydot
     - pip install graphviz
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = os.path.join(tmpdirname, "graph")
        nx.drawing.nx_pydot.write_dot(graph, path)
        import graphviz

        graphviz.render("dot", "png", path)
        img = matplotlib.image.imread(path + ".png")
        plt.imshow(img)
        plt.axis("off")
        plt.show()


class ClassAsNameMixin:
    def name(self):
        return self.__class__.__name__


class Severity:
    """Based on https://github.com/python/cpython/blob/3.8/Lib/logging/__init__.py"""

    CRITICAL = logging.CRITICAL
    FATAL = CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    @classmethod
    def to_name(cls, level: int) -> str:
        return cls._levelToName[level]

    @classmethod
    def to_level(cls, name: str) -> int:
        return cls._nameToLevel[name]

    _levelToName = {
        CRITICAL: "CRITICAL",
        ERROR: "ERROR",
        WARNING: "WARNING",
        INFO: "INFO",
        DEBUG: "DEBUG",
        NOTSET: "NOTSET",
    }
    _nameToLevel = {
        "CRITICAL": CRITICAL,
        "FATAL": FATAL,
        "ERROR": ERROR,
        "WARN": WARNING,
        "WARNING": WARNING,
        "INFO": INFO,
        "DEBUG": DEBUG,
        "NOTSET": NOTSET,
    }


class Callback:
    def __init__(self, callback: Callable, default_severity: int = Severity.INFO):
        self.callback = callback
        self.default_severity = default_severity

    @contextmanager
    def __call__(self, *, severity=None, step_type=None, node_id=None):
        severity = self.default_severity if severity is None else severity
        self.callback(
            severity=severity, status="start", step_type=step_type, node_id=node_id
        )
        try:
            yield
        except Exception as error:
            severity = max(severity, Severity.ERROR)  # in case of fatal
            if hasattr(error, "message"):
                error_message = str(error.message)
            else:
                error_message = str(error)
            error_type = error.__class__.__name__
            self.callback(
                severity=severity,
                status="failed",
                step_type=step_type,
                node_id=node_id,
                error=f"{error_type}: {error_message}",
            )
            raise
        else:
            self.callback(
                severity=severity, status="end", step_type=step_type, node_id=node_id
            )


# import traceback; print(traceback.format_tb(error.__traceback__))  # a way to extract traceback
def example_callback(
    *, severity: int, step_type=None, node_id=None, status=None, error=None
):
    print(
        f"{Severity.to_name(severity)}:    step_type: {step_type} "
        f"node_id: {node_id} status: {status} error: {error}"
    )


def no_callback(
    *, severity: int, step_type=None, node_id=None, status=None, error=None
):
    pass


def flatten(dct: dict) -> dict:
    """
    Flattens nested dictionaries keeping keys only from the deepest.

    >>> flatten({"a": 1, "b": 2})
    {'a': 1, 'b': 2}
    >>> flatten({"a": 1, "b": {"c": 3, "d": 4}})
    {'a': 1, 'c': 3, 'd': 4}
    >>> flatten({"a": 1, "b": {"c": 3, "d": {"e": 5, "f": 6}}})
    {'a': 1, 'c': 3, 'e': 5, 'f': 6}
    """
    result = {}
    for k, v in dct.items():
        if isinstance(v, dict):
            result.update(flatten(v))
        else:
            result[k] = v
    return result


def add_docs_from(*classes):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        if wrapper.__doc__ is None:
            wrapper.__doc__ = ""
        if not last_line_is_empty(wrapper.__doc__):
            wrapper.__doc__ += "\n"
        wrapper.__doc__ += "\n".join(
            f"\n{cls.__name__}:{cls.__doc__}" for cls in classes
        )
        return wrapper

    return decorator


def last_line_is_empty(s: str) -> bool:
    return s.splitlines()[-1].strip() == ""


if __name__ == "__main__":
    # TODO: this is an example of Callback usage and should later be moved to tests

    class Runner:
        def __init__(self, callback: Callable):
            self.callback = Callback(callback, default_severity=Severity.INFO)

        def run(self):
            with self.callback(severity=Severity.DEBUG, step_type="all"):
                print("started run")
                with self.callback(step_type="step 1", node_id=1):
                    print("inside first step")
                with self.callback(step_type="step 2", node_id=2):
                    print("inside second step.")
                    print("inside second step. Now 1/0 =", 1 / 0)
                print("ended run (this will not be printed due to an error above)")

    r = Runner(example_callback)
    r.run()
