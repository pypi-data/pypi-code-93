from pydantic import BaseModel

from .StatusMessage import StatusMessage


class Progress(BaseModel):
    """
    Details of an in progress task

    Attributes
    ----------
    percent (float, required): completion percentage
    message (StatusMessage, optional): message describing progress report
    """

    percent: float
    message: StatusMessage = None
