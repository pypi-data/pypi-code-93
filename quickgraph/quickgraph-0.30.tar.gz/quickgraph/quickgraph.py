"""QuickGraph Library (v0.1)
"""

import networkx as nx
import statistics
import random
import community as community_louvain
import networkx.algorithms.community as nx_comm
import matplotlib.pyplot as plt
import numpy as np
import pathlib


def info(G):
    """
    This function will show some basic metrics of graph G, including:
        basic information of the graph,
        average degree,
        average clustering coefficient,
        number of connected components,
        percentage of nodes within the largest connected component (LCC),
        modularity value of the graph using the label propagation partition and the louvain partition,
        CDF plot of degree and clustering coefficient,
        BAR plot of up to top 10 large connected components.
        All figures are filed in a new /figures folder, with number od nodes and edges entitled.  
    
    """
    num_nodes = len(list(G.nodes))
    print("Number of Nodes:", num_nodes, end=", ")
    num_edges = len(list(G.edges))
    print("Number of Edges:", num_edges)

    degree_all = 0
    degree_ytick = []
    for uid in G.nodes:
        degree_all += G.degree(uid)
        degree_ytick.append(G.degree(uid))
    average_degree = round(degree_all/num_nodes, 4)       
    print("Avg. degree:", average_degree, end=", ")
    plot_CDF(degree_ytick, 'Degree', num_nodes, num_edges)

    print("Avg. clustering coefficient:", round(nx.average_clustering(G), 4), end=", ")
    clustering = list(nx.clustering(G).values())
    plot_CDF(clustering, "ClusteringCoefficient", num_nodes, num_edges)

    v = {}
    louvain_dict = community_louvain.best_partition(G)
    for key, value in louvain_dict.items():
        v.setdefault(value, set()).add(key)
    louvain_patition = v.values()
    print("Modularity (Louvain) =", round(nx_comm.modularity(G, louvain_patition),4))
        
    cc = sorted(nx.connected_components(G), key=len, reverse=True)
    
    print("Number of connected components:", len(cc), end=", ")
    print("Number of nodes in LCC:", len(cc[0]), "(",round(len(cc[0])/num_nodes*100, 4),"%)")
    if len(cc)  > 0:
        data = []
        counter = 0
        while counter < min(len(cc), 10):
            data.append(len(cc[counter]))
            counter += 1
        
        plot_BAR(list(data), num_nodes, num_edges)
        
    #print("Modularity (label propagation) =", round(nx_comm.modularity(G,nx_comm.label_propagation_communities(G)),4), end=", ")

    
    
def plot_CDF(data, index, num_nodes, num_edges):
    plot_xtick = sorted(data)
    plot_ytick = np.array(data)
    xrange = np.percentile(plot_ytick,95)

    pdf = plot_ytick/sum(plot_ytick)
    cdf = np.cumsum(pdf)
    plt.plot(plot_xtick, cdf, label = 'CDF')
    plt.xlabel(index)
    plt.ylabel('Fraction')
    plt.title('CDF of '+index)
    
    plt.xlim([0,max(xrange, 0.00001)])
    plt.ylim([0,1])
    fig_name = 'QuickGraph_N' + str(num_nodes) + '_E' + str(num_edges) + '_' +index +'_CDF'
    pathlib.Path('./figures').mkdir(parents=True, exist_ok=True) # Python 3.5 and above
    plt.savefig('./figures/'+fig_name+'.eps', bbox_inches='tight')
    plt.close()

def plot_BAR(data, num_nodes, num_edges):
    plt.style.use('ggplot')

    x_ticks = []
    counter = 0
    while counter < len(data):
        counter += 1
        x_ticks.append(counter)

    y = data

    plt.bar(x_ticks, y, log=True)
    plt.xticks(x_ticks)
    plt.xlabel("Top 10 Connected Components")
    plt.ylabel("Size")
    plt.title("Sizes of the top 10 connected components")
    fig_name = 'QuickGraph_N' + str(num_nodes) + '_E' + str(num_edges) + '_'  +'_BAR'
    plt.savefig('./figures/'+fig_name+'.png', bbox_inches='tight')
    plt.close()

def LCC_analysis(G):

    """
    This functio will show some basic information about the largest connected component LCC optionally, including:
        average degree,
        average clustering coefficient,
        rough distribution of shortest path length using 1000 randomly selected nodes in the LCC.

    """
    
    cc = sorted(nx.connected_components(G), key=len, reverse=True)
    largest_cc = G.subgraph(cc[0])
    cc_nodes = list(largest_cc.nodes)
    nodes_num = largest_cc.number_of_nodes()
    LCC_degrees = largest_cc.degree()
    LCC_degrees_seq = []
    for uid in cc_nodes:
        LCC_degrees_seq.append(LCC_degrees[uid])
    sum_degree = 0
    for x in LCC_degrees:
        sum_degree += x[1]
    print("LCC: Avg. degree =", round(sum_degree/nodes_num, 4),end=", ")

    print("Avg. clustering coefficient =", round(nx.average_clustering(largest_cc), 4),end=", ")

    v = {}
    louvain_dict = community_louvain.best_partition(G)
    for key, value in louvain_dict.items():
        v.setdefault(value, set()).add(key)
    louvain_patition = v.values()
    print("Modularity (Louvain) =", round(nx_comm.modularity(G, louvain_patition),4))
    #modularity_value = nx_comm.modularity(largest_cc,nx_comm.label_propagation_communities(largest_cc))
    #print("Modularity =",round(modularity_value, 4))

    shortest_path_pdf = {}
    shortest_path_mean = []
    list_path_length = []
    for counter in range(500):
        source = cc_nodes[random.randint(0,nodes_num-1)]
        dest = cc_nodes[random.randint(0,nodes_num-1)]
        shortest_path_length = nx.shortest_path_length(largest_cc, source, dest)
        if shortest_path_length in shortest_path_pdf.keys():
            shortest_path_pdf[shortest_path_length] += 1
            shortest_path_mean.append(shortest_path_length)
        else:
            shortest_path_pdf[shortest_path_length] =1
            shortest_path_mean.append(shortest_path_length)
    

    list_path_length = list(shortest_path_pdf.keys())
    list_path_length.sort()
    print("(rough) shortest path length =", end = " ")
    for index in list_path_length: 
        print(index,":",shortest_path_pdf[index], "(",shortest_path_pdf[index]/10, "%)",end = ", ")

    print("Avg. shortest path length =",statistics.mean(shortest_path_mean))


def demo():
    G = nx.Graph()
    with open('nodes_58228.csv', 'r',newline='') as f:
        reader = f.readline()
        while reader:
            G.add_node(int(reader))
            reader = f.readline()

    with open('links_58228.csv', 'r', newline='') as f: #Add edges into G
        reader = f.readline()
        while reader:
            x = reader.split(',')
            node_1 = int(x[0])
            node_2 = int(x[1])
            G.add_edge(node_1, node_2)
            reader = f.readline()
            
    info(G) # Show the basic information of the graph
    LCC_analysis(G,1,1,1) # Show the information of the largest connected component (LCC)


    
    


