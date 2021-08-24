import functools
from typing import *

from cached_property import cached_property

from quicly.model import QxAttr, QxOptional
from quicly.decorator import QxDecoratorHook, QxDecorator
from quicly.conf import QxConf, QxGlobalConf
from quicly.urlutils import QxUrl
from quicly.result import QxResult, QxError, QxFinish, QxHttpResult, QxTemplate
from quicly import jsonutils as json
from quicly.patterns import PATTERN_URL_QUERY
from quicly.inspectutils import QxInspectUtils
from quicly.session import QxSessionFactory, QxSession

import re
import copy
import threading
import uuid as _uuid
import inspect
import bson
import pickle
import pyDes
from collections import OrderedDict
from datetime import datetime
import uuid
import yaml


_RPC_METHODS = {'RPC'}
_HTTP_METHODS = {'GET', 'PUT', 'PATCH', 'DELETE', 'POST', 'HEAD', 'OPTIONS'}
_METHODS = _RPC_METHODS.union(_HTTP_METHODS)
_VAR_DEF_PATTERN = re.compile(r'{[_A-Z]+[_0-9A-Z]*(:[^}]*)?}', re.I)
_VAR_VAL_PATTERN = '[^/]*'


class QxCaseInsensitiveDict(OrderedDict):
  _mapping = dict()

  def __init__(self, *al, **kw):
    super(QxCaseInsensitiveDict, self).__init__(*al, **kw)
    for k, v in super(QxCaseInsensitiveDict, self).items():
      self._mapping[k.lower()] = k

  def get(self, k: str, default: Any = None) -> Any:
    kk = self._mapping.get(k.lower())
    if kk:
      ret = super(QxCaseInsensitiveDict, self).get(kk, default)
    else:
      ret = default
    return ret

  def __getitem__(self, k: str):
    return self.get(k)

  def __setitem__(self, k: str, v: Any):
    self._mapping[k.lower()] = k
    super(QxCaseInsensitiveDict, self).__setitem__(k, v)


QxHeaders = QxCaseInsensitiveDict
QxCookies = QxCaseInsensitiveDict


