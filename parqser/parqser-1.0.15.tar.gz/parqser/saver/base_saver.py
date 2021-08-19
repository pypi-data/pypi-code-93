from typing import List, Dict, Any


class BaseSaver:
    def __init__(self, *args, **kwargs):
        raise NotImplemented

    def save(self, params: Dict[str, Any]) -> None:
        raise NotImplemented

    def save_batch(self, params: List[Dict[str, Any]]) -> None:
        raise NotImplemented
