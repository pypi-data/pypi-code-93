# -*- coding: utf-8 -*-
from labelci.common.exception.labelci_sdk_exception import XuelangCloudException


class DataHubCredential:

    def __init__(self, accessToken) -> None:
        if accessToken is None or accessToken.strip() == "":
            raise XuelangCloudException("InvalidDataHubCredential", "accessToken is should not be none or empty")

        self.accessToken = accessToken


class AlgorithmHubCredential:

    def __init__(self, accessToken) -> None:
        if accessToken is None or accessToken.strip() == "":
            raise XuelangCloudException("InvalidAlgorithmHubCredential", "accessToken is should not be none or empty")

        self.accessToken = accessToken
