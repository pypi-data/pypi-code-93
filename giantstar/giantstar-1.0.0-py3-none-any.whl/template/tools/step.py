from giantstar.drivers.httpDriver import HTTPDriver
from giantstar.drivers.webDriver import WEBDriver
from giantstar.drivers.kwDriver import KeyWordDriver
from giantstar.drivers.appDriver import APPDriver


class Step:

    def step(self, kw_path, **kwargs):
        kwargs["data_set"]["version"] = 2
        if kw_path == "api":
            HTTPDriver.run(**kwargs)
        elif kw_path == "web":
            kwargs["data_set"]["request"] = [kwargs["data_set"]["request"]]
            WEBDriver.run(**kwargs)
        elif kw_path == 'app':
            kwargs["data_set"]["request"] = [kwargs["data_set"]["request"]]
            APPDriver.run(**kwargs)
        else:
            KeyWordDriver.run(kw=kw_path, **kwargs)

