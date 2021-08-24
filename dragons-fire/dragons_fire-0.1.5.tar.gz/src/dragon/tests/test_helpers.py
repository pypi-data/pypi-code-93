from .._helpers import TEST_CLASSES


class TestHelpers:
    def test_classes_is_dict(self):
        assert isinstance(TEST_CLASSES, dict)
