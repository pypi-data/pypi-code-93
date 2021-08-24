from unittest.mock import MagicMock

class AuditsApiMock:

    def __init__(self):
        self.mock_list_audits = MagicMock()
        self.mock_list_auth_records = MagicMock()

    def list_audits(self, *args, **kwargs):
        """
        This method mocks the original api AuditsApi.list_audits with MagicMock.
        """
        return self.mock_list_audits(self, *args, **kwargs)

    def list_auth_records(self, *args, **kwargs):
        """
        This method mocks the original api AuditsApi.list_auth_records with MagicMock.
        """
        return self.mock_list_auth_records(self, *args, **kwargs)

