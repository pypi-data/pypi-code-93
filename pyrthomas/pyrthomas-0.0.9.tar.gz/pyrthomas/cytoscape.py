import sys

from networkx.utils import open_file
import networkx as nx


@open_file(0, mode='r')
def read_sif(path, connector=None):
    """Read graph in cytoscape SIF format from path.

    Parameters
    ----------
    path : file or string
       File or filename to write.

    Returns
    -------
    G : NetworkX MultiGraph or MultiDiGraph."""

    lines = (line for line in path)
    G = nx.DiGraph()
    for i in lines:
        l = i.split()
        if len(l) == 3 and connector:
            if l[1] != connector:
                continue
        if len(l) == 3:  # interaction
            # take " out of the name
            if l[0][0] == '"' and l[0][-1] == '"':
                l[0] = l[0][1:-1]
            if l[2][0] == '"' and l[2][-1] == '"':
                l[2] = l[2][1:-1]
        else:  # node only
            if len(l) != 1: continue
            if l[0][0] == '"' and l[0][-1] == '"':
                l[0] = l[0][1:-1]
            G.add_node(l[0])
        if len(l) < 3: continue
        try:
            list(G.nodes).index(l[0])
        except:
            G.add_node(l[0])
        try:
            list(G.nodes).index(l[2])
        except:
            G.add_node(l[2])
        G.add_edge(l[0], l[2], weight=l[1])
    return G


@open_file(1, mode='w')
def write_sif(G: nx.DiGraph, path, connector=None):
    """Write NetworkX graph G to cytoscape sif format on path.

    Path can be a string or a file handle.
    """
    for edge in list(G.edges(data=True)):
        link = connector if connector is not None else edge[2]['weight']
        path.write("%s\t%s\t%s\n" % (edge[0],
                                     link,
                                     edge[1]))
    return


def importCyAttributes(obj, filename='-', attr=None):
    """Imports attributes from a Cytoscape's attributes file

    @param obj: network
    @param filename: attributes file
    """
    if filename == '-':
        arq = sys.stdin
    else:
        arq = open(filename, 'r')
    if attr == None:
        attr = arq.readline().split()[0]
        if attr == 'cluster' or attr == 'Cluster':
            attr = ('cluster', 'cluster')
    else:
        arq.next()  # read header even if it's not used
    for i in arq:
        l = i.split()
        # TODO: error if n == None
        n = obj.findNode(l[0])
        if n != None:
            obj.nodes[n].setAttribute(attr, ' '.join(l[2:]))
    if filename != '-':
        arq.close()


def exportCyAttributes(obj, filename='-', attrname=('cluster', 'cluster'), s=""):
    """Exports attributes to a Cytoscape's attributes file

    @param obj: network
    @param filename: file to export
    @param attrname: attribute to write as header of Cytoscape's
    attributes file"""
    if filename == '-':
        arq = sys.stdout
    else:
        arq = open(filename, 'w')
    if isinstance(attrname, tuple):
        arq.write("%s\n" % attrname[-1])
    else:
        arq.write("%s\n" % attrname)
    for i in range(0, obj.nnodes):
        arq.write("%s\t=\t%s%s\n" % (obj.nodes[i].getName(), s,
                                     obj.nodes[i].getAttribute(attrname)))
    if filename != '-':
        arq.close()
