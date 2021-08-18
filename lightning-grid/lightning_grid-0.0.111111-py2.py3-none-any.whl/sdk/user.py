from dataclasses import dataclass

from grid.sdk import env
from grid.sdk._gql.queries import get_user_basic_info


@dataclass(frozen=True)
class User:
    user_id: str
    username: str
    first_name: str
    last_name: str


@dataclass(frozen=True)
class SDKUser(User):
    email: str
    is_verified: bool
    is_blocked: bool
    completed_signup: bool

    @classmethod
    def from_logged_in_user(cls) -> "SDKUser":
        resp = get_user_basic_info()
        if not resp["isVerified"]:
            raise PermissionError(
                f"User account not yet verified. Verify your "
                f"account at {env.GRID_URL}/#/verification"
            )
        if not resp["completedSignup"]:
            raise PermissionError(
                f"You haven't yet completed registration. Please complete "
                f"registration at {env.GRID_URL}/#/registration"
            )
        if resp["isBlocked"]:
            raise PermissionError(
                f"Your account with username `{resp['username']}` has been "
                f"suspended. Please reach out to support at support@grid.ai"
            )

        return cls(
            user_id=resp["userId"],
            username=resp["username"],
            first_name=resp["firstName"],
            last_name=resp["lastName"],
            email=resp["email"],
            is_verified=resp["isVerified"],
            is_blocked=resp["isBlocked"],
            completed_signup=resp["completedSignup"],
        )
