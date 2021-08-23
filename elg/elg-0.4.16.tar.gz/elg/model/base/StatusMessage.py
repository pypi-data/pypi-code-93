from typing import Dict, List

from pydantic import BaseModel


class StatusMessage(BaseModel):
    """
    Represents a single status message, in a form amenable to internationalisation.

    Each message contains a code, which can be looked up in a list to find the actual text in any of the available
    languages.  The text can contain numbered placeholders of the form <code>{0}</code>, which are filled in with values
    specified in the "params" property. The "text" property provides a single fallback text to be used if the specified
    code cannot be found in the lookup table.

    Attributes
    ----------
    code: (str, required) status code to be found in lookup table
    params: (List[str], required) values to fill in message placeholder
    text: (str, requored) fallback text to be used if specified code cannot be found in lookup table
    detail: (Dict, optional) arbitrary further details that don't need translation (e.g: stacktrace)
    """

    code: str
    params: List[str]
    text: str
    detail: Dict = None
