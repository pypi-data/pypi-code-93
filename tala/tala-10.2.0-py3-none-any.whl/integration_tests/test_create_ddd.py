import pytest

from tala.ddd.maker.ddd_maker import UnexpectedCharactersException

from .console_script_mixin import ConsoleScriptTestMixin


class TestCreateDDD(ConsoleScriptTestMixin):
    def test_create(self):
        self._when_creating_a_ddd(name="legal_name")
        self._then_result_is_successful()

    def _when_creating_a_ddd(self, name=None):
        self._create_ddd(name)

    def test_create_with_illegal_characters(self):
        self._when_creating_a_ddd_then_an_exception_is_raised(
            name="illegal-name",
            expected_exception=UnexpectedCharactersException,
            expected_pattern="Expected only alphanumeric ASCII and underscore characters in DDD name 'illegal-name', "
            "but found others"
        )

    def _when_creating_a_ddd_then_an_exception_is_raised(self, name, expected_exception, expected_pattern):
        with pytest.raises(expected_exception, match=expected_pattern):
            self._when_creating_a_ddd(name)

    def test_create_and_verify_with_default_language(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._when_verifying()
        self._then_result_is_successful()

    def test_create_and_verify_with_specified_language(self):
        self._given_created_ddd_with_specified_language(language="sv")
        with self._given_changed_directory_to_target_dir():
            self._when_verifying()
        self._then_result_is_successful()

    def _when_verifying(self):
        self._run_tala_with(["verify"])
