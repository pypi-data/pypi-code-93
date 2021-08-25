from configparser import ConfigParser

def git_to_https(uri):
    "Convert git URI (for a GitHub SSH repo) to https"
    assert uri.startswith("git"), f"No git SSH repo at {uri}"
    https = uri.split("@")[1].replace(":","/")
    https = "https://" + https[:https.rfind(".git")]
    return https

def parse_subdomain_url(ns_path, sd_subpath):
    """
    Process an individual subdomain for quill.fold.read_ns
    """
    subdomain = ns_path / sd_subpath
    sd_git_conf = subdomain / ".git" / "config"
    c = ConfigParser()
    with open(sd_git_conf, "r") as f:
        c.read_file(f)
    sd_url = git_to_https(c.get('remote "origin"', "url"))
    return sd_url
