import sys
import warnings

from ale_py import ALEInterface

from typing import Dict

if sys.version_info < (3, 9):
    import importlib_resources as resources
else:
    import importlib.resources as resources

from importlib.util import find_spec
from pkg_resources import iter_entry_points


def normalize_rom_name(rom):
    """
    Normalize rom name, snake case -> camal case
    """
    return rom.title().replace("_", "")


def find_internal_roms(package: str) -> Dict[str, str]:
    """
    Find ROMs in base `package` with extension *.bin
    """
    roms = {}
    # Iterate over ROMs in `packages`'s resources
    for resource in filter(
        lambda file: file.endswith(".bin"), resources.contents(package)
    ):
        with resources.path(package, resource) as path:
            resolved = str(path.resolve())
            rom = ALEInterface.isSupportedROM(resolved)
            if rom is None:
                raise ImportError(
                    f"ROM ale-py.roms/{path.name} is not supported, did you import via ale-import-roms?"
                )

            # ROM names are snake case in ALE, convert to camel case.
            romid = normalize_rom_name(rom)
            roms[romid] = resolved
    return roms


def find_external_roms(group: str) -> Dict[str, str]:
    """
    Find external ROMs which have the entry points of ale_py.roms
    """
    roms = {}
    # Iterate over all entrypoints in this group
    for external in iter_entry_points(group):
        # We load the external load ROM function and
        # update the ROM dict with the result
        # Silently fail as this is run on root pkg import
        try:
            external_find_roms = external.load()
            roms.update(external_find_roms())
        except Exception as e:
            warnings.warn(
                f"Failed to load ROMs from external {external}\n{e}", stacklevel=2
            )

    return roms


def find_atari_py_roms(package: str) -> Dict[str, str]:
    roms = {}
    # Iterate over `atari_roms` subfolder if the package exists
    if find_spec(package) is not None and "atari_roms" in resources.contents(package):
        warnings.warn(
            "Importing atari-py roms won't be supported in future releases of ale-py.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        root = resources.files(package) / "atari_roms"
        for path in root.glob("*.bin"):
            resolved = str(path.resolve())
            rom = ALEInterface.isSupportedROM(resolved)
            # For backwards compat don't fail upon importing atari-py ROMs
            if rom is None:
                warnings.warn(
                    (
                        f"ROM atari-py.roms/{path.name} is not supported."
                        "Try importing ROMs with ale-import-roms to assess which "
                        "ROMs are supported by the ALE."
                    ),
                    stacklevel=2,
                )
                continue

            # ROM names are snake case in ALE, convert to camel case.
            romid = normalize_rom_name(rom)
            roms[romid] = resolved

    return roms
