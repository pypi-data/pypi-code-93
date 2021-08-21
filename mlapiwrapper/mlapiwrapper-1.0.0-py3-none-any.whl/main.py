from sentimentApi import Api
import ssl
if __name__ == "__main__":
    api = Api(response_format="json")
    print(ssl.OPENSSL_VERSION)
    test_list = ["nhân viên nhiệt tình", "hỗ trợ rất tốt"]
    # print(api.get_preprocess(test_list)
    # print(api.get_SentimetnPredict(test_list))
    # print(api.get_AspectWords(test_list))
    # print(api.get_Opinion(test_list))
    print(api.get_Qualifer(test_list)[0])