import pytest

from nltkma.corpus.reader import CorpusReader


@pytest.fixture(autouse=True)
def mock_plot(mocker):
    """ Disable matplotlib plotting in test code """

    try:
        import matplotlib.pyplot as plt
        mocker.patch.object(plt, 'gca')
        mocker.patch.object(plt, 'show')
    except ImportError:
        pass


@pytest.fixture(scope="module", autouse=True)
def teardown_loaded_corpora():
    """
    After each test session ends (either doctest or unit test),
    unload any loaded corpora
    """

    yield  # first, wait for the test to end

    import nltkma.corpus

    for name in dir(nltkma.corpus):
        obj = getattr(nltkma.corpus, name, None)
        if isinstance(obj, CorpusReader) and hasattr(obj, "_unload"):
            obj._unload()