class QxRequest(object):
  def __init__(self, method: str, url: str, headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None, body: Optional[bytes] = None, form: Optional[Dict[str, str]] = None, files: List = None, request_uuid: str = None, request_time: Optional[datetime] = None):
    self._method = method.upper()
    self._url = QxUrl(url)
    self._headers = QxHeaders(headers.items() if isinstance(headers, dict) else [])
    self._cookies = QxCookies(cookies.items() if isinstance(cookies, dict) else [])
    self._body = body if isinstance(body, (bytes, str)) else b''
    self._data = [self._body]
    self._args = dict()
    self._form = form if isinstance(form, dict) else {}
    self._files = files if isinstance(files, list) else []
    self._request_uuid = request_uuid if request_uuid else str(uuid.uuid4())
    self._request_time = request_time if request_time else datetime.utcnow()
    self._session = None

  @property
  def method(self) -> str:
    return self._method

  @property
  def url(self) -> QxUrl:
    return self._url

  @property
  def headers(self) -> Dict[str, str]:
    return self._headers

  @property
  def cookies(self) -> Dict[str, str]:
    return self._cookies

  @property
  def body(self) -> Optional[bytes]:
    return self._body

  @property
  def data(self) -> Any:
    return self._data[-1] if self._data else None

  @data.setter
  def data(self, data: Any):
    self._data.append(data)

  @property
  def args(self) -> Dict:
    return self._args

  @args.setter
  def args(self, args):
    self._args = args

  @property
  def form(self) -> Dict[str, str]:
    return self._form

  @property
  def files(self) -> List:
    return self._files

  @property
  def request_uuid(self):
    return self._request_uuid

  @property
  def request_time(self):
    return self._request_time

  @property
  def session(self):
    return self._session

  @session.setter
  def session(self, session: QxSession):
    self._session = session

  def get_content_type(self):
    items = [x.strip().lower() for x in self.headers.get('Content-Type', '').split(';')]
    content_type = items[0]
    if len(items) > 1 and items[1].startswith('charset:'):
      charset = items[1].split(':', maxsplit=1)[-1]
    else:
      charset = None
    return content_type, charset

  def get_accept(self):
    accept = set([x.strip().lower() for x in self.headers.get('Accept', '').split(';')])
    charset = self.headers.get('Accept-Charset', None)
    return accept, charset

  def get_content_encryption(self):
    items = [x.strip() for x in self.headers.get('X-Qx-Content-Encryption', '').split(';')]
    if len(items) < 2:
      items.append('')
    return tuple(items)

  def get_accept_encryption(self):
    return self.headers.get('X-Qx-Accept-Encryption', '')

  def parse_args(self):
    args = dict()

    for arg_t in (self.cookies.get('qx-args'), self.headers.get('x-qx-args')):
      if not isinstance(arg_t, str):
        continue

      try:
        arg_t_d = json.loads(arg_t)
        if isinstance(arg_t_d, dict):
          for k, v in arg_t_d.items():
            args[k] = v
      except (pickle.PickleError, json.JSONDecodeError, TypeError, ValueError):
        if PATTERN_URL_QUERY.fullmatch(arg_t) and arg_t.count('"') == 0 and arg_t.count("'") == 0 and (arg_t.count('&') > 0 or arg_t.count('=') > 0):
          for k, v in QxUrl.parse_query_str(arg_t).items():
            args[k] = v

    if isinstance(self.url.query, dict):
      for k, v in self.url.query.items():
        args[k] = v

    if isinstance(self.form, dict):
      for k, v in self.form.items():
        args[k] = v

    if isinstance(self.data, dict):
      for k, v in self.data.items():
        args[k] = v

    self.args = args

  @property
  def sessionid(self):
    return self.args.get('__QXSESSIONID__', self.headers.get('X-QX-SESSIONID', self.cookies.get('QXSESSIONID')))


class QxResponse(object):
  def __init__(self, request: QxRequest, code: int = 0, headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None, body: Optional[bytes] = ''):
    self._request = request
    self._code = code
    self._headers = QxHeaders(headers.items() if isinstance(headers, dict) else [])
    self._cookies = QxCookies(cookies.items() if isinstance(cookies, dict) else [])
    self._body = body
    self._data = [body]

  @property
  def request(self) -> QxRequest:
    return self._request

  @property
  def code(self) -> int:
    return self._code

  @property
  def headers(self) -> Dict[str, str]:
    return self._headers

  @property
  def cookies(self) -> Dict[str, str]:
    return self._cookies

  @property
  def body(self) -> Optional[bytes]:
    return self._body

  @property
  def data(self) -> Any:
    return self._data[-1] if self._data else None

  @data.setter
  def data(self, data: Any):
    self._data.append(data)


