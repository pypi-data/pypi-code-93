# Keep this file in sync with mimeType.ts.

from atoti._version import VERSION

_ATOTI_MAJOR_VERSION = VERSION.split(".", maxsplit=1)[0]

LINK_MIME_TYPE = f"application/vnd.atoti.link.v{_ATOTI_MAJOR_VERSION}+json"

CONVERT_QUERY_RESULT_TO_WIDGET_MIME_TYPE = (
    f"application/vnd.atoti.convert-query-result-to-widget.v{_ATOTI_MAJOR_VERSION}+json"
)

WIDGET_MIME_TYPE = f"application/vnd.atoti.widget.v{_ATOTI_MAJOR_VERSION}+json"
