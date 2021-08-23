import pytest

from jsm_user_services.decorators.lgpd import anonymize_sensible_data
from jsm_user_services.decorators.lgpd_utils import AnonymizeLogic
from jsm_user_services.exception import DecoratorWrongUsage


class TestAnonymizeSensibleData:
    def test_should_raise_if_not_initialized_and_no_param_is_defined(self):
        @anonymize_sensible_data
        def my_method():
            pass

        with pytest.raises(
            TypeError, match=r"wrapper\(\) missing 1 required positional argument: 'method_that_uses_the_decorator'"
        ):
            my_method()

    def test_should_raise_if_initialized_but_no_param_is_defined(self):
        with pytest.raises(
            TypeError, match=r"anonymize_sensible_data\(\) missing 1 required positional argument: 'to_be_anonymized'"
        ):
            # it fails before the method's execution
            @anonymize_sensible_data()
            def my_method():
                pass

    def test_should_raise_if_param_is_not_a_dict(self):
        with pytest.raises(DecoratorWrongUsage, match="Please, pass a dict as param."):
            # it fails before the method's execution
            @anonymize_sensible_data("test")
            def my_method():
                pass

    def test_should_raise_if_key_is_not_a_string(self):
        with pytest.raises(
            DecoratorWrongUsage, match=r"('The keys must be a str, got key %s of type %s', 1, <class 'int'>)"
        ):
            # it fails before the method's execution
            @anonymize_sensible_data({"correct": AnonymizeLogic.NAME, 1: AnonymizeLogic.CPF})
            def my_method():
                pass

    def test_should_raise_if_value_is_not_from_enum(self):
        with pytest.raises(
            DecoratorWrongUsage, match=r"('The values must be a AnonymizeLogic, got value %s', 'some random logic')"
        ):
            # it fails before the method's execution
            @anonymize_sensible_data({"correct": AnonymizeLogic.NAME, "incorrect": "some random logic"})
            def my_method():
                pass

    def test_should_raise_if_method_does_not_return_a_dict(self):
        @anonymize_sensible_data({"correct": AnonymizeLogic.NAME})
        def my_method():
            return "me ajuda cara"

        with pytest.raises(
            DecoratorWrongUsage,
            match=r"('The method must return a dict or a list, but returned type %s', <class 'str'>)",
        ):
            my_method()

    def test_should_raise_if_key_does_not_exist(self):
        @anonymize_sensible_data({"some_key": AnonymizeLogic.NAME})
        def my_method():
            return {}

        with pytest.raises(DecoratorWrongUsage, match=r"('Key not found %s', 'some_key')"):
            my_method()

    def test_should_not_raise_if_key_does_not_exist_but_param_is_false(self):
        @anonymize_sensible_data({"some_key": AnonymizeLogic.NAME}, False)
        def my_method():
            return {}

        assert my_method() == {}

    def test_should_user_pattern_from_param(self):
        @anonymize_sensible_data({"test1xptotest2": AnonymizeLogic.NAME}, traverse_dict_pattern="xpto")
        def my_method():
            return {"test1": {"test2": "Lucas Gigek Carvalho"}}

        assert my_method() == {"test1": {"test2": "Lucas Carvalho"}}

    def test_should_anonymize_data_according_to_param(self):
        @anonymize_sensible_data(
            {
                "name": AnonymizeLogic.NAME,
                "cpf": AnonymizeLogic.CPF,
                "phone": AnonymizeLogic.PHONE,
                "email": AnonymizeLogic.EMAIL,
                "city": AnonymizeLogic.ADDRESS_CITY,
                "state": AnonymizeLogic.ADDRESS_STATE,
                "neighborhood": AnonymizeLogic.ADDRESS_NEIGHBORHOOD,
                "street": AnonymizeLogic.ADDRESS_STREET,
                "number": AnonymizeLogic.ADDRESS_NUMBER,
                "complement": AnonymizeLogic.ADDRESS_COMPLEMENT,
                "postal_code": AnonymizeLogic.ADDRESS_POSTAL_CODE,
            }
        )
        def my_method():
            return {
                "name": "Lucas Gigek Carvalho",
                "cpf": "12345678910",
                "phone": "5511912345678",
                "email": "lucas.carvalho@juntossomosmais.com.br",
                "city": "São Paulo",
                "state": "SP",
                "neighborhood": "Vila Olímpia",
                "street": "Av. Gomes de Carvalho",
                "number": "1666",
                "complement": "8o andar",
                "postal_code": "04547-006",
            }

        assert my_method() == {
            "name": "Lucas Carvalho",
            "cpf": "*******8910",
            "phone": "*********5678",
            "email": "l*************@juntossomosmais.com.br",
            "city": "São Paulo",
            "state": "SP",
            "neighborhood": None,
            "street": None,
            "number": None,
            "complement": None,
            "postal_code": None,
        }

    def test_should_anonymize_data_on_nested_dicts(self):
        @anonymize_sensible_data(
            {
                "address__city": AnonymizeLogic.ADDRESS_CITY,
                "address__state": AnonymizeLogic.ADDRESS_STATE,
                "address__neighborhood": AnonymizeLogic.ADDRESS_NEIGHBORHOOD,
                "address__street": AnonymizeLogic.ADDRESS_STREET,
                "address__number": AnonymizeLogic.ADDRESS_NUMBER,
                "address__complement": AnonymizeLogic.ADDRESS_COMPLEMENT,
                "address__postal_code": AnonymizeLogic.ADDRESS_POSTAL_CODE,
            }
        )
        def my_method():
            return {
                "address": {
                    "city": "São Paulo",
                    "state": "SP",
                    "neighborhood": "Vila Olímpia",
                    "street": "Av. Gomes de Carvalho",
                    "number": "1666",
                    "complement": "8o andar",
                    "postal_code": "04547-006",
                }
            }

        assert my_method() == {
            "address": {
                "city": "São Paulo",
                "state": "SP",
                "neighborhood": None,
                "street": None,
                "number": None,
                "complement": None,
                "postal_code": None,
            }
        }

    def test_should_anonymize_data_on_lists(self):
        @anonymize_sensible_data(
            {
                "addresses__data__city": AnonymizeLogic.ADDRESS_CITY,
                "addresses__data__state": AnonymizeLogic.ADDRESS_STATE,
                "addresses__data__neighborhood": AnonymizeLogic.ADDRESS_NEIGHBORHOOD,
                "addresses__data__street": AnonymizeLogic.ADDRESS_STREET,
                "addresses__data__number": AnonymizeLogic.ADDRESS_NUMBER,
                "addresses__data__complement": AnonymizeLogic.ADDRESS_COMPLEMENT,
                "addresses__data__postal_code": AnonymizeLogic.ADDRESS_POSTAL_CODE,
            }
        )
        def my_method():
            return {
                "addresses": [
                    {
                        "type": "work",
                        "data": {
                            "city": "São Paulo",
                            "state": "SP",
                            "neighborhood": "Vila Olímpia",
                            "street": "Av. Gomes de Carvalho",
                            "number": "1666",
                            "complement": "8o andar",
                            "postal_code": "04547-006",
                        },
                    },
                    {
                        "type": "personal",
                        "data": {
                            "city": "São Paulo",
                            "state": "SP",
                            "neighborhood": "Um bairro honesto",
                            "street": "Uma rua mais honesta ainda",
                            "number": "2",
                            "complement": None,
                            "postal_code": "03874-000",
                        },
                    },
                ]
            }

        assert my_method() == {
            "addresses": [
                {
                    "type": "work",
                    "data": {
                        "city": "São Paulo",
                        "state": "SP",
                        "neighborhood": None,
                        "street": None,
                        "number": None,
                        "complement": None,
                        "postal_code": None,
                    },
                },
                {
                    "type": "personal",
                    "data": {
                        "city": "São Paulo",
                        "state": "SP",
                        "neighborhood": None,
                        "street": None,
                        "number": None,
                        "complement": None,
                        "postal_code": None,
                    },
                },
            ]
        }

    def test_should_anonymize_user_data_from_ishtar(self):
        @anonymize_sensible_data(
            {
                "cpf": AnonymizeLogic.CPF,
                "name": AnonymizeLogic.NAME,
                "emails__email": AnonymizeLogic.EMAIL,
                "phones__number": AnonymizeLogic.PHONE,
                "username": AnonymizeLogic.CPF,
                "addresses__city": AnonymizeLogic.ADDRESS_CITY,
                "addresses__state": AnonymizeLogic.ADDRESS_STATE,
                "addresses__number": AnonymizeLogic.ADDRESS_NUMBER,
                "addresses__street": AnonymizeLogic.ADDRESS_STREET,
                "addresses__district": AnonymizeLogic.ADDRESS_NEIGHBORHOOD,
                "addresses__complement": AnonymizeLogic.ADDRESS_COMPLEMENT,
                "addresses__postal_code": AnonymizeLogic.ADDRESS_POSTAL_CODE,
            }
        )
        def my_method():
            return {
                "id": "b74ad26a-e80a-4756-bdc9-1207fd3c62e9",
                "cpf": "44053216044",
                "name": "Proprietário Automação sHAZRscr",
                "roles": ["owner"],
                "emails": [{"type": "personal", "email": "diego.ferreira@juntossomosmais.com.br"}],
                "gender": "male",
                "phones": [
                    {"type": "mobile", "number": "5511981656209"},
                    {"type": "landline", "number": "551155380499"},
                ],
                "status": "active",
                "mediums": ["whatsapp"],
                "birthday": "1990-01-01",
                "username": "44053216044",
                "addresses": [
                    {
                        "city": "São Paulo",
                        "type": "main",
                        "state": "SP",
                        "number": "474",
                        "street": "Rua João Fugulin",
                        "country": "BRA",
                        "district": "Jardim Germânia",
                        "complement": "3564572",
                        "postal_code": "05849340",
                    },
                    {
                        "city": "São Paulo",
                        "type": "shipping",
                        "state": "SP",
                        "number": "474",
                        "street": "Rua João Fugulin",
                        "country": "BRA",
                        "district": "Jardim Germânia",
                        "complement": "3564572",
                        "postal_code": "05849340",
                    },
                ],
            }

        assert my_method() == {
            "id": "b74ad26a-e80a-4756-bdc9-1207fd3c62e9",
            "cpf": "*******6044",
            "name": "Proprietário sHAZRscr",
            "roles": ["owner"],
            "emails": [{"type": "personal", "email": "d*************@juntossomosmais.com.br"}],
            "gender": "male",
            "phones": [
                {"type": "mobile", "number": "*********6209"},
                {"type": "landline", "number": "********0499"},
            ],
            "status": "active",
            "mediums": ["whatsapp"],
            "birthday": "1990-01-01",
            "username": "*******6044",
            "addresses": [
                {
                    "city": "São Paulo",
                    "type": "main",
                    "state": "SP",
                    "number": None,
                    "street": None,
                    "country": "BRA",
                    "district": None,
                    "complement": None,
                    "postal_code": None,
                },
                {
                    "city": "São Paulo",
                    "type": "shipping",
                    "state": "SP",
                    "number": None,
                    "street": None,
                    "country": "BRA",
                    "district": None,
                    "complement": None,
                    "postal_code": None,
                },
            ],
        }

    def test_should_not_raise_if_list_contains_different_data_structures(self):
        @anonymize_sensible_data({"users__name": AnonymizeLogic.NAME})
        def my_method():
            return {"users": ["Baraka", "Johnny Cage", {"name": "Liu L Kang"}]}

        assert my_method() == {"users": ["Baraka", "Johnny Cage", {"name": "Liu Kang"}]}

    def test_should_anonymize_if_dict_has_nested_lists(self):
        @anonymize_sensible_data({"users__name": AnonymizeLogic.NAME})
        def my_method():
            return {
                "users": [
                    [{"name": "Baraka"}, {"name": "Liu L Kang"}],
                    [{"name": "Kung K Lao"}, {"name": "Johnny J. Cage"}],
                ]
            }

        assert my_method() == {
            "users": [[{"name": "Baraka"}, {"name": "Liu Kang"}], [{"name": "Kung Lao"}, {"name": "Johnny Cage"}]]
        }

    def test_should_anonymize_if_param_is_a_list(self):
        @anonymize_sensible_data({"name": AnonymizeLogic.NAME})
        def my_method():
            return [
                {"name": "Baraka"},
                {"name": "Liu L Kang"},
                {"name": "Kung K Lao"},
                {"name": "Johnny J Cage"},
                {"name": 'Edward John "Noob Saibot" Boon'},
            ]

        assert my_method() == [
            {"name": "Baraka"},
            {"name": "Liu Kang"},
            {"name": "Kung Lao"},
            {"name": "Johnny Cage"},
            {"name": "Edward Boon"},
        ]

    def test_should_work_if_method_receives_a_param(self):
        @anonymize_sensible_data({"name": AnonymizeLogic.NAME})
        def my_method(should_return, *args, **kwargs):
            return should_return

        assert my_method({"name": "Liu Kang"}) == {"name": "Liu Kang"}
        assert my_method(should_return={"name": "Liu Kang"}) == {"name": "Liu Kang"}
        assert my_method({"name": "Liu Kang"}, useless_param_that_shouldnt_impact="test") == {"name": "Liu Kang"}
