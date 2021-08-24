from googleapiclient.discovery import build
from . import auth

class Search:
    def list_all_files(self):
        creds = auth.Auth().verify_token()

        if creds:
            service = build('drive', 'v3', credentials=creds)

            results = service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                print('no files found.')
            else:
                for item in items:
                    print(u'{0} ({1})'.format(item['name'], item['id']))
        else:
            print('verification failed. please login.')
