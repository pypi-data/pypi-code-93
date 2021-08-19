# coding: utf-8
import requests


class FIASClient(object):
    """Клиент к серверу ФИАС"""
    fias_source = 'https://fias.nalog.ru/WebServices/Public/'

    def get_all_download_file_info(self):
        result = requests.get(
            '{}GetAllDownloadFileInfo'.format(self.fias_source)
        ).json()

        return result


client = FIASClient()