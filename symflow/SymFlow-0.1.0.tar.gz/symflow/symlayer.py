import tensorflow as tf
from sympy import symbols,Eq,lambdify
from sympy.codegen.ast import CodeBlock, Assignment,Return


a,b,c=symbols('a b c')

class SymLayer(tf.keras.layers.Layer):
  """Create a keras layer based on sympy expressions.

  Args:
    exprs: List of sympy expressions that define the operations that need to be performed by the Layer.
    arguments: List of sympy symbols that are required to fulfill the above sympy expressions.
    *args: Arguments passed on to tf.keras.layers.Layer initialization.
    *kwargs: Keyword arguments passed on to tf.keras.layers.Layer initialization.

  Attributes:
    exprs: List of sympy expressions that define the operations that are performed by the Layer.
    args: List of sympy symbols that correspond to the input of the layer's inputs argument in the call method.

  Examples:
    todo
"""
  exprs=[]
  args=[]
  def __init__(self,exprs=[],arguments=[],*args,**kwargs):
    self.exprs+=exprs
    self.args+=arguments
    super().__init__(self,*args,**kwargs)


  def build(self,input_shape,*args,**kwargs):
    super().build(self,*args,**kwargs)
    self._code=CodeBlock(*self.exprs)
    self._code=self.exprs[0]
    self._exec=lambdify(self.args,self._code,"tensorflow")

  def call(self,inputs):
    return self._exec(*inputs)


class AddLayer(SymLayer):
  """ Adds two values """
  #exprs=[Assignment(a,b+c),Return(a)]
  exprs=[b+c]
  args=[b,c]