class QxHandlerFunc(object):
  def __init__(self, func: Callable, args: Optional[Dict[str, QxAttr]], result: Optional[QxAttr] = None):
    self._func = func if callable(func) else lambda: QxError(QxError.CODE_501_NOT_IMPLEMENTED)
    self._args = args if isinstance(args, dict) else dict()
    self._result = result
    self._func_cached = None

  @property
  def func(self) -> Callable:
    return self._func

  @property
  def args(self) -> Optional[Dict[str, QxAttr]]:
    return self._args

  @property
  def result(self) -> Optional[QxAttr]:
    return self._result

  def _check_args(self, args: Dict[str, Any]) -> bool:
    err = None

    if isinstance(args, dict):
      for k, v in self.args.items():
        if k in args or isinstance(v, QxOptional):
          if not v.check(args.get(k)):
            err = QxError(code=QxError.CODE_400_BAD_REQUEST, reason='INVALID_ARGS', data={
              'name': k,
            })
            break
        else:
          err = QxError(code=QxError.CODE_400_BAD_REQUEST, reason='MISSING_REQUIRED_ARGS', data={
            'name': k,
          })
    else:
      err = QxError(code=QxError.CODE_400_BAD_REQUEST)

    return err

  def _process_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
    ret = dict()

    if isinstance(args, dict):
      for k, v in args.items():
        if isinstance(self.args, dict) and k in self.args and isinstance(self.args[k], QxAttr):
          v = self.args[k].value(v)
        ret[k] = copy.copy(v)

    return ret

  def _check_result(self, result: Any) -> bool:
    ret = True

    if isinstance(self.result, QxAttr) and not self.result.check(result):
      ret = False

    return ret

  def _process_result(self, result: Any) -> Any:
    ret = None

    if isinstance(self.result, QxAttr):
      if self.result.check(result):
        result = self.result.value(result)
        ret = copy.copy(result)
    else:
      ret = result

    return ret

  def _get_func(self) -> Callable:
    if callable(self._func_cached):
      func = self._func_cached
    else:
      func = self._func

      if QxInspectUtils.is_class_method(func):
        cls = QxInspectUtils.get_method_class(func)
        func = functools.partial(func, cls)
      elif QxInspectUtils.is_inst_method(func):
        cls = QxInspectUtils.get_method_class(func)
        inst_k = '__qx_handler_inst__'
        inst = getattr(cls, inst_k, None)
        if inst is None or not isinstance(inst, cls):
          inst = cls()
          setattr(cls, inst_k, inst)
        func = functools.partial(func, inst)
      self._func_cached = func
    return func

  def __call__(self, request: QxRequest) -> QxResult:
    if callable(self._func):
      err = self._check_args(request.args)
      if err is None or not isinstance(err, Exception):
        request.args = self._process_args(request.args)

        try:
          func = self._get_func()

          kw_full = dict(
            request=request,
            args=request.args,
          )

          func_args = inspect.getfullargspec(func)

          kw = kw_full if func_args.varkw else dict([x for x in kw_full.items() if x[0] in func_args.args])

          result = func(**kw)
        except QxFinish as f:
          result = f
        except QxError as e:
          result = e
        except QxResult as r:
          result = r
        except Exception as e:
          import traceback
          traceback.print_exc()
          result = QxError(data=e)

        if not isinstance(result, QxResult):
          if isinstance(result, Exception):
            import traceback
            traceback.print_exc()
            result = QxError(data=result)
          else:
            result = QxFinish(data=result)
      else:
        result = err if isinstance(err, QxError) else QxError(code=QxError.CODE_400_BAD_REQUEST)
    else:
      result = QxError(code=QxError.CODE_501_NOT_IMPLEMENTED)

    try:
      assert isinstance(result, QxResult)
    except AssertionError as e:
      result = QxError(data=e)

    return result


class QxHandlerMeta(object):
  def __init__(self, path: str, methods: Union[str, List[str], Tuple[str], Set[str]] = None):
    self._path, self._pattern, self._varlist = self._process_path(path)
    self._methods = self._process_methods(methods)

  @property
  def path(self) -> str:
    return self._path

  @property
  def pattern(self) -> Optional[re.Pattern]:
    return self._pattern

  @property
  def varlist(self) -> Tuple[str]:
    return self._varlist

  @property
  def methods(self) -> Set[str]:
    return self._methods

  @staticmethod
  def _process_path(path: str) -> Tuple[str, Optional[re.Pattern], Tuple[str]]:
    matches = list(_VAR_DEF_PATTERN.finditer(path))

    pattern = None
    varlist = []

    if len(matches):
      p = ''

      i = 0
      for m in matches:
        j, k = m.span()

        var_fields = path[j + 1:k - 1].split(':', maxsplit=1)
        var_name = var_fields[0].strip()
        var_pattern = var_fields[1].strip() if len(var_fields) >= 2 else _VAR_VAL_PATTERN

        p += path[i:j]
        p += f'({var_pattern})'

        varlist.append(var_name)

        i = k

      p += path[i:]

      pattern = re.compile(p)

    varlist = tuple(varlist)

    return path, pattern, varlist

  @staticmethod
  def _process_methods(methods: Union[str, List[str], Tuple[str], Set[str]]) -> Set[str]:
    if isinstance(methods, str):
      methods = methods.upper()
      if methods in _METHODS:
        ret = {methods}
      elif methods == 'RPC':
        ret = _RPC_METHODS
      elif methods == 'HTTP':
        ret = _HTTP_METHODS
      else:
        ret = _METHODS
    elif isinstance(methods, (list, tuple, set)):
      ret = set()
      for m in methods:
        if not isinstance(m, str):
          continue
        m = m.upper()

        if m in _METHODS:
          ret.add(m)
        elif m == 'RPC':
          ret += _RPC_METHODS
        elif m == 'HTTP':
          ret += _HTTP_METHODS
        elif m == '*':
          ret += _METHODS

      if not ret:
        ret = _METHODS
    else:
      ret = _METHODS

    return ret


