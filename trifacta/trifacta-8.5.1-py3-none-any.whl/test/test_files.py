import pytest
import os
from trifacta.util import tfrequests as tfr
from trifacta.util import tffiles as tff
import tempfile
import pandas as pd


class TestFilesClass:
    def test_uploadFileParams(self):
        user = tfr.get(url="/v4/people/current").json()
        with pytest.raises(ValueError):
            tff.uploadFile(path=None, data=None, filename = '/baz/bletch.txt', user=user)
        with pytest.raises(ValueError):
            tff.uploadFile(path='/foo/bar', filename="/baz/bletch.txt", user=None)

    def test_uploadFile(self):
        awsConfig = None
        r = tfr.raw_get(url="/v4/awsConfigs", params={"limit": 1})
        if r.status_code == 200:
            awsConfig = r.json()["data"][0]
        df = pd.DataFrame({'letters': ['a','b','c'], 'numbers': [1,2,3]}).set_index('numbers')
        user = tfr.get(url="/v4/people/current").json()
        with tempfile.NamedTemporaryFile(dir = f'{os.getcwd()}/test/data', suffix = ".tripytest") as tmp:
            df.to_csv(tmp.name)
            r1 = tff.uploadFile(path=tmp.name, filename=os.path.basename(tmp.name), user=user, awsConfig=awsConfig)
            r2 = tff.uploadFile(path=tmp.name, filename=None, user=user, awsConfig=awsConfig)
    # there is no unit test for downloadGet -- will be exercised via a richer
    # call in the API. #REVISIT