import collections
import json
import os
import re


try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

from pkg_resources import parse_version


def version_info(value):
    return tuple(int(i) for i in value.split(".") if i.isdigit())


__version__ = "1.1.4"
__title__ = "pgdoc-datatype-parser"

PG_RELEASE_MIN_VERSION = (6, 3)
PG_GH_RELEASES_URL = "https://api.github.com/repos/postgres/postgres/tags"
PG_RELEASES_JSON_FILEPATH = os.path.join(os.path.dirname(__file__), "pg-releases.json")
PG_DT_DOC_FILE_URLSCHEMA = (
    "https://raw.githubusercontent.com/postgres/"
    "postgres/{commit_id}/doc/src/sgml/datatype.sgml"
)


class InvalidReleaseVersion(ValueError):
    pass


def pg_release_name_to_version(release_name):
    mayor = re.search(r"REL_{0,1}(\d+)", release_name).group(1)

    minor_match = re.search(r"\d+_(\d+)_", release_name)
    if minor_match is not None:
        minor = minor_match.group(1)
    else:
        minor = None

    micro_match = re.search(r"(\d+)$", release_name)
    if micro_match is not None:
        micro = micro_match.group(1)
    else:
        micro = ""

    rc_match = re.search(r"_([A-Z]+)", release_name)
    if rc_match is not None:
        rc = rc_match.group(1)
        if len(rc) > 2:
            rc = rc[0].lower()
        else:
            rc = rc.lower()
    else:
        rc = ""

    if minor is None:
        return f"{mayor}.{micro}{rc}"
    return f"{mayor}.{minor}.{micro}{rc}"


def build_pg_releases_json_file(filepath=None):
    filepath = filepath if filepath else PG_RELEASES_JSON_FILEPATH
    if os.path.exists(filepath):
        raise OSError("Previous PostgreSQL releases file '%s' exists." % filepath)

    github_token = os.environ.get("GITHUB_TOKEN")

    content = {}
    # Github API pagination
    _last_page, _current_page = (float("inf"), 1)
    while _current_page <= _last_page:
        url = "%s?per_page=100&page=%d" % (PG_GH_RELEASES_URL, _current_page)
        req = Request(url)
        if github_token:
            req.add_header("Authorization", "token %s" % github_token)
        res = urlopen(req)

        # Discover last page
        if _last_page == float("inf"):
            link_header = res.getheader("link")
            _last_page = int(
                re.search(r"[^_]page=(\d+)", link_header.split(",")[-1]).group(1)
            )

        # Parse releases
        for release in json.loads(res.read()):
            if not release["name"].startswith("REL"):
                continue
            version = pg_release_name_to_version(release["name"])
            _version_info = version_info(version)
            if _version_info < PG_RELEASE_MIN_VERSION:
                continue
            content[version] = release["commit"]["sha"]
        _current_page += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json.dumps(content))
    return content


def versions(pg_releases_filepath=None):
    pg_releases_filepath = (
        pg_releases_filepath if pg_releases_filepath else PG_RELEASES_JSON_FILEPATH
    )
    decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
    with open(pg_releases_filepath, encoding="utf-8") as f:
        releases = decoder.decode(f.read())
    return list(releases.keys())


def latest_version(pg_releases_filepath=None):
    _versions = versions(pg_releases_filepath=pg_releases_filepath)[:15]
    _latest = parse_version(_versions[0])
    response = _versions[0]
    for version in _versions:
        _parsed_version = parse_version(version)
        if _parsed_version > _latest:
            _latest = _parsed_version
            response = version
    return response


def commit_from_release(version="latest", pg_releases_filepath=None):
    pg_releases_filepath = (
        pg_releases_filepath if pg_releases_filepath else PG_RELEASES_JSON_FILEPATH
    )
    if not os.path.exists(pg_releases_filepath):
        raise FileNotFoundError(
            "PostgreSQL releases file '%s' does not exists." % (pg_releases_filepath)
        )

    if version == "latest":
        pg_releases_filepath = (
            pg_releases_filepath if pg_releases_filepath else PG_RELEASES_JSON_FILEPATH
        )
        decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
        with open(pg_releases_filepath, encoding="utf-8") as f:
            releases = decoder.decode(f.read())
        commit = releases[list(releases.keys())[0]]
    else:
        with open(pg_releases_filepath, encoding="utf-8") as f:
            releases = json.loads(f.read())
        if version not in releases:
            for i in range(2 - version.count(".")):
                version += ".0"
                if version in releases:
                    break
        if version not in releases:
            for j in range(version.count(".")):
                if not version.endswith(".0"):
                    break
                version = ".".join(version.split(".")[:-1])
                if version in releases:
                    break
        if version not in releases:
            raise InvalidReleaseVersion(
                "Version '%s' is not a valid PostgreSQL release." % (version)
            )
        commit = releases[version]
    return commit


def _clean_entry(value):
    response, _inside_tag, _last_c_space = ("", False, False)
    for c in value:
        if c == "<":
            _inside_tag = True
            continue
        elif c == ">" and _inside_tag:
            _inside_tag = False
            continue
        else:
            if not _inside_tag:
                if c == " ":
                    if not _last_c_space:
                        response += c
                        _last_c_space = True
                    continue
                response += c
                _last_c_space = False
    return response


def parse_datatypes(sgml_content):
    _inside_datatypes_table, _inside_tbody, n_entry, _current_dt = (
        False,
        False,
        0,
        None,
    )
    response = {}

    lines = sgml_content.splitlines()
    for i, line in enumerate(lines):
        if not _inside_datatypes_table and 'id="datatype-table"' in line:
            _inside_datatypes_table = True
            continue
        elif not _inside_tbody and "<tbody>" in line:
            _inside_tbody = True
            continue
        elif _inside_tbody and "<entry>" in line:
            n_entry += 1
            if "</entry>" not in line and "</type>" not in line:
                line += lines[i + 1]
            value_match = re.search(r"<type>(.*)</type>", line)
            if value_match is None:
                value_match = re.search(r"<entry>(.*)</entry>", line)

            # Remove XML tags, múltiple continue spaces...
            value = _clean_entry(value_match.group(1))

            if n_entry == 1:
                response[value] = {}
                _current_dt = value
            elif n_entry == 2:
                aliases = value or None
                if aliases and "," in aliases and "[" not in aliases:
                    aliases = aliases.split(",")
                response[_current_dt]["aliases"] = aliases
            elif n_entry == 3:
                response[_current_dt]["description"] = value
                n_entry = 0
                _current_dt = None
        elif _inside_tbody and "</tbody>" in line:
            break
    return response


def pgdoc_datatypes(version="latest", pg_releases_filepath=None):
    commit = commit_from_release(
        version=version, pg_releases_filepath=pg_releases_filepath
    )

    url = PG_DT_DOC_FILE_URLSCHEMA.replace("{commit_id}", commit)
    return parse_datatypes(urlopen(url).read().decode("utf-8"))
