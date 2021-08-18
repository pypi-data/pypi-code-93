# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Module for performing bulk queries on the mod database and repositories
"""

import re
import sys
from collections import defaultdict
from collections.abc import Container
from typing import (
    AbstractSet,
    Any,
    DefaultDict,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

from portmodlib.atom import Atom, FQAtom, atom_sat
from portmodlib.colour import blue, bright, green, lblue, lgreen, red, yellow
from portmodlib.l10n import l10n
from portmodlib.usestr import parse_usestr

from .config import get_config
from .config.mask import is_masked
from .config.use import get_use, get_use_expand, use_reduce
from .download import get_total_download_size
from .globals import env
from .loader import load_all, load_all_installed, load_installed_pkg, load_pkg
from .pybuild import Pybuild
from .repo import get_repo
from .repo.metadata import get_global_use, get_package_metadata, get_use_expand_values
from .util import get_newest


def get_maintainer_string(maintainers: Union[List[Any], Any]) -> str:
    def list_maintainers_to_human_strings(maintainers: List[Any]) -> str:
        """return the list of maintainers as a human readible string"""
        result = ""
        for maintainer_id in range(len(maintainers)):
            maintainer = str(maintainers[maintainer_id])
            if maintainer_id >= len(maintainers) - 1:  # the last
                result += maintainer
            elif maintainer_id >= len(maintainers) - 2:  # the second last
                result += maintainer + " and "
            else:
                result += maintainer + ", "
        return result

    if not isinstance(maintainers, list):
        maintainers = [maintainers]

    return list_maintainers_to_human_strings(maintainers)


def print_depgraph(
    mod: Pybuild, level: int, level_limit: int, seen: AbstractSet[Pybuild] = frozenset()
) -> int:
    """
    Recursively prints the dependency graph for the given mod.

    Note that use conditionals and or statements are ignored.
    This prints out all possible dependencies, not actual dependencies.
    """
    if level > level_limit:
        return level - 1

    deps = parse_usestr(mod.DEPEND + " " + mod.RDEPEND, token_class=Atom)
    max_level = level

    new_seen = set(seen)

    def print_token(token, conditional=None):
        atom = Atom(token)
        mod = get_newest(load_pkg(atom))
        enabled, _ = get_use(mod)

        def colour(flag):
            if flag.rstrip("?").lstrip("-!") in enabled:
                return bright(red(flag))
            return bright(blue(flag))

        use = map(colour, atom.USE)
        use_str = ""
        if atom.USE:
            use_str = f'[{" ".join(use)}]'

        if conditional:
            dep = f"( {conditional} ( {atom.strip_use()} ) ) "
        else:
            dep = f"({atom.strip_use()}) "

        print(" " * (level + 1) + f"-- {bright(green(mod.ATOM.CPF))} " + dep + use_str)
        if mod in new_seen:
            print(" " * level + "-- " + l10n("omit-already-displayed-tree"))
            return level

        new_seen.add(mod)
        return print_depgraph(mod, level + 1, level_limit, new_seen)

    for token in deps:
        if isinstance(token, list):
            if token[0] == "||":
                for inner_token in token[1:]:
                    max_level = max(level, print_token(inner_token))
            elif token[0].endswith("?"):
                for inner_token in token[1:]:
                    max_level = max(level, print_token(inner_token, token[0]))
            else:
                for inner_token in token:
                    max_level = max(level, print_token(inner_token))
        else:
            max_level = max(level, print_token(token))

    return max_level


def str_strip(value: str) -> str:
    return re.sub("(( +- +)|(:))", "", value)


def str_squelch_sep(value: str) -> str:
    return re.sub(r"[-_\s]+", " ", value)


def query(
    fields: Union[str, Iterable],
    value: str,
    strip: bool = False,
    squelch_sep: bool = False,
    insensitive: bool = False,
    installed: bool = False,
) -> Generator[Pybuild, None, None]:
    """
    Finds mods that contain the given value in the given field
    """

    def func(val: str) -> str:
        result = val
        if insensitive:
            result = result.lower()
        if strip:
            result = str_strip(result)
        if squelch_sep:
            result = str_squelch_sep(result)
        return result

    search = func(value)

    if not installed:
        mods = load_all()
    else:
        mods = load_all_installed()

    for mod in mods:
        if isinstance(fields, str):
            if (
                hasattr(mod, fields)
                and isinstance(getattr(mod, fields), Container)
                and search in func(getattr(mod, fields))
            ):
                yield mod
        else:
            if any(
                hasattr(mod, field) and search in func(getattr(mod, field))
                for field in fields
            ):
                yield mod


def query_depends(atom: Atom, all_mods=False) -> List[Tuple[FQAtom, str]]:
    """
    Finds mods that depend on the given atom
    """
    if all_mods:
        mods = load_all()
    else:
        mods = load_all_installed()

    depends = []
    for mod in mods:
        if not all_mods:
            enabled, disabled = get_use(mod)
            atoms = use_reduce(
                mod.RDEPEND, enabled, disabled, token_class=Atom, flat=True
            )
        else:
            atoms = use_reduce(mod.RDEPEND, token_class=Atom, matchall=True, flat=True)

        for dep_atom in atoms:
            if dep_atom != "||" and atom_sat(dep_atom, atom):
                depends.append((mod.ATOM, dep_atom))
    return depends


def get_flag_string(
    name: Optional[str],
    enabled: Iterable[str],
    disabled: Iterable[str],
    installed: Optional[AbstractSet[str]] = None,
    *,
    verbose: bool = True,
    display_minuses=True,
):
    """
    Displays flag configuration

    Enabled flags are displayed as blue
    If the installed flag list is passed, flags that differ from the
    installed set will be green
    if name is None, the name prefix will be omitted and no quotes will
    surround the flags
    """

    def disable(string: str) -> str:
        if display_minuses:
            return "-" + string
        return string

    flags = []
    for flag in sorted(enabled):
        if installed is not None and flag not in installed:
            flags.append(bright(lgreen(flag)))
        elif verbose:
            flags.append(red(bright(flag)))

    for flag in sorted(disabled):
        if installed is not None and flag in installed:
            flags.append(bright(lgreen(disable(flag))))
        elif verbose:
            if display_minuses:
                flags.append(blue(disable(flag)))
            else:
                flags.append(lblue(disable(flag)))

    inner = " ".join(flags)

    if not flags:
        return None

    if name:
        return f'{name}="{inner}"'

    return inner


def display_search_results(
    mods: Iterable[Pybuild], summarize: bool = True, file=sys.stdout
):
    """
    Prettily formats a list of mods for use in search results
    """
    groupedmods: Dict[str, List[Pybuild]] = {}
    for mod in mods:
        if groupedmods.get(mod.CPN) is None:
            groupedmods[mod.CPN] = [mod]
        else:
            groupedmods[mod.CPN].append(mod)

    sortedgroups = sorted(groupedmods.values(), key=lambda group: group[0].NAME)

    for group in sortedgroups:
        sortedmods = sorted(group, key=lambda mod: mod.PV)
        newest = get_newest(group)
        installed = load_installed_pkg(Atom(newest.CPN))
        download = get_total_download_size([newest])

        if installed is not None:
            installed_str = blue(bright(installed.PV))

            flags = {flag.lstrip("+") for flag in installed.IUSE if "_" not in flag}
            usestr = get_flag_string(
                None, installed.INSTALLED_USE & flags, flags - installed.INSTALLED_USE
            )
            texture_options = {
                size
                for mod in group
                for size in use_reduce(
                    installed.TEXTURE_SIZES, matchall=True, flat=True
                )
            }
            texture = next(
                (
                    use.lstrip("texture_size_")
                    for use in installed.INSTALLED_USE
                    if use.startswith("texture_size_")
                ),
                None,
            )
            if isinstance(texture, str):
                texture_string = get_flag_string(
                    "TEXTURE_SIZE", [texture], texture_options - {texture}
                )
            else:
                texture_string = None
            use_expand_strings = []
            for use in get_config().get("USE_EXPAND", []):
                if use in get_config().get("USE_EXPAND_HIDDEN", []):
                    continue
                enabled_expand, disabled_expand = get_use_expand(installed, use)
                if enabled_expand or disabled_expand:
                    string = get_flag_string(use, enabled_expand, disabled_expand, None)
                    use_expand_strings.append(string)

            installed_str += (
                " {"
                + " ".join(
                    list(filter(None, [usestr, texture_string] + use_expand_strings))
                )
                + "}"
            )
        else:
            installed_str = "not installed"

        # List of version numbers, prefixed by either (~) or ** depending on
        # keyword for user's arch. Followed by use flags, including use expand
        version_str = ""
        versions = []
        ARCH = env.prefix().ARCH
        for mod in sortedmods:
            if ARCH in mod.KEYWORDS:
                version_nofmt = mod.PV
                version = green(mod.PV)
            elif "~" + ARCH in mod.KEYWORDS:
                version_nofmt = "(~)" + mod.PV
                version = yellow(version_nofmt)
            else:
                version_nofmt = "**" + mod.PV
                version = red(version_nofmt)

            if is_masked(mod.ATOM, mod.REPO):
                versions.append(red("[M]" + version_nofmt))
            else:
                versions.append(version)
        version_str = " ".join(versions)
        flags = {
            flag.lstrip("+") for mod in group for flag in mod.IUSE if "_" not in flag
        }
        usestr = get_flag_string(None, [], flags, display_minuses=False)
        texture_options = {
            size
            for mod in group
            for size in use_reduce(mod.TEXTURE_SIZES, matchall=True, flat=True)
        }
        texture_string = get_flag_string(
            "TEXTURE_SIZE", [], texture_options, display_minuses=False
        )
        use_expand_strings = []
        for use in get_config().get("USE_EXPAND", []):
            if use in get_config().get("USE_EXPAND_HIDDEN", []):
                continue
            flags = {
                re.sub(f"^{use.lower()}_", "", flag)
                for flag in mod.IUSE_EFFECTIVE
                for mod in group
                if flag.startswith(f"{use.lower()}_")
            }
            if flags:
                string = get_flag_string(use, [], flags, None, display_minuses=False)
                use_expand_strings.append(string)

        version_str += (
            " {"
            + " ".join(
                list(filter(None, [usestr, texture_string] + use_expand_strings))
            )
            + "}"
        )

        # If there are multiple URLs, remove any formatting from the pybuild and
        # add padding
        homepage_str = "\n                 ".join(newest.HOMEPAGE.split())
        mod_metadata = get_package_metadata(mod)

        print(
            "{}  {}".format(green("*"), bright(newest.CPN)),
            "       {} {}".format(green(l10n("package-name")), mod.NAME),
            "       {} {}".format(
                green(l10n("package-available-versions")), version_str
            ),
            "       {} {}".format(
                green(l10n("package-installed-version")), installed_str
            ),
            "       {} {}".format(green(l10n("package-size-of-files")), download),
            "       {} {}".format(green(l10n("package-homepage")), homepage_str),
            "       {} {}".format(
                green(l10n("package-description")), str_squelch_sep(newest.DESC)
            ),
            "       {} {}".format(green(l10n("package-license")), newest.LICENSE),
            sep="\n",
            file=file,
        )

        if mod_metadata and mod_metadata.upstream:
            maintainers = mod_metadata.upstream.maintainer
            if maintainers:
                maintainers_display_strings = get_maintainer_string(maintainers)
                print(
                    "       {} {}".format(
                        green(l10n("package-upstream-author")),
                        maintainers_display_strings,
                    ),
                    file=file,
                )

        print(file=file)

    if summarize:
        print("\n" + l10n("packages-found", num=len(sortedgroups)), file=file)


class FlagDesc:
    """Use flag descriptions"""

    def __init__(self, desc: str):
        self.desc = desc

    def __str__(self):
        return self.desc


class LocalFlagDesc(FlagDesc):
    """Local use flag description"""

    def __init__(self, pkg: Pybuild, desc: str):
        super().__init__(desc)
        self.pkg = pkg

    def __repr__(self):
        return f"LocalDesc({self.pkg}, {self.desc})"


class UseExpandDesc(FlagDesc):
    """Local use flag description"""

    def __init__(self, category: str, flag: str, desc: str):
        super().__init__(desc)
        self.flag = flag
        self.category = category

    def __repr__(self):
        return f"UseExpandDesc({self.category}, {self.desc})"


def get_flag_desc(pkg: Pybuild, flag: str) -> Optional[FlagDesc]:
    """Returns the description for the given use flag"""
    repo_root = get_repo(pkg.REPO).location

    global_use = get_global_use(repo_root)
    metadata = get_package_metadata(pkg)

    if metadata and flag in metadata.use:
        return LocalFlagDesc(pkg, metadata.use[flag])
    if flag in global_use:
        return FlagDesc(global_use[flag])
    if flag.startswith("texture_size_"):
        size = flag.replace("texture_size_", "")
        return UseExpandDesc("texture_size", size, l10n("texture-size-desc", size=size))
    if "_" in flag:  # USE_EXPAND
        use_expand = flag.rsplit("_", 1)[0]
        suffix = flag.replace(use_expand + "_", "")
        use_expand_desc = get_use_expand_values(repo_root, use_expand).get(suffix)
        if use_expand_desc:
            return UseExpandDesc(use_expand, suffix, use_expand_desc)

    return None


def get_flags(
    pkg: Pybuild,
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, Dict[str, str]]]:
    """
    Returns all use flags and their descriptions for the given package

    returns:
        Three dictionaries, one each for local flags, global flags and use_expand flags,
        in that order. The use expand flags are subdivided for each use_expand category.
    """
    repo_root = get_repo(pkg.REPO).location

    global_use = get_global_use(repo_root)
    metadata = get_package_metadata(pkg)

    local_flags = {}
    global_flags = {}
    use_expand_flags: DefaultDict[str, Dict[str, str]] = defaultdict(dict)

    for flag in pkg.IUSE_EFFECTIVE:
        if metadata and flag in metadata.use:
            local_flags[flag] = metadata.use[flag]
        elif flag in global_use:
            global_flags[flag] = global_use[flag]
        elif flag.startswith("texture_size_"):
            size = flag.replace("texture_size_", "")
            desc = l10n("texture-size-desc", size=size)
            use_expand_flags["texture_size"][size] = desc
        elif "_" in flag:  # USE_EXPAND
            use_expand = flag.rsplit("_", 1)[0]
            suffix = flag.replace(use_expand + "_", "")
            use_expand_desc = get_use_expand_values(repo_root, use_expand).get(suffix)
            if use_expand_desc:
                use_expand_flags[use_expand][suffix] = use_expand_desc
        else:
            # No description Found.
            # Might be an installed package without metadata.yaml
            continue

    return local_flags, global_flags, use_expand_flags
