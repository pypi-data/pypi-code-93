import abc
import collections.abc
import inspect
from typing import Optional
import sre_parse as _sre_parse
from . import _sre_dump

class Node(abc.ABC):
  @classmethod
  @property
  @abc.abstractmethod
  def _sre_id(cls) -> str:
    pass

  @abc.abstractmethod
  def _to_sre(self):
    pass

  def _to_sre_tuple(self):
    return (self._sre_id, self._to_sre())

  @classmethod
  @abc.abstractmethod
  def _from_sre(cls, *args, **kwargs):
    pass

  def _traverse(self, handler):
    pass

  def dump(self):
    return _sre_dump.dump([self._to_sre_tuple()])

  def __repr__(self):
    t = self._to_sre()
    if not isinstance(t, tuple):
      t = (t,)
    return f"{type(self).__name__}{t}"


class NodeList:
  _nodes: dict[int, type[Node]] = dict()

  def __init__(self, *nodes: list[Node]):
    self.nodes = nodes

  @abc.abstractmethod
  def _to_sre(self) -> list[tuple]:
    return list(map(lambda node: node._to_sre_tuple(), self.nodes))

  @classmethod
  def _from_sre(cls, ops):
    def decode(c, args):
      factory = cls._nodes[c]._from_sre
      if len(inspect.signature(factory).parameters) == 1:
        return factory(args)
      else:
        return factory(*args)
    return NodeList(*[decode(*op) for op in ops])

  def _traverse(self, handler):
    for child in self.nodes:
      handler(child)

  def dump(self):
    return _sre_dump.dump(self._to_sre())

  @classmethod
  def _register_type(cls, node_type: type[Node]):
    cls._nodes[node_type._sre_id] = node_type
    return node_type

  def __repr__(self):
    return f"[{', '.join(map(repr, self.nodes))}]"


srenode = NodeList._register_type


@srenode
class Literal(Node):
  from sre_constants import LITERAL as _sre_id

  def __init__(self, code: int):
    self.code = code

  @property
  def string(self):
    return chr(self.code)

  @string.setter
  def string(self, x):
    self.code = ord(x)

  def _to_sre(self):
    return self.code

  @classmethod
  def _from_sre(cls, code: int):
    return cls(code)


@srenode
class NotLiteral(Node):
  from sre_constants import NOT_LITERAL as _sre_id

  def __init__(self, code: int):
    self.code = code

  @property
  def string(self):
    return chr(self.code)

  @string.setter
  def string(self, x):
    self.code = ord(x)

  def _to_sre(self):
    return self.code

  @classmethod
  def _from_sre(cls, code: int):
    return cls(code)


@srenode
class In(Node):
  from sre_constants import IN as _sre_id

  def __init__(self, target: NodeList):
    self.target = target

  def _to_sre(self):
    return self.target._to_sre()

  @classmethod
  def _from_sre(cls, ops: list):
    return cls(NodeList._from_sre(ops))

  def _traverse(self, handler):
    self.target._traverse(handler)


@srenode
class Negate(Node):
  from sre_constants import NEGATE as _sre_id

  def __init__(self):
    pass

  def _to_sre(self):
    return None

  @classmethod
  def _from_sre(cls, _=None):
    return cls()


@srenode
class Range(Node):
  from sre_constants import RANGE as _sre_id

  def __init__(self, lo_code: int, hi_code: int):
    self.lo_code = lo_code
    self.hi_code = hi_code

  @property
  def lo_string(self):
    return chr(self.lo_code)

  @property
  def hi_string(self):
    return chr(self.hi_code)

  @lo_string.setter
  def lo_string(self, x):
    self.lo_code = ord(x)

  @hi_string.setter
  def hi_string(self, x):
    self.hi_code = ord(x)

  def _to_sre(self):
    return self.lo_code, self.hi_code

  @classmethod
  def _from_sre(cls, lo_code, hi_code):
    return cls(lo_code, hi_code)


@srenode
class Category(Node):
  from sre_constants import CATEGORY as _sre_id, CHCODES

  _categories = {item.name.lower(): item for item in CHCODES}

  def __init__(self, category: str):
    self.category = category

  def _to_sre(self):
    return self._categories[self.category]

  @classmethod
  def _from_sre(cls, category):
    return cls(category.name.lower())


@srenode
class At(Node):
  from sre_constants import AT as _sre_id, ATCODES

  _positions = {item.name.lower(): item for item in ATCODES}

  def __init__(self, position: str):
    self.position = position

  def _to_sre(self):
    return self._positions[self.position]

  @classmethod
  def _from_sre(cls, position):
    return cls(position.name.lower())


@srenode
class MinRepeat(Node):
  from sre_constants import MIN_REPEAT as _sre_id
  from sre_constants import MAXREPEAT

  def __init__(self, min: Optional[int], max: Optional[int], target: NodeList):
    self.min = min
    self.max = max
    self.target = target

  def _to_sre(self):
    max = self.MAXREPEAT if self.max is None else self.max
    return (self.min, max, self.target._to_sre())

  @classmethod
  def _from_sre(cls, min, max, target):
    max = None if max == cls.MAXREPEAT else max
    return cls(min, max, NodeList._from_sre(target))

  def _traverse(self, handler):
    self.target._traverse(handler)


@srenode
class MaxRepeat(Node):
  from sre_constants import MAX_REPEAT as _sre_id
  from sre_constants import MAXREPEAT

  def __init__(self, min: Optional[int], max: Optional[int], target: NodeList):
    self.min = min
    self.max = max
    self.target = target

  def _to_sre(self):
    max = self.MAXREPEAT if self.max is None else self.max
    return (self.min, max, self.target._to_sre())

  @classmethod
  def _from_sre(cls, min, max, target):
    max = None if max == cls.MAXREPEAT else max
    return cls(min, max, NodeList._from_sre(target))

  def _traverse(self, handler):
    self.target._traverse(handler)


@srenode
class SubPattern(Node):
  from sre_constants import SUBPATTERN as _sre_id

  def __init__(self, gid: int, target: NodeList):
    self.gid = gid
    self.target = target

  def _to_sre(self):
    return (self.gid, 0, 0, self.target._to_sre())

  @classmethod
  def _from_sre(cls, gid, _unk1, _unk2, target):
    return cls(gid, NodeList._from_sre(target))

  def _traverse(self, handler):
    self.target._traverse(handler)


@srenode
class Branch(Node):
  from sre_constants import BRANCH as _sre_id

  def __init__(self, targets: list[NodeList]):
    self.targets = targets

  def _to_sre(self):
    return (None, list(map(NodeList._to_sre, self.targets)))

  @classmethod
  def _from_sre(cls, _unk1, targets):
    return cls(list(map(NodeList._from_sre, targets)))

  def _traverse(self, handler):
    for target in self.targets:
      target._traverse(handler)


@srenode
class Any(Node):
  from sre_constants import ANY as _sre_id

  def __init__(self):
    pass

  def _to_sre(self):
    return None

  @classmethod
  def _from_sre(cls, _unk1):
    return cls()


def parse(pattern):
  return NodeList._from_sre(_sre_parse.parse(pattern))
