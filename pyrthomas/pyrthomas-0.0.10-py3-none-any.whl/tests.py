import io
from operator import eq
from unittest import TestCase

import networkx as nx

from network import NetworkService
from network_analyser import NetworkAnalyser
from pyrthomas.cytoscape import read_sif, write_sif


class NetworkTestCase(TestCase):
    def setUp(self):
        self.network = nx.DiGraph()
        self.network.add_edge('x', 'y', weight=1)
        self.network.add_edge('x', 'x', weight=2)
        self.network.add_edge('y', 'x', weight=-1)

        # self.network.add_edge('BTK', 'MAL', weight=1)
        # self.network.add_edge('MAL', 'NFKB', weight=1)
        # self.network.add_edge('NFKB', 'INCY', weight=1)
        # self.network.add_edge('INCY', 'NFKB', weight=2)
        # self.network.add_edge('INCY', 'SOCS1', weight=1)
        # self.network.add_edge('SOCS1', 'NFKB', weight=-1)
        # self.network.add_edge('SOCS1', 'MAL', weight=-1)

    def test_state_space(self):
        result = NetworkAnalyser.get_state_space(self.network)
        expected = [{'x': 0, 'y': 0}, {'x': 0, 'y': 1}, {'x': 1, 'y': 0}, {'x': 1, 'y': 1},
                    {'x': 2, 'y': 0},
                    {'x': 2, 'y': 1}]
        self.assertEqual(result, expected)

    def test_state_graph(self):
        parameters = {
            "x": [
                ([], 0,), (['x'], 2), (['y'], 2), (['x', 'y'], 2)
            ],
            "y": [
                ([], 0,), (['x'], 1)
            ]
        }
        graph = NetworkAnalyser.get_state_graph(self.network, parameters)
        result = list(graph.nodes)
        expected = ['0,0', '0,1', '1,0', '1,1', '2,0', '2,1']
        self.assertListEqual(result, expected)

    def test_sif_converter(self):
        with io.StringIO('') as f:
            write_sif(self.network, f)
            f.seek(0)
            G = read_sif(f)
        em = nx.algorithms.isomorphism.generic_edge_match('weight', 1,
                                                          lambda x, y: eq(str(x), str(y)))
        result = nx.is_isomorphic(self.network, G, edge_match=em)
        self.assertTrue(result)

    def test_dot_converter(self):
        service = NetworkService()
        service.network = self.network
        with io.StringIO('') as f:
            service.export_dot(f)
            imported_network = NetworkService()

            f.seek(0)

            imported_network.import_dot(f)

        em = nx.algorithms.isomorphism.generic_edge_match('weight', 1,
                                                          lambda x, y: eq(str(x), str(y)))
        result = nx.is_isomorphic(self.network, imported_network.network, edge_match=em)
        # self.assertTrue(result)

    def test_network_service_sif_converter(self):
        service = NetworkService()
        service.network = self.network
        with io.StringIO('') as f:
            service.export_sif(f)
            imported_network = NetworkService()

            f.seek(0)

            imported_network.import_sif(f)

        em = nx.algorithms.isomorphism.generic_edge_match('weight', 1,
                                                          lambda x, y: eq(str(x), str(y)))
        result = nx.is_isomorphic(self.network, imported_network.network, edge_match=em)
        self.assertTrue(result)

    def test_all(self):
        graphs = NetworkAnalyser.get_possible_state_graphs(self.network)
        assert len(list(graphs)) == 324
