import os

from koalak.utils import randomstr, temp_pathname


def test_randomstr():
    # By default the function work (no need the first param)
    randomstr()

    # test length
    assert len(randomstr(10)) == 10
    assert len(randomstr(20)) == 20

    # test alphabet
    alphabet = "abc"
    for _ in range(20):
        a = randomstr(alphabet=alphabet)
        for c in a:
            assert c in alphabet

    # test exclude
    alphabet = "ab"
    a = randomstr(1, alphabet=alphabet, exclude="a")
    assert a == "b"

    # test prefix
    assert randomstr(prefix="ab_").startswith("ab_")


def test_temp_pathname():
    # Test that if we create a file, it is correctly removed
    with temp_pathname() as pathname:
        saved_pathname = pathname
        assert not os.path.exists(pathname)
        # create the file
        open(pathname, "w")

        assert os.path.exists(pathname)
    assert not os.path.exists(saved_pathname)

    # Test that if we create a directory, it is correctly removed
    with temp_pathname() as pathname:
        saved_pathname = pathname
        assert not os.path.exists(pathname)
        # create the file
        os.makedirs(os.path.join(pathname, "test"))
        assert os.path.exists(pathname)
    assert not os.path.exists(saved_pathname)

    # Test that the file is correctly removed after an exception
    class DummyException(Exception):
        pass

    try:
        with temp_pathname() as pathname:
            # create the file
            open(pathname, "w")
            raise DummyException
    except DummyException:
        assert not os.path.exists(pathname)
