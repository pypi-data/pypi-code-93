import re

from aniparser.constants import audio_terms, video_terms, source_terms

__all__ = (
    "EPISODE_SEASON_REGEX",
    "EPISODE_REGEX",
    "SEASON_REGEX",
    "RESOLUTION_REGEX",
    "CHECKSUM_REGEX",
    "BRACKET_TERMS_REGEX",
    "YEAR_REGEX",
    "EXTENSION_REGEX",
    "RELEASE_VERSION_REGEX",
    "RELEASE_GROUP_REGEX",
    "EMPTY_BRACKETS_REGEX",
    "AUDIO_TERM_REGEX",
    "VIDEO_TERM_REGEX",
    "SOURCE_TERM_REGEX",
    "ALTERNATE_TITLE_REGEX",
)

# Unfortunately there's too many combinations that can fuck up with titles too
# we need to handle episodes/seasons in steps
EPISODE_SEASON_REGEX = re.compile(
    r"s?(?P<season>\d+)(e|ep|sp|x)(?P<episode>\d+)", flags=re.IGNORECASE
)
EPISODE_REGEX = re.compile(
    r"(\/| )e?(?P<episode>\d+)[ \.\-\/]",
    flags=re.IGNORECASE,
)
SEASON_REGEX = re.compile(r"\(?(Season| s) ?(?P<season>\d+)\)?", flags=re.IGNORECASE)

RESOLUTION_REGEX = re.compile(
    r"(?P<pos_height>\d{3,4})([p]|[x\u00D7](?P<height>\d{3,4}))|\[(?P<alone_height>\d{3,4})\]",
    flags=re.IGNORECASE,
)
CHECKSUM_REGEX = re.compile(
    r"[ -]?[\[(](?P<checksum>[A-Fa-f0-9]{8})[\])][ -]?", flags=re.IGNORECASE
)
BRACKET_TERMS_REGEX = re.compile(r"\[(?P<terms>[\w \-_.]*)\]", flags=re.IGNORECASE)
YEAR_REGEX = re.compile(r"[\[\( \-](?P<year>\d{4})[\]\) \-]", flags=re.IGNORECASE)
EXTENSION_REGEX = re.compile(r"(\.(?:(?:[a-z]+)|\[\w+\]))")
RELEASE_VERSION_REGEX = re.compile(r"(?P<release>v\d+)", flags=re.IGNORECASE)
RELEASE_GROUP_REGEX = re.compile(r"^\/[\[\(](?P<release_group>[\w\s\- ]+)[\]\)]")
EMPTY_BRACKETS_REGEX = re.compile(r"[\[\(][_\-. ]*[\]\)]")


AUDIO_TERM_REGEX = re.compile(
    f"({'|'.join(audio_terms)})" + r"(?=[^\w])", flags=re.IGNORECASE
)
VIDEO_TERM_REGEX = re.compile(
    f"({'|'.join(video_terms)})" + r"(?=[^\w])", flags=re.IGNORECASE
)
SOURCE_TERM_REGEX = re.compile(
    f"({'|'.join(source_terms)})" + r"(?=[^\w])", flags=re.IGNORECASE
)

ALTERNATE_TITLE_REGEX = re.compile(
    r"\((?P<alternate_title>[\w ]+)\)", flags=re.IGNORECASE
)
