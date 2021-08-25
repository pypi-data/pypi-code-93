from pandas import merge, concat
from ..manifest.man import ssm
from ..manifest.namings import alias_df
from ..fold.ns_util import ns_path

__all__ = ["write_man_README"]

def process_df_row(r, remote_template="https://gitlab.com/{}/{}.gitlab.io"):
    namespaced = f"{r.namespace} ⠶ {r.alias if r.alias else r.domain}"
    remote_url = remote_template.format(*[r.repo_name]*2)
    return f"- `{r.domain}`: [{namespaced}]({remote_url})"

def write_man_README(title="spin.systems"):
    """
    Store a representation with links from the manifest `qu.ssm`
    """
    df = merge(alias_df, ssm.as_df())
    domain_vals = ["cal", "log", "conf", "pore", "ocu", "arc", "qrx", "erg", "opt"]
    domain_vals += ["poll", "arb", "reed", "noto", "plot", "doc", "labs"]
    df = concat([df.query(f"domain == '{d}'") for d in domain_vals])
    list_entries = list(map(lambda r: process_df_row(r[1]), df.iterrows()))
    ss_url = "https://gitlab.com/{}/{}.gitlab.io".format(*["spin.systems"]*2)
    README_md_lines = [f"# {title}", "", f"spin.systems: [`ss`]({ss_url})", ""]
    README_md_lines += list_entries
    README_md = "\n".join(README_md_lines) + "\n"
    with open(ns_path / "README.md", "w") as f:
        f.write(README_md)
    return