class QxHandler(object):
  def __init__(self, func: QxHandlerFunc, meta: QxHandlerMeta):
    self._func = func
    self._meta = meta

  @property
  def func(self) -> QxHandlerFunc:
    return self._func

  @property
  def meta(self) -> QxHandlerMeta:
    return self._meta


class QxHandlers(object):
  def __init__(self):
    self._handlers = OrderedDict()  # type: Dict[str, QxHandler]

  @property
  def handlers(self) -> Dict[str, QxHandler]:
    return self._handlers

  def clear(self):
    self._handlers.clear()

  def register(self, handler: QxHandler):
    self._handlers[handler.meta.path] = handler

  def match(self, path: str, method: Optional[str] = None) -> Tuple[Optional[QxHandler], List[Tuple[str, str]]]:
    handler = self._handlers.get(path)
    args = list()

    if not isinstance(handler, QxHandler):
      for handler_t in self._handlers.values():
        if isinstance(handler_t, QxHandler) and isinstance(handler_t.meta.pattern, re.Pattern) and handler_t.meta.pattern.fullmatch(path):
          handler = handler_t
          args_t = handler_t.meta.pattern.findall(path)[0]
          for i in range(len(args_t)):
            args.append((
              handler_t.meta.varlist[i],
              args_t[i],
            ))
          break

    if isinstance(handler, QxHandler) and isinstance(method, str) and len(method) and method.upper() not in handler.meta.methods:
      handler = None

    return handler, args


class QxDecoder(object):
  def can_decode(self, request: QxRequest) -> bool:
    raise NotImplementedError()

  def decode(self, request: QxRequest) -> QxRequest:
    raise NotImplementedError()


class QxDecoderLayer(QxDecoder):
  def __init__(self, *decoders):
    self._decoders = [x for x in decoders if isinstance(x, QxDecoder)]

  @property
  def decoders(self) -> List[QxDecoder]:
    return self._decoders

  def can_decode(self, request: QxRequest) -> bool:
    return True

  def decode(self, request: QxRequest) -> QxRequest:
    for decoder in self.decoders:
      if decoder.can_decode(request):
        request = decoder.decode(request)
        break
    return request


class QxDecoderLayers(QxDecoder):
  def __init__(self, *layers):
    self._layers = [x for x in layers if isinstance(x, QxDecoderLayer)]

  @property
  def layers(self) -> List[QxDecoderLayer]:
    return self._layers

  def can_decode(self, request: QxRequest) -> bool:
    return True

  def decode(self, request: QxRequest) -> QxRequest:
    for layer in self.layers:
      if layer.can_decode(request):
        request = layer.decode(request)
    return request


class QxEncoder(object):
  def can_encode(self, response: QxResponse) -> bool:
    raise NotImplementedError()

  def encode(self, response: QxResponse) -> QxResponse:
    raise NotImplementedError()


class QxEncoderLayer(QxEncoder):
  def __init__(self, *encoders):
    self._encoder = [x for x in encoders if isinstance(x, QxEncoder)]

  @property
  def encoders(self) -> List[QxEncoder]:
    return self._encoder

  def can_encode(self, response: QxResponse) -> bool:
    return True

  def encode(self, response: QxResponse) -> QxResponse:
    for encoder in self.encoders:
      if encoder.can_encode(response):
        response = encoder.encode(response)
        break
    return response


