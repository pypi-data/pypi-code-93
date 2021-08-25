# -*- coding: utf-8 -*-
from django.utils.text import slugify
from django.conf import settings


def ievv_slugify(value):
    """
    Replaces norwegian characters before slugify

    Args:
        value:

    Returns:
        slugified value

    """
    character_replace_map = {
        'æ': 'a',
        'ø': 'o',
        'å': 'a'
    }
    if hasattr(settings, 'IEVV_SLUGIFY_CHARACTER_REPLACE_MAP'):
        character_replace_map = settings.IEVV_SLUGIFY_CHARACTER_REPLACE_MAP
    for character, replace_character in character_replace_map.items():
        value = value.replace(character, replace_character)
    return slugify(value)
