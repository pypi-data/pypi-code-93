import requests

from biolib.biolib_api_client.auth import BearerAuth
from biolib.biolib_api_client import BiolibApiClient
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger


class BiolibAppApi:
    @staticmethod
    def fetch_by_name(account_handle, app_name):
        response = requests.get(
            f'{BiolibApiClient.get().base_url}/api/apps/',
            params={'account_handle': account_handle, 'app_name': app_name},
            auth=BearerAuth(BiolibApiClient.get().access_token)
        )

        if not response.ok:
            raise Exception(response.content.decode())

        paginated_apps = response.json()
        if len(paginated_apps['results']) > 0:
            return paginated_apps['results'][0]
        else:
            raise BioLibError('App not found')

    @staticmethod
    def push_app_version(app_id, zip_binary, author, app_name, set_as_active):
        response = requests.post(
            f'{BiolibApiClient.get().base_url}/api/app_versions/',
            files={
                'app': (None, app_id),
                'set_as_active': (None, 'true' if set_as_active else 'false'),
                'state': (None, 'published'),
                'source_files_zip': zip_binary
            },
            auth=BearerAuth(BiolibApiClient.get().access_token)
        )
        if not response.ok:
            logger.error(f'Push failed for {author}/{app_name}:')
            raise BioLibError(response.text)

        # TODO: When response includes the version number, print the URL for the new app version
        logger.info(f'Successfully pushed app version for {author}/{app_name}.')
        return response.json()

    @staticmethod
    def update_app_version(app_version_id, data):
        response = requests.patch(
            f'{BiolibApiClient.get().base_url}/api/app_versions/{app_version_id}/',
            json=data,
            auth=BearerAuth(BiolibApiClient.get().access_token)
        )
        if not response.ok:
            logger.error(f'Failed to update app version {app_version_id}')
            raise BioLibError(response.text)

        return response.json()
