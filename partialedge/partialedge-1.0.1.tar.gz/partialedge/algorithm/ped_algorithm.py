import os
import json
import random
import timeit
import gc
import logging
from partialedge.structure import data_structure as ds
from partialedge.graph import graph_creation as gcr
from partialedge.graph import graph_window as gw
from partialedge.core import crossing as cr, tree as tr, tree_decomp as dy

DEFAULT_LOGGER_NAME = "ped"
VERBOSITY_LEVEL_PROCESS = logging.INFO - 1
VERBOSITY_LEVEL_EXPORT = logging.INFO - 1
VERBOSITY_LEVEL_CREATION = logging.INFO - 3
VERBOSITY_LEVEL_RESULT = logging.INFO - 2
VERBOSITY_LEVEL_LOADING = logging.INFO - 2
VERBOSITY_LEVEL_TIMING = logging.INFO - 1
VERBOSITY_LEVEL_DATA = logging.INFO - 2

RESULT_PATH = "resources/sample"
COLORS = ["blue", "green", "red", "cyan", "magenta", "yellow", "darkblue", "darkgreen", "orange", "brown", "gold", "grey", "teal"]

logging.basicConfig(format="%(message)s\n", level=logging.INFO)


class PedAlgorithm:

    def __init__(self, name, logger=logging.getLogger(DEFAULT_LOGGER_NAME), output_path=RESULT_PATH):
        self.name = name
        self.logger = logger
        self.output_path = output_path

        self.stats = dict({"success": False})
        self.result_dict = dict()
        self.time_dict = dict()
        self.graph_dict = dict()
        self.intersection_dict = dict()
        self.result_edge_dict = dict()
        self.result_ink = -1

        self.graph = None
        self.intersection_graph = None

    def export_json_result(self, dir_path=None):
        if dir_path is None:
            os.makedirs(os.path.join(self.output_path, "json"), exist_ok=True)
            path = os.path.join(self.output_path, "json", self.name + ".json")
        else:
            path = os.path.join(dir_path, self.name + ".json")

        with open(path, "w") as f:
            f.write(json.dumps(self.stats, indent=4, sort_keys=True))

        self.logger.log(VERBOSITY_LEVEL_EXPORT, "result json exported to {}".format(path))

    def export_source_graph(self, dir_path=None):
        node_list, edge_list = self.create_node_edge_lists()
        root = dict()
        root["nodes"] = node_list
        root["edges"] = edge_list

        if dir_path is None:
            path = os.path.join(self.output_path, self.name + ".json")
        else:
            path = os.path.join(dir_path, self.name + ".json")

        with open(path, "w") as f:
            f.write(json.dumps(root, indent=4, sort_keys=True))

        self.logger.log(VERBOSITY_LEVEL_EXPORT, "source json exported to {}".format(path))

    def export_image_result(self, dir_path=None):
        if dir_path is None:
            path = os.path.join(self.output_path, "image", "result")
        else:
            path = dir_path

        self.set_edges_partial()
        window = gw.GraphWindow()
        window.draw_graph(self.graph)
        window.export_as_png(path, self.name + ".png")
        window.close()

        self.logger.log(VERBOSITY_LEVEL_EXPORT, "result image exported to {}".format(os.path.join(path, self.name + ".png")))

    def export_image_source(self, dir_path=None):
        if dir_path is None:
            path = os.path.join(self.output_path, "image", "source")
        else:
            path = dir_path

        self.set_edges_full()
        window = gw.GraphWindow()
        window.draw_graph(self.graph)
        window.export_as_png(path, self.name + ".png")
        window.close()

        self.logger.log(VERBOSITY_LEVEL_EXPORT, "source image exported to {}".format(os.path.join(path, self.name + ".png")))

    def create_graph(self, n, m, layout="spring"):
        try:
            self.graph = gcr.create_random_graph(n, m, layout)
            node_list, edge_list = self.create_node_edge_lists()
            self.logger.log(VERBOSITY_LEVEL_CREATION, "graph with {} nodes and {} edges created\nnodes: {}\nedges: {}".format(n, m, node_list, edge_list))
        except Exception as e:
            self.stats["error"] = str(e)
            self.logger.error("graph creation failed\n{}".format(str(e)))

    def create_node_edge_lists(self):
        node_list = []
        for node in self.graph.nodes:
            d = dict()
            d["index"] = node.index
            d["coordinates"] = node.coords
            node_list.append(d)

        edge_list = []
        for edge in self.graph.edges:
            d = dict()
            d["incident_nodes"] = [node.index for node in edge.nodes]
            edge_list.append(d)

        return node_list, edge_list

    def load_graph_from_graph_file(self, file_path):
        self.logger.log(VERBOSITY_LEVEL_LOADING, "loading graph from graph file {}".format(file_path))

        with open(file_path, "r") as f:
            d = json.load(f)

        self.graph = gcr.load_graph_from_graph_dict(d)

    def load_graph_from_result_file(self, file_path):
        self.logger.log(VERBOSITY_LEVEL_LOADING, "loading graph from result file {}".format(file_path))

        with open(file_path, "r") as f:
            d = json.load(f)

        self.graph = gcr.load_graph_from_result_dict(d)

    def load_graph_from_graph_dict(self, graph_dict):
        self.graph = gcr.load_graph_from_dicts(graph_dict["nodes"], graph_dict["edges"])

    def perform_algorithm_on_graph(self, graph):
        self.graph = graph
        node_list, edge_list = self.create_node_edge_lists()
        self.logger.log(VERBOSITY_LEVEL_CREATION, "using graph\nnodes: {}\nedges: {}".format(node_list, edge_list))

        self.perform_algorithm()

    def perform_algorithm(self):
        self.set_graph_dict()
        self.execute()

    def set_graph_dict(self):
        self.time_dict["init_datastructure"] = timeit.timeit(stmt=self.init_datastructure, number=1)
        self.logger.log(VERBOSITY_LEVEL_TIMING, "initialization completed in {:.3f} seconds".format(self.time_dict["init_datastructure"]))

        node_list, edge_list = self.create_node_edge_lists()

        node_dict = dict()
        node_dict["node_count"] = len(self.graph.nodes)
        node_dict["nodes"] = node_list

        edge_dict = dict()
        edge_dict["edge_count"] = len(self.graph.edges)
        edge_dict["edges"] = edge_list

        self.graph_dict["node_data"] = node_dict
        self.graph_dict["edge_data"] = edge_dict
        self.graph_dict["ink"] = self.graph.get_ink_value()
        self.stats["graph"] = self.graph_dict

    def set_intersection_dict(self):
        self.intersection_dict["node_count"] = len(self.intersection_graph.nodes)
        self.intersection_dict["edge_count"] = len(self.intersection_graph.edges)

        nodes, edges, delta_count = self.get_intersection_stats()
        self.intersection_dict["nodes"] = nodes
        self.intersection_dict["edges"] = edges
        self.intersection_dict["delta_count"] = delta_count
        self.stats["intersection"] = self.intersection_dict

    def get_intersection_stats(self):
        delta_count = dict()
        node_delta = dict({i: 0 for i in range(len(self.intersection_graph.nodes))})

        for edge in self.intersection_graph.edges:
            node_delta[edge.nodes[0].index] = node_delta[edge.nodes[0].index] + 1
            node_delta[edge.nodes[1].index] = node_delta[edge.nodes[1].index] + 1

        for delta in node_delta.values():
            if len(delta_count) - 1 < delta:
                for i in range(len(delta_count), delta + 1):
                    delta_count[i] = 0
            delta_count[delta] = delta_count[delta] + 1

        nodes = [dict({"index": index, "delta": delta}) for index, delta in node_delta.items()]
        edges = [dict({"incident_nodes": [edge.nodes[0].index, edge.nodes[1].index]}) for edge in self.intersection_graph.edges]
        return nodes, edges, delta_count

    def init_datastructure(self):
        self.intersection_graph = gcr.create_intersection_graph(self.graph.edges, symmetric=True)
        self.set_intersection_dict()

    def execute(self):
        self.logger.log(VERBOSITY_LEVEL_PROCESS, "running partial edge drawing algorithm for graph drawing with {} nodes and {} edges".format(len(self.graph.nodes), len(self.graph.edges)))
        self.logger.log(VERBOSITY_LEVEL_DATA, "initial ink: {:.4f}".format(self.graph.get_ink_value()))

        self.stats["success"] = False
        self.time_dict["algorithm"] = timeit.timeit(stmt=self.run_algorithm, number=1)
        self.logger.log(VERBOSITY_LEVEL_TIMING, "algorithm completed in {:.3f} seconds".format(self.time_dict["algorithm"]))

        self.stats["success"] = True

        self.result_edge_dict["ink"] = self.result_ink
        self.logger.log(VERBOSITY_LEVEL_DATA, "result ink: {:.4f}".format(self.result_ink))

        self.set_result_edges()
        self.logger.log(VERBOSITY_LEVEL_RESULT, "result stub values\n" + ", ".join(["({:d}, [{:.5f}, {:.5f}])".format(node.index, *stubs) for node, stubs in self.result_dict.values()]))

    def set_result_edges(self):
        edgelist = []
        for intersection_node, stubs in self.result_dict.values():
            d = dict()
            d["incident_nodes"] = [node.index for node in intersection_node.edge.nodes]
            d["stub"] = stubs
            edgelist.append(d)
        self.result_edge_dict["edges"] = edgelist

        self.stats["result"] = self.result_edge_dict
        self.stats["time"] = self.time_dict

    def run_algorithm(self):
        pass

    def set_edges_full(self):
        for edge in self.graph.edges:
            edge.factor = ds.FULL_LENGTH_TUPLE

    def set_edges_partial(self):
        for intersection_node, stub_factor in self.result_dict.values():
            intersection_node.edge.factor = stub_factor

    def check_crossings(self, subplot):
        nodes = [node for node, _ in self.result_dict.values()]
        for node in nodes:
            color = random.choice(COLORS)
            node.edge.color = color
            node.edge.draw_label(subplot, node.index)
            print(str(node.index), color)
        for i in range(len(nodes)-1):
            for j in range(i+1, len(nodes)):
                node1stub1 = nodes[i].edge.get_stub_one()
                node1stub2 = nodes[i].edge.get_stub_two()
                node2stub1 = nodes[j].edge.get_stub_one()
                node2stub2 = nodes[j].edge.get_stub_two()
                if node1stub1.crosses(node2stub1) or node1stub1.crosses(node2stub2) or node1stub2.crosses(node2stub1) or node1stub2.crosses(node2stub2):
                    print(str(nodes[i].index), "crosses", str(nodes[j].index))


