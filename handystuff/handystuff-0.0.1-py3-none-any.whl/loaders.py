import os
from typing import Any, Dict, List

from _jsonnet import evaluate_file

try:
    import ujson as json
    import json as vanilla_json
except ImportError:
    import json

    vanilla_json = json


def load_json(path: str) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def write_json(result, path, pretty=True, encoder=None):
    if os.path.dirname(path).replace(".", ""):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w+") as f:
        if pretty:
            vanilla_json.dump(result, f, indent=4, separators=(',', ': '), cls=encoder)
        else:
            json.dump(result, f)


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    with open(path) as f:
        return [json.loads(d) for d in f.read().splitlines()]


def write_jsonl(data: List[Dict[str, Any]], path, encoder=None):
    ds = [json.dumps(d, cls=encoder) for d in data]
    with open(path, 'w+') as f:
        f.write('\n'.join(ds) + '\n')


def load_jsonnet(path: str):
    return json.loads(evaluate_file(path))
