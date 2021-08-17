"""Template globals."""

from pprint import pformat
from textwrap import dedent

import emoji
from understory.indieweb.micropub import discover_post_type
from understory.indieweb.webmention import get_mentions
from understory.web import tx

__all__ = ["pformat", "tx", "get_mentions", "discover_post_type", "dedent", "emoji"]
