import importlib
import json
import logging
import pickle
import sys

try:
    import networkx as nx
    from networkx.readwrite import json_graph

    ISNX = True
except ImportError:
    ISNX = False
from base64 import b64decode, b64encode

try:
    IS_MSGPACK = True
    import msgpack
    import msgpack_numpy as m
    m.patch()
except:
    IS_MSGPACK = False


logger = logging.getLogger("serializer")
# logger.setLevel(logging.INFO)


def set_loglevel(level):
    logger.setLevel(getattr(logging, level.upper()))


set_loglevel("warning")

FIX_JSON_INTAGER_KEYS = True


def _fix_dict_keys(dic):
    """recursively parse a dictionnary to change integers-string keys
    to integers keys

    >>> test = {'1': 'toto', '2': 'tata', 3: {'18': 15.9, 22.3: {'5': 0}}}
    >>> _fix_dict_keys(test)
    {1: 'toto', 2: 'tata', 3: {18: 15.9, 22.3: {5: 0}}}
    """
    if hasattr(dic, "__dict__"):
        dic.__dict__ = _fix_dict_keys(dic.__dict__)
        return dic
    if not isinstance(dic, dict):
        return dic
    ret = {}
    for k, v in dic.items():
        v = _fix_dict_keys(v)
        if isinstance(k, str):
            try:
                k = int(k)
            except:
                pass
        ret[k] = v
    return ret


class _JSONEncode(json.JSONEncoder):
    """encode sets to json"""

    def default(self, obj):
        if isinstance(obj, (list, str, int, float, bool, type(None))):
            return super().default(obj)
        elif hasattr(obj, "to_json"):
            cls = obj.__class__
            try:
                blob = obj.to_json()
            except:
                logger.debug("cannot jsonify %s (%s) (skip)", obj, type(obj))
                return
            logger.debug("catched %s(%s)", cls, obj)
            obj = {
                "__json__": blob,
                "classname": obj.__class__.__name__,
                "module": obj.__module__,
                "class": cls,
            }
            return obj
        return {"_python_object": b64encode(pickle.dumps(obj)).decode("utf-8")}