class QxEncoderLayers(QxEncoder):
  def __init__(self, *layers):
    self._layers = [x for x in layers if isinstance(x, QxEncoderLayer)]

  @property
  def layers(self) -> List[QxEncoderLayer]:
    return self._layers

  def can_encode(self, response: QxResponse) -> bool:
    return True

  def encode(self, response: QxResponse) -> QxResponse:
    for layer in self.layers:
      if layer.can_encode(response):
        response = layer.encode(response)
        break
    return response


class QxCoder(QxEncoder, QxDecoder):
  _lock = threading.Lock()
  _inst = None

  def __new__(cls, *al, **kw):
    if not isinstance(cls._inst, cls):
      with cls._lock:
        if not isinstance(cls._inst, cls):
          cls._inst = super().__new__(cls, *al, **kw)
    return cls._inst

  def can_encode(self, response: QxResponse) -> bool:
    raise NotImplementedError()

  def encode(self, response: QxResponse) -> QxResponse:
    raise NotImplementedError()

  def can_decode(self, request: QxRequest) -> bool:
    raise NotImplementedError()

  def decode(self, request: QxRequest) -> QxRequest:
    raise NotImplementedError()


class QxDESCoder(QxCoder):
  @staticmethod
  def _mk_des(p: str):
    return pyDes.des(key=p, mode=pyDes.ECB, IV=None, pad=None, padmode=pyDes.PAD_NORMAL)

  def can_encode(self, response: QxResponse) -> bool:
    return response.request.get_accept_encryption().lower() == 'des'

  def encode(self, response: QxResponse) -> QxResponse:
    p = str(_uuid.uuid4())
    des = self._mk_des(p)
    data = des.encrypt(response.data)
    response.data = data
    return response

  def can_decode(self, request: QxRequest) -> bool:
    e, p = request.get_content_encryption()
    return e.lower() == 'des' and p

  def decode(self, request: QxRequest) -> QxRequest:
    _, p = request.get_content_encryption()
    des = self._mk_des(p)
    data = des.decrypt(request.data)
    request.data = data
    return request


class QxPickleCoder(QxCoder):
  def can_encode(self, response: QxResponse) -> bool:
    accept, _ = response.request.get_accept()
    return 'application/pickle' in accept

  def encode(self, response: QxResponse) -> QxResponse:
    data = pickle.dumps(response.data)
    response.data = data
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Length'] = str(len(data))
    return response

  def can_decode(self, request: QxRequest) -> bool:
    if isinstance(request.data, bytes) and len(request.data) >= 2 and request.data[0] == 128 and request.data[1] == 4:
      try:
        pickle.loads(request.data)
        ret = True
      except (pickle.PickleError, TypeError, ValueError):
        ret = False
    else:
      ret = False
    return ret

  def decode(self, request: QxRequest) -> QxRequest:
    data = pickle.loads(request.data)
    request.data = data
    return request


class QxBsonCoder(QxCoder):
  def can_encode(self, response: QxResponse) -> bool:
    accept, _ = response.request.get_accept()
    return 'application/bson' in accept and isinstance(response.data, dict)

  def encode(self, response: QxResponse) -> QxResponse:
    data = bson.encode(response.data)
    response.data = data
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Length'] = str(len(data))
    return response

  def can_decode(self, request: QxRequest) -> bool:
    if isinstance(request.data, bytes) and len(request.data):
      try:
        bson.decode(request.data)
        ret = True
      except (bson.errors.BSONError, TypeError, ValueError):
        ret = False
    else:
      ret = False
    return ret

  def decode(self, request: QxRequest) -> QxRequest:
    data = bson.decode(request.data)
    request.data = data
    return request


