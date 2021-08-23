from typing import Any, Dict


def merge_dicts(
    source_dict: Dict[Any, Any],
    target_dict: Dict[Any, Any],
) -> None:
    """Merge source dictionary into target.

    Example:
        # from pyproject.toml

        [environment]
        test = true
        project.foo = "bar"
        project.x = "a"

        [environment.local]
        project.bar = "foo"
        project.x = "b"
        project.db.name = "test"

    Expected data for ENVIRONMENT=local:
        settings.to_dict = {
            "test": True,
            "project": {
                "foo": "bar,
                "project": {
                    "x": "b"
                },
                "bar": "foo",
                "db": {
                    "name": "test"
                },
            }
        }
    :param source_dict: The Source dictionary
    :param target_dict: The Target dictionary, which will me merged
    :current_key: Current Source Dictionary Key
    """

    def _merge_dicts(source, target, current_key):
        if isinstance(source[current_key], dict):
            if not target.get(current_key):
                target[current_key] = {}
            for k in source[current_key]:
                if not target[current_key].get(k):
                    target[current_key][k] = {}
                _merge_dicts(source[current_key], target[current_key], k)
        else:
            target[current_key] = source[current_key]

    for key in source_dict.keys():
        _merge_dicts(source_dict, target_dict, key)
