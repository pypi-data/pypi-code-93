"""Module containing ID-generation utility functions."""

import hashlib
import uuid


def generate_uuid(input_text):
    """Returns a random UUID given an input text."""
    return uuid.UUID(hashlib.md5(str(input_text).encode('utf-8')).hexdigest())
