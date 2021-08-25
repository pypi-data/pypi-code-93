from unittest.mock import patch

from hestia_earth.models.utils.term import get_emission_inputs_production_terms, get_liquid_fuel_terms, \
    get_irrigation_terms, get_urea_terms

class_path = 'hestia_earth.models.utils.term'


@patch(f"{class_path}.find_node")
def test_get_emission_inputs_production_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_emission_inputs_production_terms() == [id]


@patch(f"{class_path}.search")
def test_get_liquid_fuel_terms(mock_search):
    id = 'term-id'
    mock_search.return_value = [{'@id': id}]
    assert get_liquid_fuel_terms() == [id]


@patch(f"{class_path}.find_node")
def test_get_irrigation_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_irrigation_terms() == [id]


@patch(f"{class_path}.find_node")
def test_get_urea_terms(mock_find_node):
    id = 'term-id'
    mock_find_node.return_value = [{'@id': id}]
    assert get_urea_terms() == [id]
