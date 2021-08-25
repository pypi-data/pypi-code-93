from pathlib import Path

import pytest

from tala.config import BackendConfig, DddConfig, DeploymentsConfig

from .console_script_mixin import ConsoleScriptTestMixin


class TestConfigFileIntegration(ConsoleScriptTestMixin):
    EXPECTED_CONFIGS = {
        BackendConfig: {
            "active_ddd": "my_ddd",
            "ddds": ["my_ddd"],
            "supported_languages": ["eng"],
            "asr": "none",
            "use_recognition_profile": False,
            "repeat_questions": True,
            "use_word_list_correction": False,
            "rerank_amount": 0.2,
            "inactive_seconds_allowed": 7200,
            "response_timeout": 2.5,
            "confidence_prediction_thresholds": {"ACKNOWLEDGE": 0.8, "CHECK": 0.6, "TRUST": 1.0},
            "confidence_thresholds": {"ACKNOWLEDGE": 0.15, "CHECK": 0.1, "TRUST": 0.3}
        },
        DddConfig: {
            "use_rgl": False,
            "use_third_party_parser": False,
            "device_module": None,
            "word_list": "word_list.txt",
            "rasa_nlu": {}
        },
        DeploymentsConfig: {
            "dev": "https://127.0.0.1:9090/interact"
        }
    }

    EXPECTED_PARAMETERISED_CONFIGS = {
        BackendConfig: {
            "active_ddd": "my_ddd",
            "ddds": ["my_ddd"],
            "supported_languages": ["sv"],
            "asr": "none",
            "use_recognition_profile": False,
            "repeat_questions": True,
            "use_word_list_correction": False,
            "rerank_amount": 0.2,
            "inactive_seconds_allowed": 7200,
            "response_timeout": 2.5,
            "confidence_prediction_thresholds": {"ACKNOWLEDGE": 0.8, "CHECK": 0.6, "TRUST": 1.0},
            "confidence_thresholds": {"ACKNOWLEDGE": 0.15, "CHECK": 0.1, "TRUST": 0.3}
        }
    }

    @pytest.mark.parametrize(
        "ConfigClass,command", [(BackendConfig, "create-backend-config my_ddd"), (DddConfig, "create-ddd-config"),
                                (DeploymentsConfig, "create-deployments-config")]
    )
    def test_create_config_without_path(self, ConfigClass, command):
        self._when_running_command(f"tala {command}")
        self._then_config_contains(ConfigClass, ConfigClass.default_name(), self.EXPECTED_CONFIGS[ConfigClass])

    @pytest.mark.parametrize(
        "ConfigClass,command", [(BackendConfig, "create-backend-config my_ddd")]
    )
    def test_create_parameterised_config(self, ConfigClass, command):
        self._when_running_command(f"tala {command} -l sv")
        self._then_config_contains(ConfigClass, ConfigClass.default_name(),
                                   self.EXPECTED_PARAMETERISED_CONFIGS[ConfigClass])

    def _then_config_contains(self, ConfigClass, name, expected_config):
        actual_config = ConfigClass(name).read()
        assert expected_config == actual_config

    @pytest.mark.parametrize(
        "ConfigClass,command", [(BackendConfig, "create-backend-config my_ddd"), (DddConfig, "create-ddd-config"),
                                (DeploymentsConfig, "create-deployments-config")]
    )
    def test_create_config_with_path(self, ConfigClass, command):
        self._when_running_command(f"tala {command} --filename my_ddd.config.json")
        self._then_config_contains(ConfigClass, "my_ddd.config.json", self.EXPECTED_CONFIGS[ConfigClass])

    @pytest.mark.parametrize(
        "name,command", [
            ("backend", "create-backend-config mock_ddd"),
            ("DDD", "create-ddd-config"),
            ("deployments", "create-deployments-config"),
        ]
    )
    def test_exception_raised_if_config_file_already_exists(self, name, command):
        self._given_config_was_created_with("tala {} --filename test.config.json".format(command))
        self._when_running_command("tala {} --filename test.config.json".format(command))
        self._then_stderr_contains(
            "Expected to be able to create {} config file 'test.config.json' but it already exists.".format(name)
        )

    def _given_config_was_created_with(self, command):
        self._run_command(command)

    @pytest.mark.parametrize(
        "command", [
            "create-backend-config mock_ddd",
            "create-ddd-config",
            "create-deployments-config",
        ]
    )
    def test_config_file_not_overwritten(self, command):
        self._given_file_contains("test.config.json", "unmodified_mock_content")
        self._when_running_command("tala {} --filename test.config.json".format(command))
        self._then_file_contains("test.config.json", "unmodified_mock_content")

    @pytest.mark.parametrize("command", [
        "tala verify --config non_existing_config.json",
    ])
    def test_missing_config_causes_constructive_error_message(self, command):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command(command)
            self._then_stderr_contains_constructive_error_message_for_missing_backend_config("non_existing_config.json")

    @pytest.mark.parametrize("command", [
        "tala verify",
    ])
    def test_missing_parent_backend_config_causes_constructive_error_message(self, command):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._given_config_overrides_missing_parent(Path(BackendConfig.default_name()))
            self._when_running_command(command)
            self._then_stderr_contains_constructive_error_message_for_missing_backend_config("missing_parent.json")

    @pytest.mark.parametrize("command", [
        "tala verify",
    ])
    def test_missing_parent_ddd_config_causes_constructive_error_message(self, command):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_config_overrides_missing_parent(Path(DddConfig.default_name()))
        with self._given_changed_directory_to_target_dir():
            self._when_running_command(command)
            self._then_stderr_contains_constructive_error_message_for_missing_ddd_config("missing_parent.json")
