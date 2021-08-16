import os
import subprocess
import platform
import networkx as nx
from partialedge.config import PACKAGE_DIR

EXE_WIN_PATH = os.path.join(PACKAGE_DIR, "htd/windows/htd_main")
EXE_LINUX_PATH = os.path.join(PACKAGE_DIR, "htd/linux/htd_main-1.2.0")
GR_PATH = os.path.join(PACKAGE_DIR, "resources/td")
TD_PATH = os.path.join(PACKAGE_DIR, "resources/td")
STD_FILE_NAME = "ped"

DECOMPOSITION_TIMEOUT = 3600


def export_graph_to_gr(graph, filename=STD_FILE_NAME, dir=GR_PATH):
    gr_path = os.path.join(dir, filename + ".gr")
    with open(gr_path, "w") as f:
        f.write("p tw " + str(len(graph.nodes)) + " " + str(len(graph.edges)) + "\n")
        for edge in graph.edges:
            f.write(str(edge.nodes[0].index+1) + " " + str(edge.nodes[1].index+1) + "\n")


def import_from_td(filename=STD_FILE_NAME, dir=TD_PATH):
    td_path = os.path.join(dir, filename + ".td")
    with open(td_path, "r") as f:
        lines = f.readlines()

    first_line = lines[0].split()
    assert(first_line[0] == "s")
    assert(first_line[1] == "td")

    bag_count = int(first_line[2])
    tree_width = int(first_line[3]) - 1
    bags = []
    for line in lines[1:bag_count+1]:
        bag_line = line.split()
        assert(bag_line[0] == "b")
        bag = []
        for node_index in bag_line[2:]:
            bag.append(int(node_index)-1)
        bags.append(bag)

    tree = nx.Graph()
    for line in lines[bag_count+1:]:
        edge = line.split()
        tree.add_edge(int(edge[0])-1, int(edge[1])-1)

    return tree, bags, tree_width


def call_htd(filename=STD_FILE_NAME, in_dir=GR_PATH, out_dir=TD_PATH):
    gr_path = os.path.join(in_dir, filename + ".gr")
    td_path = os.path.join(out_dir, filename + ".td")
    exe_path = EXE_LINUX_PATH if platform.system() == "Linux" else EXE_WIN_PATH
    with open(gr_path, "r") as gr, open(td_path, "w") as td:
        proc = subprocess.Popen(os.path.join(exe_path), stdin=gr, stdout=td)
        proc.wait(DECOMPOSITION_TIMEOUT)
