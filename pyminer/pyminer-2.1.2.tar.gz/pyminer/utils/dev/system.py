import subprocess
from pathlib import Path
from typing import Union

import chardet


def system(*args: Union[str, Path]):
    args = [str(arg) for arg in args]
    result = subprocess.run(args=args, capture_output=True)
    if stdout := result.stdout:
        print('Out: ')
        stdout = stdout.decode(chardet.detect(result.stdout)['encoding'])
        print(stdout)
    if stderr := result.stderr:
        print('Error: ')
        stderr = stderr.decode(chardet.detect(result.stderr)['encoding'])
        print(stderr)
