"""One Platform python media compatibility tests."""

import random
import string
import StringIO

import google3
import apitools.base.py as apitools_base

from google3.google.api.hexa import one_platform_env
from google3.pyglib import flags
from google3.testing.integration.hexa import testcase

from google3.apiserving.tools.testing.media import media_v1_client as media_client
from google3.apiserving.tools.testing.media import media_v1_messages as media_messages

FLAGS = flags.FLAGS
_CLIENT = None


def _GenerateData(length, alphabet=None):
  if alphabet is None:
    alphabet = string.hexdigits[:16]
  return ''.join(random.choice(alphabet) for _ in xrange(length))


def _GetClient(api_endpoint):
  global _CLIENT
  if _CLIENT is None:
    _CLIENT = media_client.MediaV1(
        api_endpoint,
        get_credentials=False,
        additional_http_headers={'X-GFE-SSL': 'yes'})
  return _CLIENT


class PythonMediaTest(one_platform_env.OnePlatformEnvComponentsMixin,
                      testcase.HexaTestCase):

  def setUp(self):
    api_endpoint = self.stash.apiComponent.GetProperties()['api_url']
    self.client = _GetClient(api_endpoint)

  def testMc1SimpleUpload(self):
    data = _GenerateData(32 * 1024)
    resource_name = 'objects/non_resumable'

    upload_stream = StringIO.StringIO(data)
    upload = apitools_base.Upload.FromStream(upload_stream, 'text/plain')
    upload.strategy = 'simple'
    upload_request = media_messages.Media(resourceName=resource_name)
    upload_response = self.client.media.Upload(upload_request, upload=upload)
    self.assertIsNotNone(upload_response)

    # Download process

    resource_name = 'sdfdownloadtask/media/23362726'
    download_stream = StringIO.StringIO()
    download = apitools_base.Download.FromStream(download_stream)
    download_request = media_messages.MediaMediaDownloadRequest(
        resourceName=resource_name)

    client = media_client.MediaV1(
        api_endpoint,
        get_credentials=False,
        additional_http_headers={'X-GFE-SSL': 'yes'})

    client.media.Download(download_request, download=download)
    download_stream.seek(0)
    self.assertEqual(data, download_stream.getvalue())

  def testMc2ResumableUpload(self):
    """Resumable upload not yet implemented in ESF."""


if __name__ == '__main__':
  testcase.main()
