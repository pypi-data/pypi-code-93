from datetime import datetime, timedelta
import json
import requests


class AmoOAuthClient:
    """
    Client for authorization
    """

    def __init__(self, args_api, s3_client, logger, is_oauth2=True):
        """
        :param args_api:
        :param s3_client:
        :param is_oauth2:
        """
        self.args_api = args_api or {}
        self.is_oauth2 = is_oauth2
        self.s3_client = s3_client
        self.logger = logger
        self.__check_validity_args()
        if self.is_oauth2:
            self.access_token = None
        else:
            self.auth_cookie_str = None

    def __check_validity_args(self):
        """
        check if args api are valid
        :return:
        """
        if self.is_oauth2:
            must_have_arguments = ["CLIENT_SECRET", "CLIENT_ID", "REDIRECT_URL"]
        else:
            must_have_arguments = ["AMO_USER_LOGIN", "AMO_USER_HASH", "AMO_AUTH_URL"]

        for param in must_have_arguments:
            if param not in self.args_api:
                raise BaseException(
                    "Error. You have to specify {} param in args_api argument".format(
                        param
                    )
                )

    def __save_tokens_s3(self, data):
        """
        Save data with tokens to s3 / set only if is_oauth2=True
        :return:None
        """
        expires_in_datetime = datetime.now() + timedelta(seconds=data["expires_in"])
        data["expires_in_datetime"] = expires_in_datetime.strftime("%Y-%m-%d %H:%M")
        self.logger.info("Modifying config %s...", self.s3_client.secret_dir)
        self.s3_client.create_file(self.s3_client.secret_dir, json.dumps(data))
        self.logger.info(
            "Save new refresh and access token to %s... ", self.s3_client.secret_dir
        )

    def __get_tokens(self, args):
        """
        Get tokens and additional params
        :param args: dict with code or refresh_token
        :return: dict with refresh and access token
        """
        data = {
            "client_secret": self.args_api["CLIENT_SECRET"],
            "client_id": self.args_api["CLIENT_ID"],
            "redirect_uri": self.args_api["REDIRECT_URL"],
        }
        data.update(args)
        resp = requests.post(self.args_api["AUTH_URL"], data=data).json()
        if "refresh_token" not in resp and "access_token" not in resp:
            raise Exception(
                "An error occurred while retrieving auth params: " + str(resp)
            )
        return resp

    def oauth(self):
        """API authorization"""
        params = {
            "USER_LOGIN": self.args_api["AMO_USER_LOGIN"],
            "USER_HASH": self.args_api["AMO_USER_HASH"],
            "type": "json",
        }
        resp = requests.post(self.args_api["AMO_AUTH_URL"], data=params)
        response = resp.json()

        if response["response"]["auth"]:
            self.auth_cookie_str = resp.cookies
            self.logger.info(
                "AmoCRM: Authorized user %s ", self.args_api["AMO_AUTH_URL"]
            )
            return True

        self.logger.info(response["response"])
        raise ValueError("AmoCRM: Not authorized")

    def oauth2(self, code_auth=None):
        """API authorization auth2"""
        # read file from s3 if exists
        try:
            self.logger.info(
                "Load refresh and access token from file %s ", self.s3_client.secret_dir
            )
            response = json.loads(self.s3_client.read_file(self.s3_client.secret_dir))
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            if (
                    now_str < response["expires_in_datetime"]
            ):  # check if access token is still valid
                self.access_token = response["access_token"]
                return

            response = self.__get_tokens(
                args={
                    "refresh_token": response["refresh_token"],
                    "grant_type": "refresh_token",
                }
            )
        except Exception as exp:
            self.logger.warning(
                "If you got here you should to regenerate refresh token"
            )
            if code_auth is None:
                raise NotImplementedError(
                    "You should pass code_auth argument to save the new refresh and access tokens "
                    " (or get and save  them the first time) "
                ) from exp
            response = self.__get_tokens(
                args={"code": code_auth, "grant_type": "authorization_code"}
            )

        self.access_token = response["access_token"]
        self.__save_tokens_s3(response)

    def auth(self, code_auth=None):
        """
        General authorization for both types
        :param code_auth:
        :return:
        """
        if self.is_oauth2:
            self.oauth2(code_auth)
        else:
            self.oauth()

    def get_headers(self):
        """
        :return: headers
        """
        if self.is_oauth2:
            return {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.access_token,
            }
        return {
            "Content-Type": "application/json",
        }

    def get_response_objects(self, url, params, headers=None):
        """
        Ger response by using current auth specification
        :param headers:
        :param url:
        :param params:
        :return: response
        """
        _headers = self.get_headers()
        if headers is not None:
            _headers.update(headers)
        if not self.is_oauth2:
            return requests.get(
                url, cookies=self.auth_cookie_str, headers=_headers, params=params
            )
        return requests.get(url, headers=_headers, params=params)
