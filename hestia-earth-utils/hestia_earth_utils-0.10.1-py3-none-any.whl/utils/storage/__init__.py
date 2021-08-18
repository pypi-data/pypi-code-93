from ._s3_client import _get_bucket, _load_from_bucket, _exists_in_bucket
from ._azure_client import _get_container, _load_from_container, _exists_in_container


def _load_from_storage(filepath: str, glossary: bool = False):
    if _get_bucket(glossary):
        return _load_from_bucket(_get_bucket(glossary), filepath)
    if _get_container(glossary):
        return _load_from_container(_get_container(glossary), filepath)
    raise ImportError


def _exists(filepath: str):
    if _get_bucket():
        return _exists_in_bucket(_get_bucket(), filepath)
    if _get_container():
        return _exists_in_container(_get_container(), filepath)
    raise ImportError
