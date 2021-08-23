import zope.interface
from .tools import DiffWrapper
from typing import Any

# ------------------------------------------------------------------------------


class DVCSInterface(zope.interface.Interface):
    """
        DVCS node interface
        all methods giving class hability to perfom actions on a DVCS repository

    """

    def update_to(self, revision: str) -> bool:
        pass

    def push_to(self, local_project: Any, target_project: Any,
                force_branch: bool) -> str:
        pass

    def pull_from(self, local_project: Any, source_project: Any) -> str:
        pass

    def pullable(self, local_project: Any, target_project: Any) -> bool:
        pass

    def pushable(self, local_project: Any, target_project: Any) -> bool:
        pass

    def get_content(self, revision: str, file_name: str) -> str:
        pass

    def get_release(self) -> str:
        pass

    def get_tags(self) -> list:
        pass

    def get_branches(self) -> list:
        pass

    def get_current_rev_hash(self) -> str:
        pass

    def get_last_logs_starting_from(self,
                                    start_from_this_hash_revision: str) -> tuple:
        pass

    def get_last_logs(self, nb_lines, branch_filter: str = None,
                      revision_filter: str = None) -> tuple:
        pass

    def get_file_content(self, file_name: str, revision: str) -> str:
        pass

    def get_initial_hash(self) -> str:
        pass

    def get_current_revision_description(self) -> dict:
        pass

    def get_revision_diff(self, revision: str) -> DiffWrapper:
        pass

    def get_revision_description(self, revision: str) -> dict:
        pass
