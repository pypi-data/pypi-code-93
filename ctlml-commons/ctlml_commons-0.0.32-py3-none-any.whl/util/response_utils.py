from typing import Dict

# TODO: add status enum

def failure_response(reason) -> Dict[str, str]:
    return {"status": "FAILED", "reason": str(reason)}


def success_response() -> Dict[str, str]:
    return {"status": "OK"}
