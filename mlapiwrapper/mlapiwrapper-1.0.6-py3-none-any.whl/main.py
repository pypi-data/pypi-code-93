# -*- coding: utf-8 -*-

from sentimentApi import Api

import pandas as pd
import json
import ssl
if __name__ == "__main__":
    api = Api(response_format="json")
    print(ssl.OPENSSL_VERSION)
    test_list = [
    "nhân viên nhiệt tình. hỗ trợ rất tốt","nhân viên hơi nhiệt tình", "nhân viên hơi nhiệt tình",
    # "nhân viên nhiệt tình. hỗ trợ rất tốt", "nhân viên hơi nhiệt tình", "nhân viên nhiệt tình. hỗ trợ rất tốt",
    # "nhân viên hơi nhiệt tình", "nhân viên nhiệt tình. hỗ trợ rất tốt", "nhân viên hơi nhiệt tình",
    # "nhân viên nhiệt tình. hỗ trợ rất tốt", "nhân viên hơi nhiệt tình", "nhân viên nhiệt tình. hỗ trợ rất tốt",
    # "nhân viên hơi nhiệt tình", "nhân viên nhiệt tình. hỗ trợ rất tốt", "nhân viên hơi nhiệt tình",
    # "nhân viên nhiệt tình. hỗ trợ rất tốt", "nhân viên hơi nhiệt tình", "nhân viên nhiệt tình. hỗ trợ rất tốt",
    # "nhân viên hơi nhiệt tình", "nhân viên nhiệt tình. hỗ trợ rất tốt", "nhân viên hơi nhiệt tình",
    # "nhân viên nhiệt tình. hỗ trợ rất tốt", "nhân viên hơi nhiệt tình", "nhân viên nhiệt tình. hỗ trợ rất tốt",
    # "nhân viên hơi nhiệt tình", "nhân viên nhiệt tình. hỗ trợ rất tốt", "nhân viên hơi nhiệt tình",
    # "nhân viên nhiệt tình. hỗ trợ rất tốt", "nhân viên hơi nhiệt tình", "nhân viên nhiệt tình. hỗ trợ rất tốt",
    # "nhân viên hơi nhiệt tình", "nhân viên nhiệt tình. hỗ trợ rất tốt", "nhân viên hơi nhiệt tình"
    ]
    test_result = json.loads(api.get_All(test_list).text)
    # print(test_result['data'])
    result = json.dumps(test_result)
    df = pd.read_json(result, orient='table')
    print(df)