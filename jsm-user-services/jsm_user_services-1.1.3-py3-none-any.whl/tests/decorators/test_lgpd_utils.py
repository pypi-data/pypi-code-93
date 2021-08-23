import pytest

from jsm_user_services.decorators.lgpd_utils import AnonymizeLogic
from jsm_user_services.exception import DecoratorWrongUsage


class TestAnonymizeName:
    def test_should_raise_if_name_is_not_a_string(self):
        with pytest.raises(DecoratorWrongUsage):
            AnonymizeLogic.anonymize_name(123)

    def test_should_return_none_if_name_is_none(self):
        assert AnonymizeLogic.anonymize_name(None) is None

    def test_should_return_first_name_and_last_name_if_name_is_complete(self):
        assert AnonymizeLogic.anonymize_name("Lucas Gigek Carvalho") == "Lucas Carvalho"

    def test_should_return_only_first_name_if_there_is_no_last_name(self):
        assert AnonymizeLogic.anonymize_name("Lucas") == "Lucas"


class TestAnonymizeCpf:
    def test_should_raise_if_cpf_is_not_a_string(self):
        with pytest.raises(DecoratorWrongUsage):
            AnonymizeLogic.anonymize_cpf(12345678910)

    def test_should_none_if_cpf_is_none(self):
        assert AnonymizeLogic.anonymize_cpf(None) is None

    def test_should_return_anonymized_cpf(self):
        assert AnonymizeLogic.anonymize_cpf("12345678910") == "*******8910"


class TestAnonymizePhone:
    def test_should_raise_if_phone_is_not_a_string(self):
        with pytest.raises(DecoratorWrongUsage):
            AnonymizeLogic.anonymize_phone(5511912345678)

    def test_should_return_none_if_phone_is_none(self):
        assert AnonymizeLogic.anonymize_phone(None) is None

    def test_should_return_anonymized_phone(self):
        assert AnonymizeLogic.anonymize_phone("5511912345678") == "*********5678"


class TestAnonymizeEmail:
    def test_should_raise_if_email_is_not_a_string(self):
        with pytest.raises(DecoratorWrongUsage):
            AnonymizeLogic.anonymize_email(123)

    def test_should_return_none_if_email_is_none(self):
        assert AnonymizeLogic.anonymize_email(None) is None

    def test_should_return_anonymized_phone(self):
        assert (
            AnonymizeLogic.anonymize_email("lucas.carvalho@juntossomosmais.com.br")
            == "l*************@juntossomosmais.com.br"
        )

    def test_should_return_only_username_if_there_is_no_domain(self):
        assert AnonymizeLogic.anonymize_email("lucas.carvalho") == "l*************"


class TestAnonymizeAddressShouldNotBeReturned:
    def test_should_return_none(self):
        assert AnonymizeLogic.anonymize_address_should_not_be_returned("Av. Gomes de Carvalho") is None


class TestAnonymizeAddressShouldBeReturned:
    def test_should_return_the_same_data(self):
        assert AnonymizeLogic.anonymize_address_should_be_returned("São Paulo") == "São Paulo"
