import os
from pathlib import Path
import time
import unicodedata

from ntscli_cloud_lib.automator import DeviceIdentifier
from xdg import XDG_CACHE_HOME

# Implementation libs
from ntsjson.log import logger


def _fs_safe_chars(text):
    """
    Strip out unicode characters that are potentially unsafe for the filesystem
    """
    numbers_and_letters_unicode_categories = {"L", "Lm", "Ll", "Lt", "Lu", "Lo", "N", "Nd", "Nl", "No"}
    return "".join(x for x in text if unicodedata.category(x) in numbers_and_letters_unicode_categories)


def _device_identifier_as_string(target: DeviceIdentifier):
    """
    Create a filesystem safe hash of a device identifier.

    :param target:
    :return:
    """
    if not target.rae:
        return ""
    device_id_string = ".".join(map(_fs_safe_chars, [elt for elt in [target.rae, target.esn, target.ip, target.serial] if elt is not None]))
    return f"{device_id_string}.json"


def path(target: DeviceIdentifier) -> Path:
    cache_dir = XDG_CACHE_HOME / "ntscli-client"
    if not cache_dir.exists():
        logger.debug("Creating test plan cache dir")
        os.makedirs(cache_dir, exist_ok=True)
    xdg_cache_file: Path = cache_dir / _device_identifier_as_string(target)
    yesterday = time.time() - (60 * 60 * 24 * 1)
    if xdg_cache_file.exists() and os.path.getmtime(xdg_cache_file) < yesterday:
        logger.info("Removing stale cached test plan from the cache.")
        try:
            xdg_cache_file.unlink()
        except OSError:
            pass
    return xdg_cache_file
