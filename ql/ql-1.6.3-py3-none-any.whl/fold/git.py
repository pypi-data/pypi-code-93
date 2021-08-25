from subprocess import run
from .ns_util import ns_path, ns
from ..manifest.man import ssm
from sys import stderr
from git import Repo

__all__ = ["clone", "source_manifest", "git_news", "remote_push_manifest", "remote_pull_manifest"]


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


def git_news(repo, abbreviate_at=2):
    """
    Given a repo object, generate the `git status --porcelain` output
    and parse it to give an overview of what changed.
    """
    gitnews = repo.git.status("--porcelain")
    gnew = gitnews.split("\n")
    status_lists = [
        mods := [stat[3:] for stat in gnew if stat[0] == "M"],
        adds := [stat[3:] for stat in gnew if stat[0] == "A"],
        dels := [stat[3:] for stat in gnew if stat[0] == "D"],
        rens := [stat[3:] for stat in gnew if stat[0] == "R"],
        cops := [stat[3:] for stat in gnew if stat[0] == "C"],
        upds := [stat[3:] for stat in gnew if stat[0] == "U"],
    ]
    if abbreviate_at:
        mods = [f"{len(mods)} files"] if len(mods) > abbreviate_at else mods
        adds = [f"{len(adds)} files"] if len(adds) > abbreviate_at else adds
        dels = [f"{len(dels)} files"] if len(dels) > abbreviate_at else dels
        rens = [f"{len(rens)} files"] if len(rens) > abbreviate_at else rens
        cops = [f"{len(cops)} files"] if len(cops) > abbreviate_at else cops
        upds = [f"{len(upds)} files"] if len(upds) > abbreviate_at else upds
    # iterate over the status lists, joining them with commas (except if already
    # string-ified by the abbreviation block above)
    all_reports = [
        modreport := ["Changed ".join(["", ", ".join(l)]) for l in [mods] if mods],
        addreport := ["Added ".join(["", ", ".join(l)]) for l in [adds] if adds],
        delreport := ["Deleted ".join(["", ", ".join(l)]) for l in [dels] if dels],
        renreport := ["Renamed ".join(["", ", ".join(l)]) for l in [rens] if rens],
        copreport := ["Copied ".join(["", ", ".join(l)]) for l in [cops] if cops],
        updreport := ["Updated ".join(["", ", ".join(l)]) for l in [upds] if upds],
    ]
    report = [". ".join(stats) for stats in all_reports if stats]
    news = ". ".join(report)
    return news


def remote_push_manifest(commit_msg=None, specific_domains=None):
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
            continue # repo has no changes to untracked files, skip it
        if commit_msg is None:
            commit_msg = git_news(repo)
        if commit_msg == "":
            warn_msg = f"Warning: git repo stage added to at '{repo_dir=!s}'"
            raise ValueError("{warn_msg} - aborting commit (empty commit message)")
        else:
            repo.git.commit("-m", commit_msg)
            print(f"Commit [{repo_dir=!s}] ⠶ {commit_msg}", file=stderr)
            origin = repo.remote(name="origin")
            origin.push() # returned Push object does not seem to store useful info
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
        origin.pull() # not checked if returned Pull object stores useful info
        print(f"⇢ Pulling ⠶ {origin.name}", file=stderr)
    ssm.check_manifest()
    return
