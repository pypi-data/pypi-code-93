# -*- coding: utf-8 -*-

from sentimentApi import Api
import pandas as pd
import ssl
if __name__ == "__main__":
    api = Api(response_format="json")
    print(ssl.OPENSSL_VERSION)
    test_list = ["nhân viên nhiệt tình. hỗ trợ rất tốt"]
    # # print(api.get_preprocess(test_list)
    # # print(api.get_SentimetnPredict(test_list))
    # # print(api.get_AspectWords(test_list))
    # # print(api.get_Opinion(test_list))
    # print(api.get_Qualifer(test_list)[0])
    comment_column = []
    unit_column = []
    sentiment_column = []
    aspect_column = []
    qualifier_column = []
    units = api.get_Opinion(test_list) # [[unit1, unit2], [unit1, unit2]]
    for i in range(len(test_list)):
        comment = test_list[i]
        for unit in units[i]:
            sentiment = api.get_SentimetnPredict([unit])[0]
            aspect = api.get_AspectWords([unit])[0][0]
            qualifier_list = api.get_Qualifer([unit])
            print(qualifier_list)
            # if len(qualifier_list) == 0:
            #     qualifier_list.append('')
            # for qualifier in qualifier_list:
            #     comment_column.append(str(comment))
            #     unit_column.append(str(unit))
            #     sentiment_column.append(str(sentiment))
            #     aspect_column.append(str(aspect))
            #     if qualifier == '':
            #         qualifier_column.append('')
            #     else:
            #         qualifier_column.append(str(qualifier))
                
    # df = pd.DataFrame()
    # df['comment'] = comment_column
    # df['unit'] = unit_column
    # df['sentiment'] = sentiment
    # df['aspect'] = aspect_column
    # df['qualifier'] = qualifier_column

    # print(df)