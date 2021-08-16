from sys import path
import yaml
import pathlib

SETTINGS = {
    "show_command": True,
    "show_reason": True,
    "show_output": True,
    "colour": True
}

def load_settings(filepath):
    filepath = pathlib.Path(filepath)

    with filepath.open("r") as f:
        SETTINGS.update(
            yaml.safe_load(f.read())
        )

def setup_settings(filepath):
    root = pathlib.Path(filepath)
    config = pathlib.Path(root, "shortcut.d")

    root.mkdir()
    config.mkdir()

    with pathlib.Path(root, "settings.yaml").open("w") as f:
        f.write(
            yaml.safe_dump(SETTINGS, indent=2)
        )