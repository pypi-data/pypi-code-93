from pathlib import Path
import os


def convert(path):
    for p in path.rglob("*.vtt"):
        q = p.stem
        q = q+".srt"
        target = Path(p.parent) / q
        print(target)
        p.rename(target)
