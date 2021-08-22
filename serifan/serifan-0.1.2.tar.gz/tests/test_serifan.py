from serifan import __version__, api, session


def test_version():
    assert __version__ == "0.1.0"


def test_api():
    sb = None
    try:
        sb = api()
    except Exception as exc:
        print("serifan.api() raised {} unexpectedly!".format(exc))

    assert sb.__class__.__name__ == session.Session.__name__
