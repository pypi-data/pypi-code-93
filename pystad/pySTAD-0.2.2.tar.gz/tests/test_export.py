import json
import os
import networkx as nx
import numpy as np
import pytest

import stad as sd

network = sd.sparse.from_condensed(np.array([0.1, 0.3, 0.4]))
attribute_data = np.array([0.6, 1.0, 3.2])
wrong_attributes = np.array([0.1, 2.3])
labels = ["a", "b", "c"]
wrong_labels = ["a", "b"]


class TestExport:
  def test_networkx(self):
    g = sd.export.to_networkx(network)
    assert isinstance(g, nx.Graph)
    assert g.number_of_nodes() == 3
    assert g.number_of_edges() == 3
    assert np.allclose([e[2]['distance'] for e in g.edges.data()],
                       network.data / network.data.max())

  def test_networkx_node_color(self):
    g = sd.export.to_networkx(network, node_color = attribute_data)
    assert isinstance(g, nx.Graph)
    assert g.number_of_nodes() == 3
    assert g.number_of_edges() == 3
    assert np.allclose([e[2]['distance'] for e in g.edges.data()],
                       network.data / network.data.max())
    assert np.allclose([n[1]['color_data'] for n in g.nodes.data()],
                       attribute_data)

  def test_networkx_wrong_node_color(self):
    with pytest.raises(AssertionError):
      sd.export.to_networkx(network, node_color = wrong_attributes)

  def test_networkx_node_size(self):
    g = sd.export.to_networkx(network, node_radius = attribute_data)
    assert isinstance(g, nx.Graph)
    assert g.number_of_nodes() == 3
    assert g.number_of_edges() == 3
    assert np.allclose([e[2]['distance'] for e in g.edges.data()],
                       network.data / network.data.max())
    assert np.allclose([n[1]['radius_data'] for n in g.nodes.data()],
                       attribute_data)

  def test_networkx_wrong_node_size(self):
    with pytest.raises(AssertionError):
      sd.export.to_networkx(network, node_radius = wrong_attributes)

  def test_networkx_edge_color(self):
    g = sd.export.to_networkx(network, link_color = attribute_data)
    assert isinstance(g, nx.Graph)
    assert g.number_of_nodes() == 3
    assert g.number_of_edges() == 3
    assert np.allclose([e[2]['distance'] for e in g.edges.data()],
                       network.data / network.data.max())
    assert np.allclose([e[2]['color_data'] for e in g.edges.data()],
                       attribute_data)

  def test_networkx_wrong_edge_color(self):
    with pytest.raises(AssertionError):
      sd.export.to_networkx(network, link_color = wrong_attributes)

  def test_networkx_edge_size(self):
    g = sd.export.to_networkx(network, link_width = attribute_data)
    assert isinstance(g, nx.Graph)
    assert g.number_of_nodes() == 3
    assert g.number_of_edges() == 3
    assert np.allclose([e[2]['distance'] for e in g.edges.data()],
                       network.data / network.data.max())
    assert np.allclose([e[2]['width_data'] for e in g.edges.data()],
                       attribute_data)

  def test_networkx_wrong_edge_size(self):
    with pytest.raises(AssertionError):
      sd.export.to_networkx(network, link_width = wrong_attributes)

  def test_networkx_node_label(self):
    g = sd.export.to_networkx(network, node_label = labels)
    assert isinstance(g, nx.Graph)
    assert g.number_of_nodes() == 3
    assert g.number_of_edges() == 3
    assert np.allclose([e[2]['distance'] for e in g.edges.data()],
                       network.data / network.data.max())
    assert ([n[1]['label'] for n in g.nodes.data()] == labels)

  def test_networkx_wrong_node_label(self):
    with pytest.raises(AssertionError):
      sd.export.to_networkx(network, node_label = wrong_labels)

  def test_dict(self):
    net = sd.export._to_dict(network)
    assert isinstance(net, tuple)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())

  def test_dict_node_color(self):
    net = sd.export._to_dict(network, node_color = attribute_data)
    assert isinstance(net, tuple)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())
    assert ([n['color_data'] for n in net[0]] == attribute_data).all()

  def test_dict_wrong_node_color(self):
    with pytest.raises(AssertionError):
      sd.export._to_dict(network, node_color = wrong_attributes)

  def test_dict_node_size(self):
    net = sd.export._to_dict(network, node_radius = attribute_data)
    assert isinstance(net, tuple)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())
    assert ([n['radius_data'] for n in net[0]] == attribute_data).all()

  def test_dict_wrong_node_size(self):
    with pytest.raises(AssertionError):
      sd.export._to_dict(network, node_radius = wrong_attributes)

  def test_dict_node_label(self):
    net = sd.export._to_dict(network, node_label = labels)
    assert isinstance(net, tuple)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())
    assert [n['label'] for n in net[0]] == labels

  def test_dict_wrong_node_label(self):
    with pytest.raises(AssertionError):
      sd.export._to_dict(network, node_label = wrong_labels)

  def test_dict_edge_color(self):
    net = sd.export._to_dict(network, link_color = attribute_data)
    assert isinstance(net, tuple)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())
    assert ([e['color_data'] for e in net[1]] == attribute_data).all()

  def test_dict_wrong_edge_color(self):
    with pytest.raises(AssertionError):
      sd.export._to_dict(network, link_color = wrong_attributes)

  def test_dict_edge_size(self):
    net = sd.export._to_dict(network, link_width = attribute_data)
    assert isinstance(net, tuple)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())
    assert ([e['width_data'] for e in net[1]] == attribute_data).all()

  def test_dict_wrong_edge_size(self):
    with pytest.raises(AssertionError):
      sd.export._to_dict(network, link_width = wrong_attributes)

  def test_json(self):
    js = sd.export.to_json(network)
    assert isinstance(js, str)
    net = json.loads(js)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())

  def test_json_node_color(self):
    js = sd.export.to_json(network, node_color = attribute_data)
    assert isinstance(js, str)
    net = json.loads(js)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())
    assert ([n['color_data'] for n in net[0]] == attribute_data).all()

  def test_json_wrong_node_color(self):
    with pytest.raises(AssertionError):
      sd.export.to_json(network, node_color = wrong_attributes)

  def test_json_node_size(self):
    js = sd.export.to_json(network, node_radius = attribute_data)
    assert isinstance(js, str)
    net = json.loads(js)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())
    assert ([n['radius_data'] for n in net[0]] == attribute_data).all()

  def test_json_wrong_node_size(self):
    with pytest.raises(AssertionError):
      sd.export.to_json(network, node_radius = wrong_attributes)

  def test_json_node_label(self):
    js = sd.export.to_json(network, node_label = labels)
    assert isinstance(js, str)
    net = json.loads(js)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())
    assert [n['label'] for n in net[0]] == labels

  def test_json_wrong_node_label(self):
    with pytest.raises(AssertionError):
      sd.export.to_json(network, node_label = wrong_labels)

  def test_json_edge_color(self):
    js = sd.export.to_json(network, link_color = attribute_data)
    assert isinstance(js, str)
    net = json.loads(js)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())
    assert ([e['color_data'] for e in net[1]] == attribute_data).all()

  def test_json_wrong_edge_color(self):
    with pytest.raises(AssertionError):
      sd.export.to_json(network, link_color = wrong_attributes)

  def test_json_edge_size(self):
    js = sd.export.to_json(network, link_width = attribute_data)
    assert isinstance(js, str)
    net = json.loads(js)
    assert len(net[0]) == 3
    assert len(net[1]) == 3
    assert np.allclose([e['distance'] for e in net[1]],
                       network.data / network.data.max())
    assert ([e['width_data'] for e in net[1]] == attribute_data).all()

  def test_json_wrong_edge_size(self):
    with pytest.raises(AssertionError):
      sd.export.to_json(network, link_width = wrong_attributes)

  def test_gexf(self):
    sd.export.to_gexf('./test1.gexf', network)
    assert os.path.isfile('./test1.gexf')
    os.remove('./test1.gexf')

  def test_gexf_node_color(self):
    sd.export.to_gexf('./test2.gexf', network, node_color = attribute_data)
    assert os.path.isfile('./test2.gexf')
    os.remove('./test2.gexf')

  def test_gexf_wrong_node_color(self):
    with pytest.raises(AssertionError):
      sd.export.to_gexf('./test3.gexf', network, node_color = wrong_attributes)
    assert not os.path.isfile('./test3.gexf')

  def test_gexf_node_size(self):
    sd.export.to_gexf('./test4.gexf', network, node_radius = attribute_data)
    assert os.path.isfile('./test4.gexf')
    os.remove('./test4.gexf')

  def test_gexf_wrong_node_size(self):
    with pytest.raises(AssertionError):
      sd.export.to_gexf('./test5.gexf', network, node_radius = wrong_attributes)
    assert not os.path.isfile('./test5.gexf')

  def test_gexf_edge_color(self):
    sd.export.to_gexf('./test6.gexf', network, link_color = attribute_data)
    assert os.path.isfile('./test6.gexf')
    os.remove('./test6.gexf')

  def test_gexf_wrong_edge_color(self):
    with pytest.raises(AssertionError):
      sd.export.to_gexf('./test7.gexf', network, link_color = wrong_attributes)
    assert not os.path.isfile('./test7.gexf')

  def test_gexf_edge_size(self):
    sd.export.to_gexf('./test8.gexf', network, link_width = attribute_data)
    assert os.path.isfile('./test8.gexf')
    os.remove('./test8.gexf')

  def test_gexf_wrong_edge_size(self):
    with pytest.raises(AssertionError):
      sd.export.to_gexf('./test9.gexf', network, link_width = wrong_attributes)
    assert not os.path.isfile('./test9.gexf')

  def test_gexf_node_label(self):
    sd.export.to_gexf('./test10.gexf', network, node_label = labels)
    assert os.path.isfile('./test10.gexf')
    os.remove('./test10.gexf')

  def test_gexf_wrong_node_label(self):
    with pytest.raises(AssertionError):
      sd.export.to_gexf('./test11.gexf', network, node_label = wrong_labels)
    assert not os.path.isfile('./test11.gexf')
