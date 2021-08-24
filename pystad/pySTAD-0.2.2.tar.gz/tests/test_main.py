import os


# Only checking the API not the output...
class TestMain:
  def test_main(self):
    assert os.system('stad --help') == 0

  def test_main_only_distances(self):
    assert os.system('stad "assets/horse_dists.csv"') == 0

  def test_main_node_attributes(self):
    assert os.system('stad "assets/horse_dists.csv" -n "assets/node_attributes_correct_full.csv"') == 0

  def test_main_node_attributes_color(self):
    assert os.system('stad "assets/horse_dists.csv" -n "assets/node_attributes_correct_color.csv"') == 0

  def test_main_node_attributes_radius(self):
    assert os.system('stad "assets/horse_dists.csv" -n "assets/node_attributes_correct_radius.csv"') == 0

  def test_main_node_attributes_other(self):
    assert os.system('stad "assets/horse_dists.csv" -n "assets/node_attributes_correct_other_column.csv"') == 0

  def test_main_node_attributes_filter(self):
    assert os.system('stad "assets/horse_dists.csv" -n "assets/node_attributes_correct_filter.csv" -b3') == 0

  def test_main_node_attributes_incorrect(self):
    assert os.system('stad "assets/horse_dists.csv" -n "assets/node_attributes_incorrect_full.csv"') > 0

  def test_main_filter(self):
    assert os.system('stad "assets/horse_dists.csv" -b3') == 0

  def test_main_filter_circular(self):
    assert os.system('stad "assets/horse_dists.csv" -n "assets/node_attributes_correct_filter.csv" -b3 -c') == 0

  def test_main_penalty(self):
    assert os.system('stad "assets/horse_dists.csv" -p0.1') == 0

  def test_main_ratio(self):
    assert os.system('stad "assets/horse_dists.csv" -r') == 0

  def test_main_openmp(self):
    assert os.system('stad "assets/horse_dists.csv" -o1') == 0

  def test_main_threshold(self):
    assert os.system('stad "assets/horse_dists.csv" -t0.14') == 0

  def test_main_sweep(self):
    assert os.system('stad "assets/horse_dists.csv" -s 0.1 0.3 5') == 0

  def test_main_sweep_and_threshold(self):
    assert os.system('stad "assets/horse_dists.csv" -t0.14 -s 0.1 0.3 5') > 0

  def test_main_no_arguments(self):
    assert os.system('stad') > 0

  def test_main_edge_attributes(self):
    assert os.system('stad "assets/horse_dists.csv" -e "assets/edge_attributes_correct_full.csv"') == 0

  def test_main_edge_attributes_missing_edges(self):
    assert os.system('stad "assets/horse_dists.csv" -e "assets/edge_attributes_correct_missing_edges.csv"') == 0

  def test_main_edge_attributes_other_column(self):
    assert os.system('stad "assets/horse_dists.csv" -e "assets/edge_attributes_correct_other_column.csv"') == 0

  def test_main_edge_attributes_width(self):
    assert os.system('stad "assets/horse_dists.csv" -e "assets/edge_attributes_correct_width.csv"') == 0

  def test_main_edge_attributes_color(self):
    assert os.system('stad "assets/horse_dists.csv" -e "assets/edge_attributes_correct_color.csv"') == 0

  def test_main_edge_attributes_no_source(self):
    assert os.system('stad "assets/horse_dists.csv" -e "assets/edge_attributes_incorrect_missing_source.csv"') > 0

  def test_main_edge_attributes_no_target(self):
    assert os.system('stad "assets/horse_dists.csv" -e "assets/edge_attributes_incorrect_missing_target.csv"') > 0