import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist

import stad as sd

data = pd.read_csv('../examples/data/horse.csv')
data = data.sample(n=200)
dist = pdist(data, 'euclidean')
positions = data[['y', 'z']].to_numpy()
(network, sweep) = sd.stad(dist)

class TestPlots:
    def test_plot_network(self):
        fig, nodes, edges, g, pos = sd.plot.network(network)
    
    def test_plot_network_layout(self):
        fig, nodes, edges, g, pos = sd.plot.network(network, layout='spring')

    def test_plot_positions(self):
        fig, nodes, edges, g, pos = sd.plot.network(network, positions=positions)

    def test_plot_ax(self):
        fig, nodes, edges, g, pos = sd.plot.network(network, ax = plt.gca())

    def test_plot_edge_alpha(self):
        fig, nodes, edges, g, pos = sd.plot.network(network, edge_alpha=0.5)

    def test_plot_node_color(self):
        fig, nodes, edges, g, pos = sd.plot.network(network, node_color=data.x)

    def test_plot_edge_color(self):
        fig, nodes, edges, g, pos = sd.plot.network(network, edge_color='k')

    def test_plot_sweep(self):
        fig = sd.plot.sweep(dist, sweep)

    def test_plot_sweep_ax(self):
        fig = sd.plot.sweep(dist, sweep, ax = plt.gca())

    
    def test_plot_sweep_bins(self):
        fig = sd.plot.sweep(dist, sweep, histogram_bins = 10)

    def test_plot_traces(self):
        fig = sd.plot.traces(sweep)