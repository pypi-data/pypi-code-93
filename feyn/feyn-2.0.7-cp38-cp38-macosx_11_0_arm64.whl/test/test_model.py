import unittest

import pytest
import feyn
import _feyn
from pandas import DataFrame

import numpy as np
import io


class TestModel(unittest.TestCase):
    def _create_graph(self):
        # It was not easy to figure out how to create this programatically.
        # So I have just grabbed an example from a notebook.
        # TODO: Create this programatically, so the test does not break on
        # changes in _from_dict.
        return feyn.Model._from_dict({
            'directed': True,
            'multigraph': True,
            'nodes': [{
                'id': 0,
                'location': (0, -1, -1),
                'peerlocation': None,
                'spec': 'in:linear(f)->i',
                'strength': 0,
                'name': 'in',
                'state': {
                    "auto_adapt": True
                }
            }, {
                'id': 1,
                'spec': 'cell:tanh(i)->i',
                'location': (3, 13, 5),
                'peerlocation': None,
                'strength': 0,
                'name': 'tanh',
                'state': {
                    'w0': -14.002081871032715,
                    'w1': 0.6808160543441772,
                    'bias': 4.349215984344482
                }
            }, {
                'id': 2,
                'spec': 'cell:gaussian(i)->i',
                'location': (2, 13, 6),
                'peerlocation': None,
                'strength': 0,
                'name': 'gaussian',
                'state': {
                    'center0': 0.9357265830039978,
                    'center1': 0.9535694718360901,
                    'w0': 0.1639804095029831,
                    'w1': 0.10000000149011612
                }
            }, {
                'id': 3,
                'spec': 'out:linear(i)->f',
                'location': (2, -1, -1),
                'peerlocation': None,
                'strength': 0,
                'name': 'out',
                'state': {
                }
            }],
            'links': [
                {'source': 0, 'target': 1, 'ord': 0},
                {'source': 1, 'target': 2, 'ord': 0},
                {'source': 2, 'target': 3, 'ord': 0}
            ]
        })

    def test_persist_and_rehydrate(self):
        # Arrange
        graph = self._create_graph()

        # Sanity check. Can I predict with this graph?
        predictions = graph.predict({"in": np.array([1, 2])})
        self.assertEqual(len(predictions), 2)

        # Persist it
        file = io.StringIO()
        graph.save(file)

        with self.subTest("Should be loadable"):
            file.seek(0)
            rehydrated_graph = feyn.Model.load(file)

        with self.subTest("Should be executable"):
            predictions = rehydrated_graph.predict({"in": np.array([1, 2])})
            self.assertEqual(len(predictions), 2)

        with self.subTest("Should include a version number"):
            file.seek(0)
            file_contents = file.read()
            self.assertRegex(file_contents, "version")

    def test_persist_accepts_file_and_string(self):
        graph = self._create_graph()

        with self.subTest("Can save and load with file-like objects"):
            file = io.StringIO()
            graph.save(file)

            file.seek(0)
            rehydrated_graph = feyn.Model.load(file)
            self.assertEqual(graph, rehydrated_graph)

        with self.subTest("Can save and load with a string path"):
            import tempfile

            with tempfile.NamedTemporaryFile() as file:
                path = file.name
                graph.save(path)

                rehydrated_graph = feyn.Model.load(path)
                self.assertEqual(graph, rehydrated_graph)


    def test_query_accepts_np(self):
        input = _feyn.Interaction("in:linear(f)->i", latticeloc=(0,0,-1), name="input")

        out = _feyn.Interaction("out:linear(i)->f", latticeloc=(1,0,-1), name="out")
        out._set_source(0, 0)

        g = feyn.Model(2)
        g[0] = input
        g[1] = out

        o = g._query(
            {"input": np.array([42.0, 24, 100, 50])},
            np.array([0.1, 0.3, 0.01, 0.8])
        )

        self.assertEqual(len(o), 4)

    def test_predict_accepts_dicts_with_lists(self):
        # Arrange
        g = self._create_graph()

        o = g.predict(
            {"in": [42.0, 24, 100, 50]}
        )

        self.assertEqual(len(o), 4)
        self.assertFalse(np.isnan(o).any(), "There should be no nans")

    def test_predict_accepts_Series(self):
        g = self._create_graph()

        data = DataFrame({"in": np.array([1,2])})
        series = data.iloc[0]
        o = g.predict(series)
        self.assertFalse(np.isnan(o).any(), "There should be no nans")


    def test_invalid_graph(self):
        # Missing nodes in graph
        with self.assertRaises(RuntimeError):
            graph = feyn.Model(1)
            o = graph.predict({"in": np.array([1, 2])})

        # Wrong kind of input node
        with self.assertRaises(RuntimeError):
            graph = feyn.Model(1)
            node = _feyn.Interaction('cell:tanh(i)->i', latticeloc=(0,0,-1), name="in")
            graph[0] = node
            o = graph.predict({"in": np.array([1, 2])})

        # Wrong kind of output node
        with self.assertRaises(RuntimeError):
            graph = feyn.Model(2)

            register = _feyn.Interaction('in:linear(f)->i', latticeloc=(0,0,-1), name='in')

            node = _feyn.Interaction('cell:tanh(i)->i', latticeloc=(0,0,0), name="tanh")
            node._set_source(0, 0)

            graph[0] = register
            graph[1] = node
            o = graph.predict({"in": np.array([1, 2])})

    def test_access_interactions(self):
        # Arrange
        graph = self._create_graph()

        with self.subTest("Len returns number of interactions"):
            self.assertEqual(len(graph), 4)


        with self.subTest("Can get interaction by index"):
            self.assertEqual(graph[0].name, "in")
            self.assertEqual(graph[3].name, "out")

        with self.subTest("Can get interaction by negative index"):
            self.assertEqual(graph[-1].name, "out")
            self.assertEqual(graph[-4].name, "in")

        with self.assertRaises(IndexError):
            graph[4]

        with self.assertRaises(IndexError):
            graph[-5]
