from bbcloud_python_sdk.Api.Models.Model import Model


class SDK(Model):
    def __init__(self,*args, **kwargs):
        super(SDK, self).__init__(*args,**kwargs)
        self.model_path = None