class QxYamlCoder(QxCoder):
  def can_encode(self, response: QxResponse) -> bool:
    accept, _ = response.request.get_accept()

    ret = False

    if 'application/yaml' in accept:
      ret = True

    return ret

  def encode(self, response: QxResponse) -> QxResponse:
    _, charset = response.request.get_accept()
    if not charset:
      charset = QxGlobalConf().charset
    data = yaml.safe_dump(response.data)
    if isinstance(data, str):
      data = data.encode(charset)
    response.data = data
    response.headers['Content-Type'] = 'application/yaml'
    response.headers['Content-Length'] = str(len(data))
    return response

  def can_decode(self, request: QxRequest) -> bool:
    if isinstance(request.data, (str, bytes)) and len(request.data):
      try:
        yaml.safe_load(request.data)
        ret = True
      except (yaml.YAMLError, TypeError, ValueError):
        ret = False
    else:
      ret = False
    return ret

  def decode(self, request: QxRequest) -> QxRequest:
    _, charset = request.get_content_type()
    if not charset:
      charset = QxGlobalConf().charset
    data = request.data
    if isinstance(data, bytes):
      data = data.decode(charset)
    request.data = yaml.safe_load(data)
    return request


class QxJsonCoder(QxCoder):
  def can_encode(self, response: QxResponse) -> bool:
    accept, _ = response.request.get_accept()

    ret = False

    if 'application/json' in accept:
      ret = True
    elif isinstance(response.data, dict) and 'code' in response.data and 'reason' in response.data and 'message' in response.data and 'data' in response.data:
      ret = True

    return ret

  def encode(self, response: QxResponse) -> QxResponse:
    _, charset = response.request.get_accept()
    if not charset:
      charset = QxGlobalConf().charset
    data = json.dumps(response.data, indent=0, ensure_ascii=False)
    if isinstance(data, str):
      data = data.encode(charset)
    response.data = data
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Length'] = str(len(data))
    return response

  def can_decode(self, request: QxRequest) -> bool:
    if isinstance(request.data, (str, bytes)) and len(request.data):
      try:
        json.loads(request.data)
        ret = True
      except (json.JSONDecodeError, TypeError, ValueError):
        ret = False
    else:
      ret = False
    return ret

  def decode(self, request: QxRequest) -> QxRequest:
    _, charset = request.get_content_type()
    if not charset:
      charset = QxGlobalConf().charset
    data = request.data
    if isinstance(data, bytes):
      data = data.decode(charset)
    request.data = json.loads(data)
    return request


class QxServer(object):
  _global_handlers = OrderedDict()

  @classmethod
  def get_handlers(cls, name: str):
    handlers = cls._global_handlers.get(name)
    if not isinstance(handlers, QxHandlers):
      handlers = QxHandlers()
      cls._global_handlers[name] = handlers
    return handlers

  ################################################################################

  _decoders = QxDecoderLayers(
    QxDecoderLayer(  # 解密
      QxDESCoder(),
    ),
    QxDecoderLayer(  # 解码
      QxPickleCoder(),
      QxBsonCoder(),
      QxYamlCoder(),
      QxJsonCoder(),
    ),
  )

  _encoders = QxEncoderLayers(
    QxEncoderLayer(  # 编码
      QxPickleCoder(),
      QxBsonCoder(),
      QxYamlCoder(),
      QxJsonCoder(),
    ),
    QxEncoderLayer(  # 加密
      QxDESCoder(),
    ),
  )

  ################################################################################

  def __init__(self, name: str = None, fn_render_template: Callable = None):
    self._name = name
    self._fn_render_template = fn_render_template
    self._conf = QxConf(parent=QxGlobalConf())

  @property
  def name(self):
    return self._name

  @property
  def fn_render_template(self) -> Callable:
    return self._fn_render_template

  @property
  def conf(self) -> QxConf:
    return self._conf

  @cached_property
  def handlers(self) -> QxHandlers:
    return self.get_handlers(self.name)

  @cached_property
  def decoders(self) -> QxDecoderLayers:
    return self._decoders

  @cached_property
  def encoders(self) -> QxEncoderLayers:
    return self._encoders

  @staticmethod
  def get_http_header_server_name():
    return 'Quicly'

  def _dispatch(self, request: QxRequest) -> Any:
    handler, args = self.handlers.match(request.url.path)

    if isinstance(handler, QxHandler):
      if request.method in handler.meta.methods:
        for k, v in args:
          request.args[k] = v
        ret = handler.func(request)
      else:
        ret = QxError(code=QxError.CODE_405_METHOD_NOT_ALLOWED)
    else:
      ret = QxError(code=QxError.CODE_404_NOT_FOUND)

    return ret

  def handle(self, request: QxRequest):
    request = self.decoders.decode(request)

    request.parse_args()

    try:
      result = self._dispatch(request)
    except QxFinish as f:
      result = f
    except QxError as e:
      result = e
    except QxResult as r:
      result = r
    except Exception as e:
      import traceback
      traceback.print_exc()
      result = QxError(data=e)

    if not isinstance(result, QxResult):
      if isinstance(result, Exception):
        result = QxError(data=result)
      else:
        result = QxFinish(data=result)

    try:
      assert isinstance(result, QxResult)
    except AssertionError as e:
      result = QxError(data=e)

    if isinstance(result, QxHttpResult):
      response = QxResponse(
        request=request,
        code=result.status_code,
        body=self.fn_render_template(**result.content) if isinstance(result, QxTemplate) and callable(self.fn_render_template) else result.content,
        headers=result.headers,
        cookies=result.cookies,
      )
      response.headers.setdefault('Content-Type', 'text/html')
    else:
      response = QxResponse(
        request=request,
        body=result.to_dict(),
      )

    response = self.encoders.encode(response)

    response.headers['Server'] = self.get_http_header_server_name()

    return response