class TreeDecompositionAlgorithm(PedAlgorithm):

    def __init__(self, name, symmetric, logger=logging.getLogger(DEFAULT_LOGGER_NAME), output_path=RESULT_PATH):
        super(TreeDecompositionAlgorithm, self).__init__(name, logger, output_path)

        self.symmetric = symmetric
        self.root_bag = None
        self.treewidth = -1

    def perform_algorithm(self):
        self.set_graph_dict()
        self.create_tree_decomposition()
        self.execute()

    def create_graph_with_intersection_treewidth(self, n, m, tw, layout):
        self.graph = gcr.create_random_with_tree_width(tw, n, m, self.symmetric, layout)
        node_list, edge_list = self.create_node_edge_lists()
        self.logger.log(VERBOSITY_LEVEL_CREATION, "graph with treewidth {} in intersection graph created\nnodes: {}\nedges: {}".format(tw, node_list, edge_list))

    def create_tree_decomposition(self):
        self.time_dict["tree_decomposition"] = timeit.timeit(stmt=self.tree_decomposition, number=1)
        self.logger.log(VERBOSITY_LEVEL_TIMING, "tree decomposition completed in {:.3f} seconds".format(self.time_dict["tree_decomposition"]))

    def tree_decomposition(self):
        self.root_bag, self.treewidth = dy.form_tree_decomposition(self.intersection_graph, self.symmetric, self.logger)
        self.result_edge_dict["tree_width"] = self.treewidth

    def init_datastructure(self):
        self.intersection_graph = gcr.create_intersection_graph(self.graph.edges, self.symmetric)
        self.set_intersection_dict()
        self.result_edge_dict["symmetric"] = self.symmetric

    def run_algorithm(self):
        self.logger.log(VERBOSITY_LEVEL_PROCESS, "executing Tree Decomposition Algorithm with treewidth {}\n".format(self.treewidth))
        gc.enable()
        records = self.root_bag.calculate_records()
        result_record = max(records, key=lambda x: x.get_ink_value())
        content_dict = dict({**result_record.combination_stubset.stub_dict, **result_record.fixed_stubset.stub_dict})
        self.result_dict = {index: (content_node.intersection_node, stubs) for index, (content_node, stubs) in content_dict.items()}
        self.result_ink = result_record.get_ink_value()


