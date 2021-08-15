from . import mlr
from .mlr import Node, NodeList
from typing import Callable, Union, Optional
import inspect

class Transformer:
  def __init__(self, sequenceRule: Optional[Callable[[NodeList], Node]] = None, nodeRules: dict[Node, Callable[[Node], Node]] = {}):
    self._nodeRules = nodeRules
    self._sequenceRule = sequenceRule

  def __call__(self, regex: Union[Node, NodeList, str]):
    if isinstance(regex, Node):
      self.transform_node(regex)
      return regex
    if isinstance(regex, NodeList):
      self.transform_nodes(regex)
      return regex
    if isinstance(regex, str):
      node = mlr.parse(regex)
      self.transform_nodes(node)
      return node.dump()
    raise NotImplementedError()

  def transform_node(self, node: Node):
    rule = self._nodeRules.get(type(node), None)
    if rule is not None:
      rule(node)
      return
    node._traverse(self)

  def transform_nodes(self, nodes: NodeList):
    if self._sequenceRule is not None:
      self._sequenceRule(nodes)
      return
    nodes._traverse(self)

  def add_rule(self, target: type[Union[Node, NodeList]]=None):
    def f(rule):
      nonlocal target
      if target is None:
        spec = inspect.getfullargspec(rule)
        target = spec.annotations[spec.args[0]]
      if issubclass(target, NodeList):
        self._sequenceRule = rule
      elif issubclass(target, Node):
        self._nodeRules[target] = rule
      else:
        raise TypeError()
    return f
