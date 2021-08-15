import requests


class SteamNews:
    def __init__(self, app_id=None, game_name=None, ):
        self._base_url = "http://api.steampowered.com"
        self._news_url = "/ISteamNews/GetNewsForApp/v0002/"
        self._apps_url = "/ISteamApps/GetAppList/v0002/"
        self.app_id = None
        self.game_name = None

        convert_request = requests.get(
            url=self._base_url + self._apps_url
        )
        self._apps_list = convert_request.json()["applist"]["apps"]
        self.validateInput(app_id, game_name)

    def __str__(self):
        return 'SteamNews of {} with the appid {}'.format(self.game_name, self.app_id)

    def validateInput(self, app_id, game_name):
        """
               doc comment
               """
        if app_id is None and game_name is None:
            pass  # TODO Raise Log Error both None

        for app in self._apps_list:
            if app_id is None:
                if app["name"] == game_name:
                    self.app_id = app["appid"]
                    self.game_name = game_name
                    break
                else:
                    # TODO raise error invalid app id
                    pass
            if game_name is None:
                if app["appid"] == app_id:
                    self.app_id = app_id
                    self.game_name = app["name"]
                    break
                else:
                    # TODO raise error invalid game name
                    pass

    def get_news(self, count=None, maxLength=None):
        query_parameters = {
            'appid': self.app_id,
            'count': count,
            'maxlength': maxLength,
            'format': 'json'
        }

        news_request = requests.get(
            url=self._base_url + self._news_url,
            params=query_parameters
        )
        return news_request.json()["appnews"]