class CrossingResolutionAlgorithm(PedAlgorithm):

    def perform_algorithm(self):
        self.set_graph_dict()
        self.execute()

    def run_algorithm(self):
        self.logger.log(VERBOSITY_LEVEL_PROCESS, "executing Crossing Resolution Algorithm\n")
        gc.enable()
        result_len = cr.calculate_symmetric_homogeneous(self.intersection_graph, self.logger)
        self.result_dict = {node.index: (node, [result_len, result_len]) for node in self.intersection_graph.nodes}
        self.result_ink = sum(edge.get_length() * result_len * 2 for edge in self.graph.edges)


class TreeAlgorithm(PedAlgorithm):

    def __init__(self, name, logger=logging.getLogger(DEFAULT_LOGGER_NAME), output_path=RESULT_PATH):
        super(TreeAlgorithm, self).__init__(name, logger, output_path)
        self.roots = None

    def create_graph(self, n, m, layout=None):
        self.graph = gcr.create_random_with_tree_intersection(n, m)
        node_list, edge_list = self.create_node_edge_lists()
        self.logger.log(VERBOSITY_LEVEL_CREATION, "graph with intersection graph being a tree created\nnodes: {}\nedges: {}".format(node_list, edge_list))

    def create_tree_structure(self):
        self.time_dict["forest_init"] = timeit.timeit(stmt=self.tree_structure, number=1)
        self.logger.log(VERBOSITY_LEVEL_TIMING, "initializing forest from intersection graph took {:.3f} seconds".format(self.time_dict["forest_init"]))

    def tree_structure(self):
        self.roots = tr.form_forest(self.intersection_graph, self.logger)

    def perform_algorithm(self):
        self.set_graph_dict()
        self.create_tree_structure()
        self.execute()

    def run_algorithm(self):
        self.logger.log(VERBOSITY_LEVEL_PROCESS, "executing Tree Algorithm\n")
        gc.enable()
        result_dict = dict()
        sum = 0
        for root in self.roots:
            root.calculate_intersections()
            sum += root.get_best_ink()
            root.collect_result_ink(result_dict)

        self.result_dict = result_dict
        self.result_ink = sum

    def color_intersection_graph(self, subplot):
        for node, _ in self.result_dict.values():
            node.color = node.edge.color
            node.draw_label(subplot, node.index)

