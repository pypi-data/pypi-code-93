__all__ = ["parse_man_node", "read_man"]

def parse_man_node(node, host="gitlab.com", hosting_at="gitlab.io"):
    """
    Parse the ['human-authored'] sub/domain name and ['slugged'] repo name prefix
    from the manifest (a list in MMD file format). Apex and subdomain addresses
    are treated the same way by this function.
    """
    colsv = node.contents.split(":")[:2]
    assert len(colsv) == 2, f"Expected 2 colon-separated values, got {len(colsv)} ({node})"
    domain, repo = colsv
    org = repo
    ref = f"git@{host}:{org}/{repo}.{hosting_at}.git"
    return domain, ref

def read_man(man):
    """
    Process a `DocList` in `.mmd` list format, i.e. with colon-sep. values,
    as `subdomain:group` [where group doubles as the repo name prefix for
    GitLab] beginning with the apex domain as a list header, and followed by
    subdomains to be applied to the apex domain).
    """
    assert man.list, "The manifest MMD should be a single list"
    repo_info = list(map(parse_man_node, man.list.all_nodes))
    return repo_info

def read_man_df(man):
    repo_info = read_man(man)
    df = man.as_df()
    git_addr = [x[1] for x in repo_info]
    df["git_url"] = git_addr
    return df
