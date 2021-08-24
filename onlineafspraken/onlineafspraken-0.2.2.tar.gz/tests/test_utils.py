from onlineafspraken.api.utils import build_signature
from . import utils


def test_get_response():

    value = utils.get_response("getAgendas")

    assert value


def test_build_signature():
    signature = build_signature(b="b b", a="a")

    assert signature == "aabbb"
