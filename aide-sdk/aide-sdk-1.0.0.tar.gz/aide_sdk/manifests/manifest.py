# pylint: disable=no-member
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from json import JSONDecodeError

from dataclasses_json import dataclass_json

from aide_sdk.utils.exceptions import ManifestNotFoundError, ManifestNotValidError

__manifest__ = None


def set_manifest(manifest: Manifest):
    global __manifest__
    __manifest__ = manifest


def load(manifest_path: str = None) -> Manifest:
    """Load a model's configuration rom its associated manifest file

    :return:
    manifest: 'Manifest' - The configuration of the model parsed from its
                           manifest file
    """
    global __manifest__

    if __manifest__ is not None:
        return __manifest__

    try:
        manifest_path = os.environ.get("MANIFEST_PATH") or manifest_path or "manifest.json"
        with open(manifest_path, mode='r') as file:
            loaded_manifest = json.load(file)
            __manifest__ = Manifest.from_dict(loaded_manifest)
            return __manifest__
    except FileNotFoundError:
        raise ManifestNotFoundError()
    except JSONDecodeError:
        raise ManifestNotValidError()


@dataclass_json
@dataclass
class Manifest:
    model_name: str
    model_version: str
    model_description: str
    predicate: str
    mode: str

    def get_queue_name(self):
        return f"{self.model_name}-{self.model_version}"

    @property
    def model_uid(self):
        return f"{self.model_name}/{self.model_version}"