################################################################################


class QxServerDecoratorHook(QxDecoratorHook):
  def _check(self, target: Any) -> bool:
    return callable(target) or isinstance(target, (classmethod, staticmethod))

  def _target(self, target: Any) -> Any:
    args = None
    result = None

    if isinstance(target, QxHandlerFunc):
      args = target.args
      result = target.result
      target = target.func
    elif isinstance(target, (classmethod, staticmethod)):
      target = target.__func__

    args = self.arg('args', args)
    result = self.arg('result', result)

    func = QxHandlerFunc(
      func=target,
      args=args,
      result=result,
    )

    path = self.arg([0, 'path'], getattr(target, '__qualname__', None))
    methods = self.arg(['methods', 'method'])

    if isinstance(path, str) and path:
      meta = QxHandlerMeta(
        path=path,
        methods=methods,
      )

      QxServer.get_handlers(self.arg('server')).register(QxHandler(
        func=func,
        meta=meta,
      ))

    return func


QxServerDecorator = QxDecorator(QxServerDecoratorHook)


def FUNC(args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None):
  return QxServerDecorator(args=args, result=result)


def REQUEST(path: str, args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None, methods: Optional[Union[str, List[str], Tuple[str], Set[str]]] = None):
  return QxServerDecorator(path, args=args, result=result, methods=methods)


def RPC(path: str, args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None):
  return REQUEST(path, args, result, _RPC_METHODS)


def HTTP(path: str, args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None):
  return REQUEST(path, args, result, _HTTP_METHODS)


def GET(path: str, args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None):
  return REQUEST(path, args, result, inspect.stack()[0][3])


def PUT(path: str, args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None):
  return REQUEST(path, args, result, inspect.stack()[0][3])


def PATCH(path: str, args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None):
  return REQUEST(path, args, result, inspect.stack()[0][3])


def DELETE(path: str, args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None):
  return REQUEST(path, args, result, inspect.stack()[0][3])


def POST(path: str, args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None):
  return REQUEST(path, args, result, inspect.stack()[0][3])


def HEAD(path: str, args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None):
  return REQUEST(path, args, result, inspect.stack()[0][3])


def OPTIONS(path: str, args: Optional[Dict[str, QxAttr]] = None, result: Optional[QxAttr] = None):
  return REQUEST(path, args, result, inspect.stack()[0][3])


################################################################################
