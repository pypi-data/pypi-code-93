import json
import os
from datetime import datetime
from pathlib import Path
from subprocess import DEVNULL, check_output  # nosec
from typing import Tuple

from ._compatibility import check_java_version

_ATOTI_JAVA_HOME_ENVIRONMENT_VARIABLE = "ATOTI_JAVA_HOME"
_JAVA_HOME_ENVIRONMENT_VARIABLE = "JAVA_HOME"

JAR_PATH = Path(__file__).parent / "data" / "atoti.jar"


def get_java_path() -> Path:
    """Get the path to Java.

    Uses the first available of:

    * $ATOTI_JAVA_HOME/bin/java
    * jdk4py
    * $JAVA_HOME/bin/java
    * java
    """
    if _ATOTI_JAVA_HOME_ENVIRONMENT_VARIABLE in os.environ:
        return Path(os.environ[_ATOTI_JAVA_HOME_ENVIRONMENT_VARIABLE]) / "bin" / "java"
    try:
        from jdk4py import JAVA  # type: ignore

        return JAVA
    except ImportError:
        java_path = (
            Path(os.environ[_JAVA_HOME_ENVIRONMENT_VARIABLE]) / "bin" / "java"
            if _JAVA_HOME_ENVIRONMENT_VARIABLE in os.environ
            else Path("java")
        )
        return java_path


def retrieve_info_from_jar() -> Tuple[datetime, bool]:
    """Retrieve info from the embedded JAR."""
    java_path = str(get_java_path())
    check_java_version(java_path, [11])
    output = str(
        check_output([java_path, "-jar", str(JAR_PATH), "--info"], stderr=DEVNULL),
        "utf-8",
    )
    try:
        info = json.loads(output.strip().splitlines()[-1])
        return (
            datetime.fromtimestamp(int(info["licenseEndDate"]) / 1000),
            info["isCommunityLicense"],
        )
    except Exception as err:
        raise RuntimeError(
            f"Could not retrieve info about the embedded JAR output: {output}"
        ) from err
