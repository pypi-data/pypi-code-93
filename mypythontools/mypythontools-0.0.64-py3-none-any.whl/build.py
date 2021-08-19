"""
This module build the app via pyinstaller.
It has presets to build applications build with eel.

There is one main function `build_app`. Check it's help for how to use
it (should be very simple).

Note:
    You can run build for example from vs code tasks, create folder utils,
    create build_script.py inside, add

    >>> import mypythontools
    ...
    >>> if __name__ == "__main__":
    ...     mypythontools.build.build_app()  # With all the params you need.

    Then just add this task to global tasks.json::

        {
            "label": "Build app",
            "type": "shell",
            "command": "python",
            "args": ["${workspaceFolder}/utils/build_script.py"],
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
"""

import subprocess
import shutil
from pathlib import Path
from . import paths
import mylogging

# Lazy imports
# import EelForkExcludeFiles


def build_app(
    main_file="app.py",
    preset=None,
    web_path=None,
    build_web=None,
    remove_last_build=False,
    console=True,
    debug=False,
    icon=None,
    hidden_imports=[],
    ignored_packages=[],
    datas=[],
    name=None,
    env_vars={},
    cleanit=True,
):
    """One script to build .exe app from source code.

    This script automatically generate .spec file, build node web files and add environment variables during build.

    This script suppose some structure of the app (may have way different though). You can use project-starter from the same repository,
    if you start with application.

    Args:
        main_file (str, optional): Main file path or name with extension. Main file is found automatically
            and don't have to be in root. Defaults to 'app.py'.
        preset (str, optional): Edit other params for specific use cases (append to hidden_imports, datas etc.)
            Options ['eel']. Defaults to None.
        web_path ((Path, str), optional): Folder with index.html. Defaults to None.
        build_web (bool, optional): If application contain package.json in folder 'gui', build it (if using eel). Defaults to None.
        remove_last_build (bool, optional): If some problems, it is possible to delete build and dist folders. Defaults to False.
        console (bool, optional): Before app run terminal window appears (good for debugging). Defaults to False.
        debug (bool, optional): If no console, then dialog window with traceback appears. Defaults to False.
        icon ((Path, str, None), optional): Path or name with extension to .ico file (!no png!). Defaults to None.
        hidden_imports (list, optional): If app is not working, it can be because some library was not builded. Add such
            libraries into this list. Defaults to [].
        ignored_packages (list, optional): Libraries take space even if not necessary. Defaults to [].
        datas (list, optional): Add static files to build. Example: [('my_source_path, 'destination_path')]. Defaults to [].
        name (str, optional): If name of app is different than main py file. Defaults to None.
        env_vars (dict, optional): Add some env vars during build. Mostly to tell main script that it's production (ne development) mode.
            Defaults to {}.
        cleanit (bool, optional): Remove spec file and var env py hook. Defaults to True.

    Note:
        Build pyinstaller bootloader on your pc, otherwise antivirus can check the
        file for a while on first run and even alert false positive.

        Download from github, cd to bootloader and::

            python ./waf all

        Back to pyinstaller folder and python `setup.py`
    """

    if not paths.ROOT_PATH:
        paths.set_root()

    # Try to recognize the structure of app
    build_path = paths.ROOT_PATH / "build"

    if not build_path.exists():
        build_path.mkdir(parents=True, exist_ok=True)

    # Remove last dist manually to avoid permission error if opened in some application
    dist_path = paths.ROOT_PATH / "dist"

    if dist_path.exists():
        try:
            shutil.rmtree(dist_path, ignore_errors=False)
        except (PermissionError, OSError):
            raise PermissionError(
                mylogging.return_str(
                    "App is opened (May be in another app(terminal, explorer...)). Close it first."
                )
            )

    # May be just name - not absolute
    main_file_path = Path(main_file)

    if not main_file_path.exists():

        # Iter paths and find the one
        main_file_path = paths.find_path(main_file_path, exclude=["node_modules", "build"])

        if not main_file_path.exists():
            raise KeyError("Main file not found, not infered and must be configured in params...")

    main_file_path = main_file_path.resolve()

    if not name:
        name = main_file_path.stem

    main_folder_path = main_file_path.parent

    if icon:
        icon_path = Path(icon)

        if not icon_path.exists():

            # Iter paths and find the one
            icon_path = paths.find_path(icon_path, exclude=["node_modules", "build"])

            if not icon_path.exists():
                raise KeyError("Icon not found, not infered check path or name...")
    else:
        icon_path = None

    generated_warning = """
#########################
### File is generated ###
#########################

# Do not edit this file, edit build_script
"""

    if remove_last_build:
        try:
            shutil.rmtree("build", ignore_errors=True)
        except Exception:
            pass

    # Build JS to static asset
    if build_web:
        gui_path = paths.find_path("package.json").parent
        subprocess.run(["npm", "run", "build"], shell=True, check=True, cwd=gui_path)

    if build_web or preset == "eel":
        if not web_path:
            web_path = paths.find_path("index.html", exclude=["public", "node_modules", "build"]).parent

        else:
            web_path = Path(web_path)

        if not web_path.exists():
            raise KeyError("Build web assets not found, not infered and must be configured in params...")

        datas = (
            *datas,
            (web_path.as_posix(), "gui"),
        )

    if preset == "eel":

        import EelForkExcludeFiles

        if build_web is None:
            build_web = True

        hidden_imports = [*hidden_imports, "EelForkExcludeFiles", "bottle_websocket"]
        datas = (
            *datas,
            (EelForkExcludeFiles._eel_js_file, "EelForkExcludeFiles"),
        )
        env_vars = {**env_vars, "MY_PYTHON_VUE_ENVIRONMENT": "production"}

    if env_vars:
        env_vars_template = f"""
{generated_warning}

import os
for i, j in {env_vars}.items():
    os.environ[i] = j
"""

        env_path = build_path / "env_vars.py"

        with open(env_path, "w") as env_vars_py:
            env_vars_py.write(env_vars_template)
        runtime_hooks = [env_path.as_posix()]
    else:
        runtime_hooks = None

    spec_template = f"""
{generated_warning}

import sys
from pathlib import Path
import os

sys.setrecursionlimit(5000)
block_cipher = None

a = Analysis(['{main_file_path.as_posix()}'],
            pathex=['{main_folder_path.as_posix()}'],
            binaries=[],
            datas={datas},
            hiddenimports={hidden_imports},
            hookspath=[],
            runtime_hooks={runtime_hooks},
            excludes={ignored_packages},
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
            cipher=block_cipher)
exe = EXE(pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='{name}',
        debug={debug},
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console={console},
        icon={f"'{icon_path.as_posix()}'" if icon else None})
coll = COLLECT(exe,
            a.binaries,
            a.zipfiles,
            a.datas,
            strip=False,
            upx=True,
            upx_exclude=[],
            name='{name}')
"""
    spec_path = build_path / "app.spec"

    with open(spec_path, "w") as spec_file:
        spec_file.write(spec_template)

    # Build py to exe

    subprocess.run(
        ["pyinstaller", "-y", spec_path.as_posix()],
        shell=True,
        check=True,
        cwd=paths.ROOT_PATH,
    )

    if cleanit:
        try:
            spec_path.unlink()
            env_path.unlink()
        except Exception:
            pass
