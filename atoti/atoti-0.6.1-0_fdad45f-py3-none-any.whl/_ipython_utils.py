from typing import Any, Mapping, Optional, Sequence, cast


def find_corresponding_top_level_variable_name(value: Any) -> Optional[str]:
    if not running_in_ipython():
        return None

    from IPython import get_ipython

    top_level_variables: Mapping[str, Any] = cast(Any, get_ipython()).user_ns

    for variable_name, variable_value in top_level_variables.items():
        is_regular_variable = not variable_name.startswith("_")
        if is_regular_variable and variable_value is value:
            return variable_name

    return None


def ipython_key_completions_for_mapping(mapping: Mapping[str, Any]) -> Sequence[str]:
    """Return IPython key completions for mapping."""
    return list(mapping.keys())


def running_in_ipython():
    """Test if the current session is running in IPython."""
    try:

        # pylint: disable = pointless-statement
        __IPYTHON__  # type: ignore
        return True
    except NameError:
        return False
