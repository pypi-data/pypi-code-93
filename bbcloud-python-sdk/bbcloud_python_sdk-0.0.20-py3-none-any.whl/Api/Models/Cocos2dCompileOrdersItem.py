from bbcloud_python_sdk.Api.Models.Model import Model


class Cocos2dCompileOrdersItem(Model):
    def __init__(self, *args, **kwargs):
        super(Cocos2dCompileOrdersItem, self).__init__(*args, **kwargs)
        self._modal_path = 'packer/cocos2d_compile_orders_items'
