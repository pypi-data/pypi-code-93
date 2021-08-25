from ...fold.ns_util import ns_path
from git import Repo

def _has_clean_wt(domain, add_before_check=True):
    """
    Helper function (TODO: move to a dedicated git module)
    """
    repo_dir = ns_path / domain
    assert repo_dir.exists(), f"{repo_dir=!s} in namespace but doesn't exist"
    repo = Repo(repo_dir)
    if add_before_check:
        repo.git.add("--all")
    is_clean = not repo.is_dirty()
    return is_clean
