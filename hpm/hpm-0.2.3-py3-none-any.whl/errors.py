from dataclasses import dataclass


@dataclass
class APIError(Exception):
    """An error in API call"""
