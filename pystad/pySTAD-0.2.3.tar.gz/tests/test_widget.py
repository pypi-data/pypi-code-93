import pytest
import numpy as np
import stad as sd

network = sd.sparse.from_condensed(np.array([0.1, 0.3, 0.4]))
attribute_data = np.array([0.6, 1.0, 3.2])
wrong_attributes = np.array([0.1, 2.3])
labels = ["a", "b", "c"]
wrong_labels = ["a", "b"]


class TestWidget:
  def test_widget_creation(self):
    w = sd.Widget()
    assert isinstance(w, sd.Widget)

  def test_widget_featuremode(self):
    w = sd.Widget(featureMode=True)
    assert isinstance(w, sd.Widget)

  def test_widget_show(self):
    w = sd.Widget()
    w.show(network)
  
  def test_widget_show_node_color(self):
    w = sd.Widget()
    w.show(network, node_color = attribute_data)

  def test_widget_show_wrong_node_color(self):
    w = sd.Widget()
    with pytest.raises(AssertionError):
      w.show(network, node_color = wrong_attributes)

  def test_widget_show_node_size(self):
    w = sd.Widget()
    w.show(network, node_radius = attribute_data)

  def test_widget_show_wrong_node_size(self):
    w = sd.Widget()
    with pytest.raises(AssertionError):
      w.show(network, node_radius = wrong_attributes)

  def test_widget_show_edge_color(self):
    w = sd.Widget()
    w.show(network, link_color = attribute_data)

  def test_widget_show_wrong_edge_color(self):
    w = sd.Widget()
    with pytest.raises(AssertionError):
      w.show(network, link_color = wrong_attributes)

  def test_widget_show_edge_size(self):
    w = sd.Widget()
    w.show(network,  link_width = attribute_data)
   
  def test_widget_show_wrong_edge_size(self):
    w = sd.Widget()
    with pytest.raises(AssertionError):
      w.show(network, link_width = wrong_attributes)

  def test_widget_show_node_label(self):
    w = sd.Widget()
    w.show(network, node_label = labels)
   
  def test_widget_show_wrong_node_label(self):
    w = sd.Widget()
    with pytest.raises(AssertionError):
      w.show(network, node_label = wrong_labels)
