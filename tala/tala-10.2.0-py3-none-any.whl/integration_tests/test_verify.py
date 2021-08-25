from pathlib import Path

from tala.config import DddConfig
from .console_script_mixin import ConsoleScriptTestMixin


class TestVerifyIntegration(ConsoleScriptTestMixin):
    def setup(self):
        super(TestVerifyIntegration, self).setup()

    def test_that_verifying_boilerplate_ddd_succeeds(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._when_verifying()
        self._then_result_is_successful()

    def _when_verifying(self):
        self._run_tala_with(["verify"])

    def test_stdout_when_verifying_boilerplate_ddd(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala verify")
        self._then_stdout_matches(
            "^Verifying models for DDD 'test_ddd'.\n"
            r"\[eng\] Verifying grammar.\n"
            r"\[eng\] Finished verifying grammar.\n"
            "Finished verifying models for DDD 'test_ddd'.\n$"
        )

    def test_stdout_when_verifying_boilerplate_ddd_with_rasa_enabled(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_enabled_rasa()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala verify")
        self._then_stdout_matches(
            "^Verifying models for DDD 'test_ddd'.\n"
            r"\[eng\] Verifying grammar.\n"
            r"\[eng\] Finished verifying grammar.\n"
            "Finished verifying models for DDD 'test_ddd'.\n$"
        )

    def _given_enabled_rasa(self):
        self._set_in_config_file(Path(DddConfig.default_name()), "rasa_nlu", {"eng": {"url": "mock-url", "config": {}}})

    def test_stderr_when_verifying_boilerplate_ddd(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala verify --ignore-grammar-warnings")
        self._then_stderr_is_empty()

    def _then_stderr_is_empty(self):
        assert self._stderr == ""

    def test_verify_creates_no_build_folders(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala verify")
        self._then_there_are_no_build_folders()

    def _then_there_are_no_build_folders(self):
        ddd_folder = Path("test_root") / "test_ddd" / "grammar"
        build_folders = [path for path in ddd_folder.iterdir() if path.is_dir() and path.name.startswith("build")]
        assert not any(build_folders), "Expected no build folders but got {}".format(build_folders)

    def test_verify_creates_no_build_folders_with_rasa_enabled(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_enabled_rasa()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala verify")
        self._then_there_are_no_build_folders()

    def test_verify_returncode_with_schema_violation(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_schema_violation_in_ontology()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala verify")
        self._then_returncode_signals_error()

    def _given_schema_violation_in_ontology(self):
        self._replace_in_file(Path("ontology.xml"), "ontology", "hello")

    def _then_returncode_signals_error(self):
        assert self._process.returncode != 0

    def test_verify_stderr_with_schema_violation(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_schema_violation_in_ontology()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala verify")
        self._then_stderr_contains(
            "Expected ontology.xml compliant with schema but it's in violation: "
            "Element 'hello': "
            "No matching global declaration available for the validation root., line 2"
        )
