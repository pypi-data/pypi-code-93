""" Some specific tests for API calls of the databases
"""

import sys
import pytest

sys.path.append("..")

import marinvaders.api_calls as ac  # noqa: E402

invalid_aphia_id = -1


def test_request_worms_empty():
    """Check error handling for the worms requests"""
    assert len(ac.request_worms([invalid_aphia_id])) == 0


def test_request_obis_para():
    """Check parameters in obis signature"""
    with pytest.raises(NotImplementedError):
        _ = ac.request_obis(eco_code=123, aphia_id=invalid_aphia_id)
    with pytest.raises(ValueError):
        _ = ac.request_obis()
    with pytest.raises(RuntimeError):
        _ = ac.request_obis(aphia_id=invalid_aphia_id)
