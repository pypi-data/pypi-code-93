"""Common utility methods."""
import re
from urllib.parse import urljoin


def smart_url(url, force_https=False, prefix=None):
    """Return the appropriate URL.

    The returned URL will be:
     - an empty string, when the provided url is None;
     - the provided url, unchanged, when it includes the protocol ('http', 'https' or '//');
     - otherwise, the provided url, optionally prefixed with the given prefix.
     - finally, if force_https is set, we ensure the URL is return with the HTTPS protocol.
    """
    if not url:
        return ''

    if not force_https and (url.startswith('http') or url.startswith('//')):
        return url

    if prefix:
        url = urljoin(prefix, url)

    if force_https:
        match = re.match('http:|https:', url)
        if match:
            _, _, url = url.partition(match.group(0))

        url = urljoin('https://', url)

    return url


__all__ = ['smart_url']
