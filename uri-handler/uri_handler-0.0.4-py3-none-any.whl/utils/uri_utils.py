from uri_handler.utils._compat import urllib


def join_paths(paths, delimiter='/'):
    """join paths with a delimiter"""
    return delimiter.join([p.rstrip(delimiter) for p in paths])


def uri_join(uri, *args, **kwargs):
    """os.path.join-style function for appending path strings
    to a fully qualified uri.
    """
    parsed_uri = urllib.parse.urlparse(uri)

    # py2.7 workaround for kw-only argument delimiter
    delimiter = kwargs.get('delimiter', '/')
    new_pr = urllib.parse.ParseResult(
        parsed_uri.scheme,
        parsed_uri.netloc,
        join_paths([parsed_uri.path] + list(args), delimiter),
        parsed_uri.params,
        parsed_uri.query,
        parsed_uri.fragment)
    return urllib.parse.urlunparse(new_pr)


def get_prefix_path(path, delimiter='/'):
    """get dirname-equivalent path prefix for a given delimiter"""
    if path == delimiter:
        # mimic os.path.dirname functionality
        return path

    split_path = path.rstrip(delimiter).split(delimiter)
    if len(split_path) <= 2:  # case of e.g. /mything
        return delimiter
    else:
        return delimiter.join(split_path[:-1])


def uri_prefix(uri, delimiter='/'):
    """get new uri with path that is one delimiter up from the input uri"""
    parsed_uri = urllib.parse.urlparse(uri)
    new_pr = urllib.parse.ParseResult(
        parsed_uri.scheme,
        parsed_uri.netloc,
        get_prefix_path(parsed_uri.path, delimiter),
        parsed_uri.params,
        parsed_uri.query,
        parsed_uri.fragment)
    return urllib.parse.urlunparse(new_pr)
