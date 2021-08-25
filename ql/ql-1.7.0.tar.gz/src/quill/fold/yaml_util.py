from yaml import load, Loader
from .ns_util import ns_path, ns
from .site_yaml import SiteCI
from ..manifest.man import ssm
from sys import stderr
from pathlib import Path

__all__ = ["yaml2dict", "yaml_manifests", "get_yaml_manifest", "change_build_dir"]

YAML_FNAME = ".gitlab-ci.yml"


def yaml2dict(yaml_path):
    with open(yaml_path, "r") as f:
        return load(f, Loader=Loader)


def yaml_manifests(as_dicts=False, yaml_filename=YAML_FNAME):
    """
    Clone repos as per the manifest (`qu.ssm`)
    """
    ssm.check_manifest()
    df = ssm.repos_df.loc[:, ("domain", "local")]
    manifest_dict = {}
    for domain, local in df.values:
        if local:
            local_path = ns_path / domain
            yaml_path = local_path / yaml_filename
            d = yaml2dict(yaml_path)
            manifest_dict.update({domain: d})
        else:
            pass  # do not touch if not local (for now)
    if as_dicts:
        return manifest_dict
    else:
        layout_dict = {d: SiteCI(y) for d, y in manifest_dict.items()}
        return layout_dict


def get_yaml_manifest(domain, as_dicts=False, yaml_filename=YAML_FNAME):
    all_manifests = yaml_manifests(as_dicts=as_dicts, yaml_filename=yaml_filename)
    assert domain in all_manifests, f"No YAML manifest for '{domain=}'"
    return all_manifests.get(domain)


def change_build_dir(domain, new_name, mv=True, yaml_filename=YAML_FNAME):
    """
    For a given domain, change the directory its 'script' entry is configured
    to build from (i.e. the `subdirectory` variable in the
    `fold`⠶`site_yaml.Script.cfg` dict).

    If `mv` is `True`, the files in the current build directory will be moved
    into this new build directory. N.B. any "hidden" files whose filenames
    begin with `.` will not be moved if the current build directory is the
    top-level directory, as this would include for instance `.git/` and
    `.gitlab-ci.yml` which must be in the top-level directory to function.
    For this reason it is advised to always use a non-top-level directory
    as the build directory (to avoid having to figure out how to exclude some
    files from a directory move in the event of changing it at a later stage).
    """
    # move the files from the current build dir to the new build dir, either:
    # - simply rename the current build dir to `new_name`
    # - if no current build dir: `mkdir new_name` and `mv ./* {new_name}/`
    assert type(domain) is type(new_name) is str, f"'{domain}'/'{new_name}' aren't str"
    local_path = ns_path / domain
    yaml_path = local_path / yaml_filename
    assert yaml_path.exists(), f"No YAML file at '{yaml_path!=s}'"
    site_ci = get_yaml_manifest(domain, as_dicts=False, yaml_filename=yaml_filename)
    # If block to ensure any path error while moving files vetoes YAML modification
    if mv:
        current_build_dir = site_ci.pages.script.cfg.get(
            "subdirectory"
        )  # None if unset
        if current_build_dir:
            current_build_path = local_path / current_build_dir
            yaml_expect_msg = f"'{yaml_path=!s}' says {current_build_path=!s} exists"
            assert current_build_path.exists(), f"{yaml_expect_msg}, but it doesn't!"
            # otherwise `current_build_path` exists so just rename the directory
            current_bp_par = current_build_path.parent
            new_build_path = current_build_path.rename(current_bp_par / new_name)
            print(
                f"Moved build path for {domain} from '{current_build_dir}' "
                f"--> {new_build_path}",
                file=stderr,
            )
        else:
            # implicitly: `current_build_path` = `local_path`
            new_build_path = local_path / new_name
            assert not new_build_path.exists(), f"{new_build_path=!s} already exists!"
            new_build_path.mkdir()
            # do not move "hidden" files (those whose filenames begin with a period)
            movable_files = [x for x in local_path.iterdir() if not x.name.startswith(".")]
            for source in movable_files:
                if source.is_dir() and source.name == new_name:
                    continue  # cannot move the new directory into itself!
                dest = new_build_path / source.name
                source.replace(dest)
            print(f"Created build path for {domain} at {new_build_path}", file=stderr)
    # change build directory name in the yaml's script
    site_ci.pages.script.cfg.update({"subdirectory": Path(new_name)})
    # write the SiteCI as YAML to `.gitlab-ci.yml`
    with open(yaml_path, "w") as f:
        f.write(site_ci.as_yaml)
