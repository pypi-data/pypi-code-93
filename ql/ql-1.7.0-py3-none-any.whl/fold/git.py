from subprocess import run
from . import cut
from .ns_util import ns_path, ns
from ..manifest.man import ssm
from sys import stderr
from git import Repo
from itertools import starmap

__all__ = [
    "clone",
    "source_manifest",
    "GitNews",
    "remote_push_manifest",
    "remote_pull_manifest",
]


def clone(url, as_name=None, wd=ns_path, update_man=True):
    command = ["git", "clone", url]
    if as_name:
        command.append(as_name)
    run(command, cwd=wd)
    ns.refresh()
    if update_man:
        ssm.check_manifest()
    return


def source_manifest():
    """
    Clone repos as per the manifest (`qu.ssm`)
    """
    df = ssm.repos_df.loc[:, ("domain", "git_url")]
    for domain, url in df.values:
        if (ns_path / domain).exists():
            continue  # simply do not touch for now
        try:
            clone(url, as_name=domain, update_man=False)
        except Exception as e:
            print(f"Failed on {url}: {e}", file=stderr)
    ssm.check_manifest()
    return


class GitNews:
    status_mapping = {
        "M": "Changed",
        "A": "Added",
        "D": "Deleted",
        "R": "Renamed",
        "C": "Copied",
        "U": "Updated",
    }

    def __init__(self, repo, abbreviate_at=2):
        """
        Given a repo object, generate the `git status --porcelain` output
        and parse it to give an overview of what changed.
        """
        self._news = repo.git.status("--porcelain")
        self.gnew = self._news.split("\n")
        self.status_lists = [*map(self.get_status, self.status_mapping)]
        self.abbreviate_at = abbreviate_at

    @property
    def status_labels(self):
        return [*self.status_mapping.values()]

    @property
    def all_reports(self):
        return [
            *starmap(self.report_status, zip(self.status_labels, self.status_lists))
        ]

    def __news_repr__(self):
        report = [". ".join(stats) for stats in self.all_reports if stats]
        return ". ".join(report)

    def get_status(self, letter_code):
        return [stat[3:] for stat in self.gnew if stat[0] == letter_code]

    def abbreviate_status(self, status):
        return [f"{len(status)} files"] if len(status) > self.abbreviate_at else status

    def report_status(self, action, status):
        "Returns e.g. 'Changed fileA.' or 'Changed 3 files.' as a string."
        status = self.abbreviate_status(status) if self.abbreviate_at else status
        return [f"{action} ".join(["", ", ".join(l)]) for l in [status] if status]


def remote_push_manifest(commit_msg=None, specific_domains=None, prebuild=True):
    """
    Run `git add --all` on each repo in the manifest (`qu.ssm`),
    i.e. apex and all subdomains, then `git commit -m "..."`
    where `...` is replaced by `commit_msg` or auto-generated
    if no commit is available.
    """
    if specific_domains is None:
        domains = ssm.repos_df.domain
    else:
        if type(specific_domains) is list:
            domains = specific_domains
        elif type(specific_domains) is str:
            domains = [specific_domains]
        else:
            raise TypeError(f"Unexpected type for {specific_domains=}")
    for domain in domains:
        repo_dir = ns_path / domain
        if not repo_dir.exists():
            print(f"Skipping '{repo_dir=!s}' (doesn't exist)", file=stderr)
            continue  # simply do not touch for now
        repo = Repo(repo_dir)
        repo.git.add("--all")
        if not repo.is_dirty():
            print(f"Skipping '{repo_dir=!s}' (working tree clean)", file=stderr)
            continue  # repo has no changes to untracked files, skip it
        if prebuild:
            cut.standup(domains_list=[domain])
            repo.git.add("--all")
        if commit_msg is None:
            news = GitNews(repo)
            commit_msg = news.__news_repr__()
        if commit_msg == "":
            msg = f"git repo stage added to at '{repo_dir=!s}'"
            raise ValueError("{msg} - aborting commit (empty commit message)")
        else:
            repo.git.commit("-m", commit_msg)
            print(f"Commit [{repo_dir=!s}] ⠶ {commit_msg}", file=stderr)
            origin = repo.remote(name="origin")
            origin.push()  # returned Push object does not seem to store useful info
            print(f"⇢ Pushing ⠶ {origin.name}", file=stderr)
    ssm.check_manifest()
    return


def remote_pull_manifest(specific_domains=None):
    """
    Run `git pull` on each repo in the manifest (`qu.ssm`),
    i.e. apex and all subdomains.

    No merge method is specified (unclear whether this will be necessary).

    See here if there are problems:
    https://stackoverflow.com/questions/36891470/how-to-pull-with-gitpython
    """
    if specific_domains is None:
        domains = ssm.repos_df.domain
    else:
        if type(specific_domains) is list:
            domains = specific_domains
        elif type(specific_domains) is str:
            domains = [specific_domains]
        else:
            raise TypeError(f"Unexpected type for {specific_domains=}")
    for domain in domains:
        print(f"Examining {domain}...", file=stderr)
        repo_dir = ns_path / domain
        if not repo_dir.exists():
            print(f"Skipping '{repo_dir=!s}' (doesn't exist)", file=stderr)
            continue  # simply do not touch for now
        repo = Repo(repo_dir)
        origin = repo.remote(name="origin")
        origin.pull()  # not checked if returned Pull object stores useful info
        print(f"⇢ Pulling ⠶ {origin.name}", file=stderr)
    ssm.check_manifest()
    return
