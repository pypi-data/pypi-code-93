from __future__ import annotations

import logging
from typing import Optional

from .artifact import Artifact, _Base
from .artifact_type import ArtifactType
from .code_version import CodeVersion
from .git_version import GitVersion


class CodeVersionArtifact(Artifact):
    def __init__(self, code: CodeVersion, description: Optional[str] = None):
        self.artifactType = ArtifactType.CODE
        self.description = description
        self.code: CodeVersion = code

    @classmethod
    def create(
        cls,
        path: str = ".",
    ) -> Optional[CodeVersionArtifact]:
        """
        create an artifact based on the git information relative to the given local path.

        :param path: the path to look for the git repository
        :return: a CodeVersion of None if a git repository was not found.
        """
        git_version = GitVersion.create(path)
        if git_version is not None:
            return cls(CodeVersion(git_version))
        else:
            logging.warning(f"path {path} is not part of a git repository")
            return None

    @classmethod
    def create_from_github_uri(
        cls, uri: str, script_relative_path: Optional[str] = None, login_or_token=None, password=None, jwt=None
    ) -> Optional[CodeVersionArtifact]:
        """
        create an artifact based on the github information relative to the given URI and relative path.

        Note: The URi given can include the branch you are working on. otherwise, the default repository branch will be used.

        sample :
            https://github.com/my-organization/my-repository (no branch given so using default branch)
            https://github.com/my-organization/my-repository/tree/my-current-branch (branch given is my-current-branch)

        To access private repositories, you need to authenticate with your credentials.
        see https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/about-authentication-to-github

        :param uri: the uri of the repository with a specific branch if needed.
        :param script_relative_path:  the file that is executed
        :param login_or_token: real login or personal access token
        :param password: the password
        :param jwt: the Oauth2 access token
        :return:
        """
        git_version = GitVersion.create_from_github_uri(uri, script_relative_path, login_or_token, password, jwt)
        if git_version is not None:
            return cls(CodeVersion(git_version))
        else:
            logging.warning(f"path {script_relative_path} is not part of a git repository")
            return None

    def _get_delegate(self) -> _Base:
        return self.code
