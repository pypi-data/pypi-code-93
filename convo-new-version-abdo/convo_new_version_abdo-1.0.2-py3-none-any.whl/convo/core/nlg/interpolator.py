import re
import logging
from typing import Text, Dict, Union, Any, List

log = logging.getLogger(__name__)


def interpolate_txt(template: Text, values: Dict[Text, Text]) -> Text:
    """Interpolate values into templates with placeholders.

    Transform template tags from "{tag_name}" to "{0[tag_name]}" as described here:
    https://stackoverflow.com/questions/7934620/python-dots-in-the-name-of-variable-in-a-format-string#comment9695339_7934969
    Block characters, making sure not to allow:
    (a) newline in slot name
    (b) { or } in slot name

    Args:
        template: The piece of text that should be interpolated.
        values: A dictionary of keys and the values that those
            keys should be replaced with.

    Returns:
        The piece of text with any replacements made.
    """

    try:
        text_details = re.sub(r"{([^\n{}]+?)}", r"{0[\1]}", template)
        text_details = text_details.format(values)
        if "0[" in text_details:
            # regex replaced tag but format did not replace
            # likely cause would be that tag name was enclosed
            # in double curly and format func simply escaped it.
            # we don't want to return {0[SLOTNAME]} thus
            # restoring original value with { being escaped.
            return template.format({})

        return text_details
    except KeyError as e:
        log.exception(
            f"Failed to fill utterance template '{template}'. "
            f"Tried to replace '{e.args[0]}' but could not find "
            f"a value for it. There is no slot with this "
            f"name nor did you pass the value explicitly "
            f"when calling the template. Return template "
            f"without filling the template. "
        )
        return template


def fetch_interpolate(
    template: Union[List[Any], Dict[Text, Any], Text], values: Dict[Text, Text]
) -> Union[List[Any], Dict[Text, Any], Text]:
    """Recursively process template and interpolate any text keys.

    Args:
        template: The template that should be interpolated.
        values: A dictionary of keys and the values that those
            keys should be replaced with.

    Returns:
        The template with any replacements made.
    """
    if isinstance(template, str):
        return interpolate_txt(template, values)
    elif isinstance(template, dict):
        for k, v in template.items():
            if isinstance(v, dict):
                fetch_interpolate(v, values)
            elif isinstance(v, list):
                template[k] = [fetch_interpolate(i, values) for i in v]
            elif isinstance(v, str):
                template[k] = interpolate_txt(v, values)
        return template
    elif isinstance(template, list):
        return [fetch_interpolate(i, values) for i in template]
    return template
