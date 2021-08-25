import os
import json
import httpx
import typing as t
import base64
from .. import utils
from ..base import ProcManager
from dao.model import OcrModel
from dao import YouDao as YouDaoClient

# TEST_TRANS_URL = "http://127.0.0.1:8000/search/"
# TEST_OCR_URL = "http://127.0.0.1:8000/ocr/"

TRANS_URL = "https://ke.study.163.com/code/textTrans"
OCR_URL = "https://ke.study.163.com/code/ocrTrans"

# os.environ[
#     "token"
# ] = "tYwB%2FcQm2vlyCP1oP%2FRujcnfAMlAJ9ET8JZgyPzHchScEvbrs%2BuXh5XOk78v%2FGS91eloNmbyH3TmBKqtY6EyhqFW%2F%2FKZPfjA4clnffrfjFU%3D"


class ReqBuilder:
    @property
    def use_sdk(self):
        return self.appkey and self.appsecret

    @property
    def use_token(self):
        return bool(self.token)

    def __init__(self, serve_name: str) -> None:
        self.name = serve_name
        self.token = (
            os.environ.get("token")
            if os.environ.get("token")
            else os.environ.get("TOKEN")
        )  # wow ...
        self.appkey = os.environ.get("APP_KEY")
        self.appsecret = os.environ.get("APP_SECRET")
        self.payload = {"url": None, "headers": {}, "json": {}}
        self._post: t.Callable
        # self.req_setup(serve_name)

    def req_setup(self, name: str):
        if self.use_token:
            self.appkey = None
            self.appsecret = None
            servdict = {"trans": TRANS_URL, "ocr": OCR_URL}
            url = servdict[name]
            self.payload["url"] = url
            self.payload["headers"]["token"] = self.token
            self.payload["json"].update(OcrModel.config)
            # The data model that my model.cofig have, but XJ's don't
            self._post = httpx.post
        elif self.use_sdk:
            assert isinstance(self.appkey, str)
            assert isinstance(self.appsecret, str)
            client = YouDaoClient(self.appkey, self.appsecret)
            methdict = {"trans": client.translator().search, "ocr": client.ocr().upload}
            self._post = methdict[name]
        else:
            raise Exception(
                '''To use youdao API you need to get APP_KEY and APP_SECRET\n
                For more detail to visit -> https://ai.youdao.com/'''
            )

    def post(self, **kwargs) -> httpx.Response:
        self.req_setup(self.name)
        if self.use_sdk:
            self.payload = kwargs
        elif self.use_token:
            self.payload["json"].update(kwargs)
            self.payload["timeout"] = 10.0

        res = self._post(**self.payload)
        return res


trans_req = ReqBuilder("trans")
ocr_req = ReqBuilder("ocr")


def translate_post(q: str, **kwargs):
    result = {}
    res = trans_req.post(q=q)
    result["result"] = res
    result.update(kwargs)
    return result


def translate_filter(
    result: httpx.Response, full=False, **rest
) -> t.Union[t.Dict, t.List, None]:
    d = {}
    # test code or errorCode exist
    content = result.json()
    if content.get("code") == 200:
        content = json.loads(content["data"])
    # data goes like { code:200,data:{zhiyun...} }
    # TODO needs to figure out this resp...

    basic = content.get('basic')
    if basic:
        # if basic exists, q must be one word,
        basic = utils.drop(basic, keys=["us-speech", "uk-speech"])
        basic["webdict"] = content.get('webdict').get('url')
        d.update(basic)
        if not full:
            d = d.get("explains")

    else:
        # else many words
        # now needs code == 300 condition test ...
        d["oneline"] = content["translation"]
        return d["oneline"][0]

    return d


def pic2base64(path: str, **kwargs):
    with open(path, 'rb') as f:
        # q = base64.b64encode(f.read())
        return base64.b64encode(f.read()).decode('utf-8')
        # return q.decode('utf-8')


def ocr_post(b64: t.ByteString) -> httpx.Response:
    res = ocr_req.post(img=b64)
    return res


def ocr_ret(res: httpx.Response, **kwargs) -> t.Optional[t.List]:
    text_list = []
    content = res.json()
    if content.get("code") == 200:
        content = json.loads(content["data"])

    Result = content.get("Result")
    if Result:
        items = Result.get('regions')
        for item in items:
            for l in item['lines']:
                text_list.append(l['text'])

        return text_list


def translate(q: str, full: bool = False):
    p = ProcManager(translate_post, translate_filter)
    return p(dict(q=q, full=full))


def easy_ocr(path: str):
    p = ProcManager(pic2base64, ocr_post, ocr_ret)
    return p(dict(path=path))


def easy_translate(q):
    # no no no , what i want is not in the 'basic'
    return translate(q, full=True)


# SIGH -> I used to struggle here, until that I found it's XJ's problem
# self.payload["headers"]["Accept"] = "*/*"
# self.payload["headers"]["Accept-Encoding"] = "gzip, defate, br"
# self.payload["headers"]["Connection"] = "keep-alive"
# funny = {
#     "detectType": "10012",
#     "langType": "auto",
#     "imageType": "1",
#     "docType": "json",
# }
# self.payload["json"].update(funny)
