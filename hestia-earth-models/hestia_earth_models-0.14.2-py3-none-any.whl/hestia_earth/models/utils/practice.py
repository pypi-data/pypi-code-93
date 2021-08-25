from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name

from . import _term_id, _include_methodModel


def _new_practice(term, model=None):
    node = {'@type': SchemaType.PRACTICE.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_hestia(_term_id(term)))
    return _include_methodModel(node, model)


def is_model_enabled(model: str, term_id: str, practice: dict = None):
    """
    Verify if the model + term_id group is allowed for that practice.

    Parameters
    ----------
    model : str
        The name of the `methodModel`.
    term_id : str
        The name of the `term`.
    practice : dict
        The `Practice`.

    Returns
    -------
    bool
        If the model is allowed for that particular model and term_id.
    """
    def get_value():
        term = practice.get('term', {})
        lookup = download_lookup(f"{term.get('termType')}.csv", True)
        value = get_table_value(lookup, 'termid', term.get('@id'), column_name(term_id)) or ''
        return model in value.split(';')

    return get_value() if practice else False