class Serializer:
    """mixin class handling serialization to json and msgpack

    Intro
    -----


    By default, Serializer handles those extra objects for both formats:

    * ``set``
    * ``frozenset``
    * any object having ``to_msgpack``, ``from_msgpack`` (or ``to_json`` and ``from_json``)
      (deserialization expects the object's class leaving in current namespace)

    Data serialized are found using __getstate__ (defaulted to self.__dict__).
    Overriding ``__getstate__`` and ``__setstate__`` is sometimes need to tweak serialized data

    json and integer keys
    ---------------------

    JSON does not handle integer as keys, and will convert any integer-key
    to string. Serializer is *by default* configured to convert any integer-string
    to integer when resuming from json. This behavior can be triggered by calling
    ``convert_keys_to_int(False)``


    extending Serializer for msgpack serialization
    ----------------------------------------------

    Overriding ``msgpack_encode`` and ``msgpack_decode`` allows to provide a specific encoder/decoder
    for unhandled types.

    extending Serializer for json serialization
    --------------------------------------------

    This is normally not necessary. ``Serializer`` will dump
    any not-handled python structure as pickle object.

    In the eventuality that an object wouldn't be pickable, one would
    need to override ``json_decode``. For encoding, rewriting the nested
    ``_JSONEncode`` class is necessary.

    Example
    -------

    The following example shows how to add serialization for
    a numpy array:

    >>> import numpy as np
    >>> class NumpySerial(Serializer):
    ...     def msgpack_encode(self, obj):
    ...         if isinstance(obj, np.ndarray):
    ...             obj = {'__np__': True, 'as_list': obj.tolist()}
    ...         return obj
    ...
    ...     def msgpack_decode(self, obj):
    ...         if '__np__' in obj:
    ...             obj = np.array(obj["as_list"])
    ...         return obj

    >>> class MyData(NumpySerial):
    ...     def __init__(self):
    ...         self.a = set((1,2))
    ...         self.array = np.array((1,2,3))
    >>> md = MyData()
    >>> md.a |= set((5,6))
    >>> md2 = MyData()
    >>> md2.from_msgpack(md.to_msgpack())
    >>> md2.a
    {1, 2, 5, 6}
    >>> md2.array
    array([1, 2, 3])
    >>> md3 = MyData()
    >>> md3.from_json(md.to_json())
    >>> md3.a
    {1, 2, 5, 6}
    >>> md3.array
    array([1, 2, 3])

    """

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, data):
        self.__dict__ = data

    # ===============================================================================
    # msgpack
    # ===============================================================================

    def _msgpack_encode(self, obj):
        if isinstance(obj, set):
            return {"__set__": True, "as_list": list(obj)}
        if isinstance(obj, frozenset):
            return {"__frozenset__": True, "as_list": list(obj)}
        if isinstance(obj, nx.Graph):
            _json_txt = json.dumps(json_graph.node_link_data(obj), cls=_JSONEncode)
            return {"__NX_Graph__": True, "as_json": _json_txt}
        if hasattr(obj, "to_msgpack"):
            cls = obj.__class__
            try:
                blob = obj.to_msgpack()
            except:
                logger.debug("cannot pack %s (%s) (skip)", obj, type(obj))
                return
            logger.debug("catched %s(%s)", cls, obj)
            return {
                "__blob__": blob,
                "classname": obj.__class__.__name__,
                "module": obj.__module__,
                "class": obj.__class__,
            }
        return self.msgpack_encode(obj)

    def _msgpack_decode(self, obj):
        logger.debug("unserialize %s" % obj)
        if "__set__" in obj:
            return set(obj["as_list"])
        if "__frozenset__" in obj:
            return frozenset(obj["as_list"])
        if "__NX_Graph__" in obj:
            return json_graph.node_link_graph(
                json.loads(obj["as_json"], object_hook=self._json_decode)
            )
        if "__blob__" in obj:
            clstxt = obj["class"]
            _mod = importlib.import_module(obj["module"])
            cls = getattr(_mod, obj["classname"])
            inst = cls.__new__(cls)
            inst.from_msgpack(obj["__blob__"])
            return inst
        return self.msgpack_decode(obj)

    def msgpack_encode(self, obj):
        """ hook to be eventually overriden by the inheriting class"""
        return obj

    def msgpack_decode(self, obj):
        """ hook to be eventually overriden by the inheriting class"""
        return obj

    def from_msgpack(self, data):
        """
        Populate from an msgpack blob
        """
        logger.info("[]-> unpacking %s", self.__class__.__name__)
        logger.debug("[]-> %s: unpacking %s", self.__class__.__name__, data)
        try:
            _data = msgpack.unpackb(data, raw=False, object_hook=self._msgpack_decode)
        except Exception as exc:
            logger.exception(exc)
            raise
        self.__setstate__(_data)
        logger.info("restored %s", self.__class__.__name__)

    def to_msgpack(self):
        """
        dumps a msgpack archive
        """
        data = self.__getstate__()

        logger.info("->[] packing %s", self.__class__.__name__)
        logger.debug("->[] %s: packing %s", self.__class__.__name__, data)
        try:
            pack = msgpack.packb(data, default=self._msgpack_encode, use_bin_type=True)
        except Exception as exc:
            logger.exception(exc)
            logger.critical("%s: cannot serialize \n%s" % (self, data))
            raise
        return pack

    # ===============================================================================
    # json
    # ===============================================================================

    def _json_decode(self, obj):
        if "_python_object" in obj:
            return pickle.loads(b64decode(obj["_python_object"].encode("utf-8")))
        if "__json__" in obj:
            clstxt = obj["class"]
            _mod = importlib.import_module(obj["module"])
            cls = getattr(_mod, obj["classname"])
            inst = cls.__new__(cls)
            inst.from_json(obj["__json__"])
            obj = inst
        return self.json_decode(obj)

    def json_decode(self, obj):
        """ hook to be eventually overriden by the inheriting class"""
        return obj

    def from_json(self, txt):
        """
        Populate from a json file
        """
        data = json.loads(txt, object_hook=self._json_decode)
        if FIX_JSON_INTAGER_KEYS is True:
            data = _fix_dict_keys(data)
        self.__setstate__(data)

    def to_json(self):
        """
        dump to a json string
        """
        return json.dumps(self.__getstate__(), check_circular=True, cls=_JSONEncode)


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS)
