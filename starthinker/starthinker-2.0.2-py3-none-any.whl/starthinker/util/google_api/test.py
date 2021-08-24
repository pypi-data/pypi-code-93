"""Tests for google3.third_party.starthinker.starthinker.util.google_api.core."""

from google3.third_party.starthinker.starthinker.util.google_api import core
from google3.testing.pybase import googletest
from googleapiclient.errors import HttpError
from googleapiclient.discovery import Resource


class CoreTest(googletest.TestCase):

  @mock.patch.object(googleapiclient.discovery, 'Resource')
  def test_403_retries(self, mock_job):

    # Set up your desired behavior
    mock_job.execute.side_effect = [
        HttpError(403),
        HttpError(403),
        None
    ]

    # Run our code, injecting your mock
    API_Retry(mock_job)

    # Validate behavior you want happened
    self.assertEqual(API_Retry.call_count, 3)


if __name__ == '__main__':
  googletest.main()
