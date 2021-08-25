"""Tests for EVMScripts parser"""
import pytest

from evmscript_parser import parse
from evmscript_parser.core.format import (
    HEX_PREFIX, MismatchLength
)


def test_single_parsing():
    """Perform simple test for the single EVM script."""
    spec_id = '00000001'
    address = '7804b6667d649c819dfa94af50c782c26f5abc32'
    method_id = '945233e2'
    call_data = '000000000000000000000000922' \
                'c10dafffb8b9be4c40d3829c8c708a12827f3'  # noqa
    call_data_length_int = (len(method_id) + len(call_data)) // 2
    call_data_length = hex(call_data_length_int)[2:].zfill(8)

    parsed_script = parse(''.join((
        HEX_PREFIX,
        spec_id, address, call_data_length,
        method_id, call_data
    )))

    def _with_prefix(data: str) -> str:
        return f'{HEX_PREFIX}{data}'

    assert parsed_script.spec_id == _with_prefix(spec_id)
    for ind, one_call in enumerate(parsed_script.calls):
        assert one_call.address == _with_prefix(address), ind
        assert one_call.call_data_length == call_data_length_int, ind
        assert one_call.method_id == _with_prefix(method_id), ind
        assert one_call.encoded_call_data == _with_prefix(call_data), ind


def test_positive_examples(positive_example):
    """Run tests for positive parsing examples."""
    script_code, prepared = positive_example
    parsed = parse(script_code)

    assert parsed.spec_id == prepared.spec_id
    assert len(prepared.calls) == len(parsed.calls)

    for prepared_call, parsed_call in zip(
            prepared.calls, parsed.calls
    ):
        assert parsed_call.address == prepared_call.address
        assert parsed_call.call_data_length == prepared_call.call_data_length
        assert parsed_call.method_id == prepared_call.method_id
        assert parsed_call.encoded_call_data == prepared_call.encoded_call_data


def test_negative_examples(negative_example):
    """Run tests for negative parsing examples."""
    broken_script_code = negative_example[0]

    with pytest.raises(MismatchLength):
        _ = parse(broken_script_code)
