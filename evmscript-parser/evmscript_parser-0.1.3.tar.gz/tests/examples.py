"""Tests context."""
from evmscript_parser.core.format import EVMScript, OneCall


class Parsing:
    """Context for testing of parsing functionality."""

    positive_examples = [
        (
            '0x000000017899ef901ed9b331baf7759'
            'c15d2e8728e8c2a2c00000044ae962acf'
            '000000000000000000000000000000000'
            '000000000000000000000000000000100'
            '000000000000000000000000000000000'
            '000000000000000000000000000c9',
            EVMScript(
                spec_id='00000001',
                calls=[
                    OneCall(
                        address='7899ef901ed9b331baf7759c15d2e8728e8c2a2c',
                        call_data_length=68,
                        method_id='ae962acf',
                        encoded_call_data=(
                            '000000000000000000000000000000000000'
                            '000000000000000000000000000100000000'
                            '000000000000000000000000000000000000'
                            '000000000000000000c9'
                        )
                    )
                ]
            )
        ),
        (
            '0x0000000107804b6667d649c819dfa94a'
            'f50c782c26f5abc300000024945233e200'
            '0000000000000000000000922c10dafffb'
            '8b9be4c40d3829c8c708a12827f3',
            EVMScript(
                spec_id='00000001',
                calls=[
                    OneCall(
                        address='07804b6667d649c819dfa94af50c782c26f5abc3',
                        call_data_length=36,
                        method_id='945233e2',
                        encoded_call_data=(
                            '000000000000000000000000922c10'
                            'dafffb8b9be4c40d3829c8c708a128'
                            '27f3'
                        )
                    )
                ]
            )
        ),
        (
            '0x00000001'
            '8EcF1A208E79B300C33895B'
            '62462ffb5b55627E500000024945233e2'
            '000000000000000000000000922c10daf'
            'ffb8b9be4c40d3829c8c708a12827f3'
            '8EcF1A208E79B300C33895B'
            '62462ffb5b55627E500000024945233e2'
            '000000000000000000000000922c10daf'
            'ffb8b9be4c40d3829c8c708a12827f3',
            EVMScript(
                spec_id='00000001',
                calls=[
                    OneCall(
                        address='8EcF1A208E79B300C33895B62462ffb5b55627E5',
                        call_data_length=36,
                        method_id='945233e2',
                        encoded_call_data=(
                            '000000000000000000000000'
                            '922c10dafffb8b9be4c40d38'
                            '29c8c708a12827f3'
                        )
                    ),
                    OneCall(
                        address='8EcF1A208E79B300C33895B62462ffb5b55627E5',
                        call_data_length=36,
                        method_id='945233e2',
                        encoded_call_data=(
                            '000000000000000000000000'
                            '922c10dafffb8b9be4c40d38'
                            '29c8c708a12827f3'
                        )
                    )
                ]
            )
        )
    ]

    negative_examples = [
        (
            # Invalid numbers of data bytes;
            # incorrect counter wrt to origin.
            '0x000000017899ef901ed9b331baf7759'
            'c15d2e8728e8c2a2c00000043ae962acf'
            '000000000000000000000000000000000'
            '000000000000000000000000000000100'
            '000000000000000000000000000000000'
            '000000000000000000000000000c9'
        ),
        (
            # Invalid numbers of data bytes;
            # more bytes wrt to origin.
            '0x000000017899ef901ed9b331baf7759'
            'c15d2e8728e8c2a2c00000044ae962acf'
            '000000000000000000000000000000000'
            '000000000000000000000000000000100'
            '000000000000000000000000000000000'
            '0000000000000000000000000000000c9'
        ),
        (
            # Invalid numbers of data bytes;
            # less bytes wrt to origin.
            '0x000000017899ef901ed9b331baf7759'
            'c15d2e8728e8c2a2c00000044ae962acf'
            '000000000000000000000000000000000'
            '000000000000000000000000000000100'
            '000000000000000000000000000000000'
            '0000000c9'
        ),
        (
            # Incorrect address length.
            '0x0000000104b6667d649c819dfa94a'
            'f50c782c26f5abc300000024945233e200'
            '0000000000000000000000922c10dafffb'
            '8b9be4c40d3829c8c708a12827f3',
        )
    ]


class ABIEtherscan:
    """Context for testing API caller."""

    positive_examples = [
        (
            # Tether
            '0xdac17f958d2ee523a2206206994597c13d831ec7',
            '0x18160ddd',
            'totalSupply',
        ),
        (
            # Wrapped ether
            '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
            '0x70a08231',
            'balanceOf'
        )
    ]
