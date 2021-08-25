from bbcloud_python_sdk.Api.Models.Model import Model


class Unity3dCompileOrder(Model):
    def __init__(self, *args, **kwargs):
        super(Unity3dCompileOrder, self).__init__(*args, **kwargs)
        self._modal_path = 'packer/unity3d_compile_orders'
