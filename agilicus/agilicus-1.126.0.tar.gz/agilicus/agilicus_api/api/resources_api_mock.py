from unittest.mock import MagicMock

class ResourcesApiMock:

    def __init__(self):
        self.mock_list_resources = MagicMock()

    def list_resources(self, *args, **kwargs):
        """
        This method mocks the original api ResourcesApi.list_resources with MagicMock.
        """
        return self.mock_list_resources(self, *args, **kwargs)

