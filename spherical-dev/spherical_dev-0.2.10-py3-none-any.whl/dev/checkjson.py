"""Check that JSON files are formatted with 4-space indents."""

import difflib
import json
import pathlib
import sys

import invoke


MAX_SIZE = 100 * 1024 * 1024


@invoke.task
def checkjson(_, path='.', maxsize=MAX_SIZE, update=False):
    """Check/update formatting of JSON files."""
    errors = 0
    for jsonpath in pathlib.Path(path).glob('**/*.json'):
        if jsonpath.stat().st_size > maxsize:
            print(f'{jsonpath} is too big')
            continue
        original = jsonpath.read_text(encoding='utf-8')
        indented = json.dumps(json.loads(original), indent=4) + '\n'
        if indented != original:
            if update:
                jsonpath.write_text(indented, encoding='utf-8')
            else:
                for line in difflib.unified_diff(
                    original.split('\n'),
                    indented.split('\n'),
                    fromfile=f'current/{jsonpath}',
                    tofile=f'fixed/{jsonpath}',
                    lineterm='',
                ):
                    print(line)
                errors += 1
    if errors:
        sys.exit(1)
