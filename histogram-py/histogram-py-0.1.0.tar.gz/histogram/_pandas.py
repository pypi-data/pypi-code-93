import io

import pandas as pd


@pd.api.extensions.register_dataframe_accessor("histogram")
@pd.api.extensions.register_series_accessor("histogram")
class Histogram:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        pass

    def plot(self, autoopen=True):
        """Plot opens the dataframe in histogram.dev"""
        import requests

        from . import base_url

        buf = io.BytesIO()
        self._obj.to_csv(buf, index=False)
        buf.seek(0)

        rawResp = requests.post(f"{base_url}/datafiles/hold", data=buf, headers={"Content-Type": "text/csv"})
        if rawResp.status_code != 200:
            raise Exception(rawResp.text)

        resp = rawResp.json()

        if autoopen:
            import webbrowser
            webbrowser.open(resp["urls"]["ui"])

        return resp
