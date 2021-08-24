import json
import os
import tempfile

from click import ClickException
import pytest

from anyscale import credentials


def test_validate_credential() -> None:
    with pytest.raises(ClickException):
        credentials._validate_credential("abc")

    with pytest.raises(ClickException):
        credentials._validate_credential("")

    # Should not raise an exception.
    credentials._validate_credential("sss_abcdefghjijklmnop")


def test_credentials_chose_environ_over_folder() -> None:
    old_environ = os.environ.copy()
    try:
        os.environ["ANYSCALE_CLI_TOKEN"] = "sss_os_environ"
        with tempfile.NamedTemporaryFile("w") as temp_credentials_file:
            temp_credentials_file.write(
                json.dumps({"cli_token": "sss_file_credential"})
            )
            temp_credentials_file.flush()
            credentials.CREDENTIALS_FILE = temp_credentials_file.name
            assert credentials.load_credentials() == "sss_os_environ"
    finally:
        os.environ = old_environ  # type: ignore
