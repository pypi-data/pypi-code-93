import os


def strip_prefix_path(orig: str, part: str) -> str:
    parts = os.path.split(orig)
    if len(parts) > 1 and parts[0] == part:
        parts = parts[1:]
    return os.path.join(*parts)


def get_real_path(target: str, strip: str) -> str:
    if os.path.exists(target):
        return target
    return target.replace(strip, "", 1)
