from . import urls


def make_url(base_url, action):
    return f'{base_url}/{action}'


def make_routes(base_url):
    return {url.split('.')[0]: make_url(base_url, url) for url in urls}
