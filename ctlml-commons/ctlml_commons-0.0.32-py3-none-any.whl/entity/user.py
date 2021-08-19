from dataclasses import dataclass
from typing import Dict, Optional

EXAMPLE: Dict[str, str] = {"username": "mh", "email": "mh@gmail", "pwd": "pwd", "mfa_code": "123"}


@dataclass(frozen=True)
class User:
    username: str
    email: str
    pwd: str
    mfa_code: Optional[str] = None


def main() -> None:
    user = User(**EXAMPLE)
    print(user)


if __name__ == "__main__":
    main()
