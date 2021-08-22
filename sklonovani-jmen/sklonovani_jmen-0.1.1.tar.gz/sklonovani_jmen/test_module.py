import pytest
from main import Client


class TestModule:
    def setup_method(self):
        self.client = Client(klic="klic")


    @pytest.mark.parametrize("input,expected", [ 
        ("Adelaida", ["paní Adelaido"]),
        ("Adelaida|Tomáš Novák", ["paní Adelaido", "pane Nováku"]),
        ("Firma, s r. o.", ["vážení"])
    ])
    def test_valid_requests(self, input, expected):
        test_result = self.client.request(jmeno=input)
        assert test_result == expected

    
    def test_wrong_key(self):
        client = Client("kilc")
        test_result = client.request()
        assert test_result == ["1"]


    @pytest.mark.parametrize("jmeno_input,pad_input,expected", [
        ("Adelaida", "8", ["4"]),
        ("", "5", ["5"])
    ])
    def test_error_messages(self, jmeno_input, pad_input, expected):
        test_result = self.client.request(jmeno=jmeno_input, pad=pad_input)
        assert test_result == expected


    def test_account_info(self):
        test_result = self.client.account_info(None)
        assert type(test_result) == list
        assert type(test_result[0].isdigit())