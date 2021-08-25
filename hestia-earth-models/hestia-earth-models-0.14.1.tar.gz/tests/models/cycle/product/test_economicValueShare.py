from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_product

from hestia_earth.models.cycle.product.economicValueShare import MODEL_KEY, run, _should_run, _should_run_p

class_path = f"hestia_earth.models.cycle.product.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/cycle/product/{MODEL_KEY}"


def test_should_run():
    # if total value >= 100, do nothing
    products = [{
        '@type': 'Product',
        'economicValueShare': 20
    }, {
        '@type': 'Product',
        'economicValueShare': 80
    }, {
        '@type': 'Product'
    }]
    assert not _should_run(products)

    # total < 100 => run
    products[1]['economicValueShare'] = 70
    assert _should_run(products) is True


def test_should_run_product():
    product = {'@type': 'Product'}
    assert _should_run_p(product) is True

    product['economicValueShare'] = 20
    assert not _should_run_p(product)


@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
