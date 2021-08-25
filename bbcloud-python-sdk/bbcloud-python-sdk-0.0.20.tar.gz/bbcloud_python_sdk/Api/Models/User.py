from bbcloud_python_sdk.Api.Models.Model import Model


class User(Model):
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._modal_path = None
