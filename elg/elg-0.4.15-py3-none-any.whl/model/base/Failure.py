from typing import List

from pydantic import BaseModel

from .StatusMessage import StatusMessage


class Failure(BaseModel):
    """
    Details of a failed task

    Attributes
    ----------
    errors: List[StatusMessage]: list of status messages describing failure
    """

    errors: List[StatusMessage]
