import tempfile

from trifacta.util import tfrequests


def _fetchFile(resp, fd):
    for chunk in resp.iter_content(chunk_size=128):
        fd.write(chunk)


def downloadGet(url: str = None, destination: str = None):
    resp = tfrequests.get(url)
    if not destination:
        fd = tempfile.NamedTemporaryFile(delete=False)
        _fetchFile(resp, fd)
        destination = fd.name
        fd.close()
    else:
        with open(destination, "wb") as fd:
            _fetchFile(resp, fd)
    return destination
