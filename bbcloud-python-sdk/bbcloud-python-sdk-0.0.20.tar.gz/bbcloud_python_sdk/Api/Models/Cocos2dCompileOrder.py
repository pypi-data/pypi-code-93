from bbcloud_python_sdk.Api.Models.Model import Model


class Cocos2dCompileOrder(Model):
    def __init__(self, *args, **kwargs):
        super(Cocos2dCompileOrder, self).__init__(*args, **kwargs)
        self._modal_path = 'packer/cocos2d_compile_orders'
