"""Repository related datastructures"""
import typing as t

from pydantic import UUID4, BaseModel

from taktile_types.enums.repository.access import AccessKind
from taktile_types.schemas.repository.pull_request import PullRequest


class Repository(BaseModel):
    """A repository"""

    id: UUID4
    name: str
    full_name: str
    repository_id: int
    private: bool
    installation_id: UUID4
    default_branch: t.Optional[str] = None
    description: t.Optional[str] = None

    def get_principal_and_name(self) -> t.Tuple[str, str]:
        """get_principal_and_name.
        Retrieve principal and name of a repository. E.g.
        "taktile-org/sample-repo" -> "taktile-org", "sample-repo"

        Returns
        -------
        t.Tuple[str, str] - principal, name

        """
        principal_and_name = self.full_name.split("/")
        if len(principal_and_name) != 2:
            raise ValueError(
                f"Couldn't figure out principal and name from {self.full_name}"
            )
        return principal_and_name[0], principal_and_name[1]


class RepositoryExtended(Repository):
    """Repository with access and PR information"""

    access: AccessKind
    pull_requests: t.List[PullRequest]
