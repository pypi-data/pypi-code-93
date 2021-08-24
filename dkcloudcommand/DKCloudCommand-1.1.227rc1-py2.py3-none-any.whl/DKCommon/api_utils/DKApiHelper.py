import json
import pickle
from typing import List

import requests
import six

from .api_utils import validate_and_get_response
from .DKReturnCode import DKReturnCode, SUCCESS, FAIL
from ..DKFileEncode import DKFileEncode
from ..DKPathUtils import (
    normalize_list,
    normalize_recipe_dict,
    UNIX,
    WIN,
)

MESSAGE = "message"
DESCRIPTION = "description"
KITCHEN_JSON = "kitchen.json"

_DEFAULT_TIMEOUT = 60


class DKApiHelper(object):
    def __init__(self, url, token, request_timeout=_DEFAULT_TIMEOUT):
        self._url = url
        self._jwt = token
        self._request_timeout = request_timeout

        if not token:
            raise Exception("Auth token required")

    @property
    def url(self):
        return self._url

    @property
    def headers(self):
        return {"Authorization": "Bearer {}".format(self._jwt)}

    @property
    def token(self):
        return self._jwt

    def create_order(
        self,
        kitchen,
        recipe_name,
        variation_name,
        node_name=None,
        parameters=None,
        now=False,
        ingredient_owner_order_run=None,
    ):
        """
        Full graph
        '/v2/order/create/<string:kitchenname>/<string:recipename>/<string:variationname>',
            methods=['PUT']

        Single node
        '/v2/order/create/graph/<string:kitchenname>/<string:recipename>/<string:variationname>',
            methods=['PUT']

        """
        if kitchen is None or isinstance(kitchen, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with kitchen")
        if recipe_name is None or isinstance(recipe_name, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with recipe_name")
        if variation_name is None or isinstance(variation_name, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with variation_name")

        payload = {"parameters": parameters or {}}

        if now:
            payload["schedule"] = "now"

        if node_name is None:
            url = "%s/v2/order/create/%s/%s/%s" % (self._url, kitchen, recipe_name, variation_name)
        else:
            url = "%s/v2/order/create/graph/%s/%s/%s" % (
                self._url,
                kitchen,
                recipe_name,
                variation_name,
            )
            payload["graph-setting"] = [[node_name]]

        if ingredient_owner_order_run:
            payload["ingredient_owner_order_run"] = ingredient_owner_order_run

        data = json.dumps(payload)

        try:
            response = requests.put(url, data=data, headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, "create_order: exception: %s" % str(c))
        return DKReturnCode(SUCCESS, None, payload=validate_and_get_response(response))

    def list_kitchen(self):
        url = "%s/v2/kitchen/list" % (self._url)
        try:
            response = requests.get(url, headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError, TypeError) as c:
            return DKReturnCode(FAIL, "list_kitchen: exception: %s" % str(c))

        rdict = validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None, payload=rdict["kitchens"])

    def get_kitchen_dict(self, kitchen_name):
        rv = self.list_kitchen()

        kitchens = rv.payload if rv.ok() else None

        if kitchens is None:
            return None

        for kitchen in kitchens:
            if isinstance(kitchen, dict) is True and "name" in kitchen and kitchen_name == kitchen["name"]:
                return kitchen
        return None

    def orderrun_detail(self, kitchen, pdict):
        """
        Get the details about a Order-Run (fka Serving)

        :param kitchen: kitchen name
        :param pdict: parameter dictionary
        :return: DKReturnCode
        """
        if kitchen is None or isinstance(kitchen, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with kitchen")

        url = "%s/v2/order/details/%s" % (self._url, kitchen)
        try:
            response = requests.post(url, data=json.dumps(pdict), headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError) as c:
            s = "orderrun_detail: exception: %s" % str(c)
            return DKReturnCode(FAIL, s)

        rdict = validate_and_get_response(response)

        return DKReturnCode(SUCCESS, None, payload=rdict)

    def create_kitchen(self, existing_kitchen_name, new_kitchen_name, description, message=None):
        if existing_kitchen_name is None or new_kitchen_name is None:
            return DKReturnCode(FAIL, "Need to supply an existing kitchen name")

        if (
            isinstance(existing_kitchen_name, six.string_types) is False
            or isinstance(new_kitchen_name, six.string_types) is False
        ):
            return DKReturnCode(FAIL, "Kitchen name needs to be a string")

        if message is None or isinstance(message, six.string_types) is False:
            message = "update_kitchens"

        data = json.dumps({MESSAGE: message, DESCRIPTION: description})
        url = "%s/v2/kitchen/create/%s/%s" % (self._url, existing_kitchen_name, new_kitchen_name)
        try:
            response = requests.put(url, data=data, headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError, TypeError) as c:
            return DKReturnCode(FAIL, "create_kitchens: exception: %s" % str(c))

        return DKReturnCode(SUCCESS, None, payload=validate_and_get_response(response))

    def update_kitchen(self, update_kitchen, message):
        if update_kitchen is None:
            return False
        if isinstance(update_kitchen, dict) is False or "name" not in update_kitchen:
            return False
        if message is None or isinstance(message, six.string_types) is False:
            message = "update_kitchens"
        data = json.dumps(
            {
                KITCHEN_JSON: update_kitchen,
                MESSAGE: message,
            }
        )
        url = "%s/v2/kitchen/update/%s" % (self._url, update_kitchen["name"])
        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError, TypeError) as c:
            print("update_kitchens: exception: %s" % str(c))
            return None
        validate_and_get_response(response)
        return True

    def order_pause(self, kitchen, order_id):
        if kitchen is None or isinstance(kitchen, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with kitchen")
        if kitchen is None or isinstance(order_id, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with order_id")
        url = "%s/v2/order/pause/%s" % (self._url, order_id)
        try:
            params = dict()
            params["kitchen_name"] = kitchen
            response = requests.put(url, data=json.dumps(params), headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, "order_pause: exception: %s" % str(c))

        validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None)

    def order_unpause(self, kitchen, order_id):
        if kitchen is None or isinstance(kitchen, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with kitchen")
        if kitchen is None or isinstance(order_id, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with order_id")
        url = "%s/v2/order/unpause/%s" % (self._url, order_id)
        try:
            params = dict()
            params["kitchen_name"] = kitchen
            response = requests.put(url, data=json.dumps(params), headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, "order_unpause: exception: %s" % str(c))

        validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None)

    def order_delete_all(self, kitchen):
        if kitchen is None or isinstance(kitchen, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with kitchen")
        url = "%s/v2/order/deleteall/%s" % (self._url, kitchen)
        try:
            response = requests.delete(url, headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, "order_delete_all: exception: %s" % str(c))

        validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None)

    def orderrun_get_logs(self, kitchen_name, orderrun_id, data):
        if orderrun_id is None or not isinstance(orderrun_id, six.string_types):
            return DKReturnCode(FAIL, "issue with orderrun id")
        if kitchen_name is None or not isinstance(kitchen_name, six.string_types):
            return DKReturnCode(FAIL, "issue with kitchen name")
        if data is None or not isinstance(data, dict):
            data = dict()
        url = "%s/v2/order/logs/%s/%s" % (self._url, kitchen_name, orderrun_id)
        try:
            response = requests.get(url, data=json.dumps(data), headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, "orderrun_get_logs: exception: %s" % str(c))

        rdict = validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None, payload=rdict)

    def delete_kitchen(self, existing_kitchen_name, message=None, synchronous_delete=False):
        if existing_kitchen_name is None:
            return DKReturnCode(FAIL, "Need to supply an existing kitchen name")

        if isinstance(existing_kitchen_name, six.string_types) is False:
            return DKReturnCode(FAIL, "Kitchen name needs to be a string")

        if message is None or isinstance(message, six.string_types) is False:
            message = "delete_kitchen"

        data = json.dumps({"synchronous-delete": synchronous_delete, MESSAGE: message})
        url = "%s/v2/kitchen/delete/%s" % (self._url, existing_kitchen_name)
        try:
            response = requests.delete(url, data=data, headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError, TypeError) as c:
            return DKReturnCode(FAIL, "delete_kitchens: exception: %s" % str(c))

        validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None)

    def get_recipe(self, kitchen: str, recipe: str, list_of_files: List[str] = None) -> DKReturnCode:
        if kitchen is None or isinstance(kitchen, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with kitchen parameter")

        if recipe is None or isinstance(recipe, six.string_types) is False:
            return DKReturnCode(FAIL, "issue with recipe parameter")

        url = "%s/v2/recipe/get/%s/%s" % (self._url, kitchen, recipe)
        try:
            if list_of_files is not None:
                params = dict()
                params["recipe-files"] = normalize_list(list_of_files, UNIX)
                response = requests.post(
                    url, data=json.dumps(params), headers=self.headers, timeout=self._request_timeout
                )
            else:
                response = requests.post(url, headers=self.headers, timeout=self._request_timeout)
        except (requests.RequestException, ValueError, TypeError) as c:
            return DKReturnCode(FAIL, "get_recipe: exception: %s" % str(c))

        rdict = validate_and_get_response(response)
        if recipe not in rdict["recipes"]:
            message = "Unable to find recipe %s or the stated files within the recipe." % recipe
            return DKReturnCode(FAIL, message)
        else:
            rdict = DKFileEncode.binary_files(DKFileEncode.B64DECODE, rdict)
            return DKReturnCode(SUCCESS, None, payload=normalize_recipe_dict(rdict, WIN))

    @staticmethod
    def login(url, username, password, request_timeout=_DEFAULT_TIMEOUT):

        try:
            response = requests.post(
                "%s/v2/login" % url, data={"username": username, "password": password}, timeout=request_timeout
            )
        except (requests.RequestException, ValueError, TypeError) as c:
            print("login: exception: %s" % str(c))
            return

        try:
            validate_and_get_response(response)
        except Exception as e:
            print("login: exception: %s" % str(e))
            return

        if response is not None:
            if response.text is not None and len(response.text) > 10:
                if response.text[0] == '"':
                    return response.text.replace('"', "").strip()

                return response.text
            else:
                print("Invalid jwt token returned from server")
        else:
            print("login: error logging in")

        return None

    @staticmethod
    def valid_token(url: str, token: str, request_timeout=_DEFAULT_TIMEOUT) -> bool:
        try:
            headers = {"Authorization": "Bearer {}".format(token)}
            response = requests.get("%s/v2/validatetoken" % url, headers=headers, timeout=request_timeout)
            validate_and_get_response(response)
            return True
        except Exception:
            return False
