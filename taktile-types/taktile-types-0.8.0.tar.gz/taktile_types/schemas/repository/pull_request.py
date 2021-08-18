"""Pull request related datastructures"""
from pydantic import UUID4, BaseModel


class PullRequest(BaseModel):
    """PullRequest.

    A data structure to hold a pull request
    """

    github_id: int
    url: str
    title: str
    github_number: int
    source_branch: str
    target_branch: str

    repository_id: UUID4
