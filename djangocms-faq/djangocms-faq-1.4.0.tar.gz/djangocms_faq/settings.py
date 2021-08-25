from django.conf import settings


ENABLE_API = getattr(settings, "DJANGOCMS_FAQ_ENABLE_API", True)

ANSWER_PLUGINS = getattr(
    settings,
    "DJANGOCMS_FAQ_ANSWER_PLUGINS",
    ["TextPlugin", "FilePlugin", "VideoPlayerPlugin"],
)

SHOW_KEYWORDS_QUESTION = getattr(settings, "DJANGOCMS_FAQ_SHOW_KEYWORDS_QUESTION", True)
SHOW_KEYWORDS_ANSWER = getattr(settings, "DJANGOCMS_FAQ_SHOW_KEYWORDS_ANSWER", True)

ENABLE_FUZZY_SEARCH = getattr(settings, "DJANGOCMS_FAQ_ENABLE_FUZZY_SEARCH", False)
FUZZY_SEARCH_PERCENTAGE = getattr(settings, "DJANGOCMS_FAQ_FUZZY_SEARCH_PERCENTAGE", 85)

SEARCH_WORD_BY_WORD_KEYWORDS = getattr(
    settings, "DJANGOCMS_FAQ_SEARCH_WORD_BY_WORD_KEYWORDS", False
)

MAX_QUERY_LENGTH = getattr(settings, "DJANGOCMS_FAQ_MAX_QUERY_LENGTH", 60)
