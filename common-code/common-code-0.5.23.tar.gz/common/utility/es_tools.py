from rest_framework.views import APIView
from common.decorator import METHOD_GET, METHOD_POST, METHOD_PUT, METHOD_DELETE, requests_decorator
from common.logging_config import logger
from common.rest_extend.response import Results, UPSTREAM_SERVER_ERROR_CODE, RESTResponse
from common.rest_extend.decorator import vaild_decorator

DEFAULT_ES_URL = "config.esserver.eshosturl"
DEFAULT_INDEX = "config.esserver.pointtableindex"
DEFAULT_ESSERVER_VERSION = "config.esserver.version"


class ESRequests:
    ES_URL = DEFAULT_ES_URL
    INDEX = DEFAULT_INDEX
    BASE_ES_URL = "{host}?index={index}".format(host=ES_URL, index=INDEX)
    ESSERVER_VERSION = DEFAULT_ESSERVER_VERSION

    def __new__(cls, *args, **kwargs):
        ES_URL = kwargs.pop("ES_URL", None)
        INDEX = kwargs.pop("INDEX", None)
        ESSERVER_VERSION = kwargs.pop("ESSERVER_VERSION", None)
        if ES_URL:
            cls.ES_URL = ES_URL
        if INDEX:
            cls.INDEX = INDEX
        if ESSERVER_VERSION:
            cls.ESSERVER_VERSION = ESSERVER_VERSION
        # assert (
        #     cls.ES_URL == DEFAULT_ES_URL
        #     or cls.INDEX == DEFAULT_INDEX
        #     or cls.ESSERVER_VERSION == DEFAULT_ESSERVER_VERSION
        # ), f"'ES_URL'={ES_URL} or 'INDEX'={INDEX} or 'DEFAULT_ESSERVER_VERSION'={DEFAULT_ESSERVER_VERSION}"

        cls.BASE_ES_URL = "{host}?index={index}".format(host=cls.ES_URL, index=cls.INDEX)
        logger.info(cls.ES_URL, cls.INDEX, cls.ESSERVER_VERSION, cls.BASE_ES_URL)
        return super().__new__(cls, *args, **kwargs)

    def get(self, _id=None, data: dict = None):
        """

        :param _id:
        :param data:
        :return:
        """
        if _id:
            url = "{base_url}&id={id}".format(base_url=self.BASE_ES_URL, id=_id)
        else:
            url = self.BASE_ES_URL
        if not data:
            data = {}

        data = {"version": self.ESSERVER_VERSION, "data": data}
        results, response = self.get_requests_response(url, METHOD_GET, data)
        if results.code == 200:
            data = response.json()
            data = data.get("data")
            results.data = data

        return results

    def post(self, data, _id=None):
        """

        :param data:
        :param _id:
        :return:
        """
        if _id:
            url = "{base_url}&id={id}".format(base_url=self.BASE_ES_URL, id=_id)
        else:
            url = self.BASE_ES_URL
        body = {"version": self.ESSERVER_VERSION, "data": data}
        results, response = self.get_requests_response(url, METHOD_POST, body)
        return results

    def put(self, _id, data):
        """
        :param _id:
        :param data:
        :return:
        """
        url = "{base_url}&id={id}".format(base_url=self.BASE_ES_URL, id=_id)
        body = {"version": self.ESSERVER_VERSION, "data": data}

        results, response = self.get_requests_response(url, METHOD_PUT, body)
        return results

    def delete(self, _id):
        """
        :param _id:
        :return:
        """
        url = "{base_url}&id={id}".format(base_url=self.BASE_ES_URL, id=_id)
        body = {"version": self.ESSERVER_VERSION, "data": {}}
        results, response = self.get_requests_response(url, METHOD_DELETE, body)
        return results

    @requests_decorator(failure_skip=False)
    def download(self, url, *args):
        response = args[0]
        return response

    def get_requests_response(self, url, method, data=None) -> tuple:
        """
        请求es接口，并进行初步判断
        :param url:
        :param method:
        :param data:
        :return: tuple-》results，response
        """
        results = Results()
        # if isinstance(data, dict) or isinstance(data, list):
        #     data = json.dumps(data)
        response = None
        try:
            update_time = data.pop('update_time', None)
            create_time = data.pop('create_time', None)
            response = self.download(url, method=method, json=data)
            if response != None:
                if response.status_code >= 500:
                    results.code = UPSTREAM_SERVER_ERROR_CODE
                else:
                    results.code = response.status_code
                results.describe = response.json().get("describe")
            else:
                results.code = 500
                results.describe = "download error"

                # data = response.json()
                # describe = data.get("describe")
                # # 判断上层服务是否正常响应
                # if response.status_code == 400 and (
                #         "pointtable not found  id:" in describe or "删除一个不存在" in describe
                # ):
                #     results.code = 200
                # else:
                #     results.code = UPSTREAM_SERVER_ERROR_CODE
                #     results.describe = describe

        except Exception as e:
            results.code = UPSTREAM_SERVER_ERROR_CODE
            results.describe = str(e)
        return results, response


class ESView(APIView):
    tools: ESRequests = None

    def get(self, request, obj_ser=None, data=None):
        _id = request.GET.get("id")
        if not data:
            _data = data
        else:
            _data = request.data.get("data")
        results = self.tools.get(_id, _data)

        return RESTResponse(results)

    def post(self, request, obj_ser=None, _id=None):
        results = self.tools.post(obj_ser.validated_data.get("data"), _id=_id)
        return RESTResponse(results)

    def put(self, request, obj_ser=None, data=None, need_results=False):
        _id = request.GET.get("id")
        results = self.validate_id(_id)
        if not results:
            data = obj_ser.validated_data.get("data")
            if '_source' in data.keys():
                data = data.get('_source')
            results = self.tools.put(_id=_id, data=data)
        return RESTResponse(results)

    def delete(self, request, obj_ser=None, data=None, need_results=False):
        _id = request.GET.get("id")
        results = self.validate_id(_id)
        if not results:
            results = self.tools.delete(_id)
        return RESTResponse(results)

    def validate_id(self, _id):
        results = Results()
        if not _id:
            results.describe = "id cannot be empty!!!"
            return results

    def vaild_data(self, request, func, obj_ser):
        external_wrapper = vaild_decorator(obj_serializer=obj_ser)
        internal_wrapper = external_wrapper(func)
        res = internal_wrapper(self, request)
        print(res)
