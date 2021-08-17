#!/usr/bin/env python3

import re
import os
from pathlib import Path

def list_files_local(directory: str, regex: re.Pattern) -> list:
    directory = Path(directory).expanduser().resolve(strict = True).as_posix()
    if not directory: return []
    #file_list = []
    #for root, dirs, files in os.walk(directory):
    #    for f in files:
    #        if regex.search(os.path.join(root, f)): file_list.append(os.path.join(root, f))
    #return file_list
    return [os.path.join(root, f)  for (root, dirs, files) in os.walk(directory) for f in files if regex.match(os.path.join(root, f))]
    #return [os.path.join(root, f) for (root, dirs, files) in os.walk(directory) for f in files]


rex = re.compile('.*\.py$')
loc = '~/work-GRID/jalien_py'

l = list_files_local(loc, rex)
print(l)
