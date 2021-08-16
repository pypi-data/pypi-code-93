import pandas
from copy import deepcopy
import warnings
from pandas.io.formats.format import return_docstring
from .exceptions import VariableException

DATETIME_FORMAT = "%d/%m/%Y"

class Variable:

    # initialization

    def __init__(self, name, datetime_index, initializing_value=None):


        datetime_index = pandas.to_datetime(datetime_index.strftime(DATETIME_FORMAT))

        self._value = pandas.DataFrame({
            'value':[initializing_value]*len(datetime_index)
        }, index=datetime_index)

        self._name = name
        self._formula = initializing_value

    # auxiliar methods

    def _index_intersection(self, x):

        return self._value.index.intersection(x.index)

    def _new_1_v(self, frmt):

        new_v_index = self._index_intersection(self.value)

        new_v = Variable(
            frmt.format(self.name),
            new_v_index
        )

        new_v._formula = new_v.name

        return new_v

    def _new_2_v(self, x, frmt):

        new_v_index = self._index_intersection(x.value)

        new_v = Variable(
            frmt.format(self.name, x.name),
            new_v_index
        )

        new_v._formula = new_v.name

        return new_v

    def _define_var(self, x):

        if not isinstance(x, Variable):

            new_v_index = self._index_intersection(self.value)

            new_v = Variable(
                str(x),
                new_v_index
            )

            new_v.value = x

            new_v._formula = new_v.name

            return new_v

        else:

            return x
    # special methods

    def apply_for_each_element(self, func):

        frmt = "{}(".format(func.__qualname__)

        new_v = self._new_1_v(frmt + "{}" + ")")

        new_v.value = [func(self.value.loc[i]['value']) for i in new_v.value.index]

        if isinstance(func, type(lambda: 0)):
            
            new_v._formula = new_v.name

            warnings.warn("The function applied is a lambda. So, the formula is being set to {}. It's better to use a named function.".format(new_v.name))

        return new_v

    def shift(self, periods):

        if periods == 0:

            return self
        
        else:

            periods_frmt = "{})".format(periods if periods < 0 else "+{}".format(periods))

            new_v = self._new_1_v("shift({}, ".format(self.name) + periods_frmt)

            new_v.value = self.value.shift(periods=periods)

            return new_v

    def get_value_by_index(self, datetime_index):

        return self.value.loc[datetime_index.strftime(DATETIME_FORMAT)]['value']

    # dunder methods

    def __divmod__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "(divmod({}, {}))")

        new_v.value['value'] = [divmod(self.value.loc[i]['value'], x.value.loc[i]['value']) for i in new_v.value.index]

        return new_v

    def __invert__(self):

        new_v = self._new_1_v("~({})")

        new_v.value = ~self.value

        return new_v

    def __pos__(self):

        new_v = self._new_1_v("+({})")

        new_v.value = +self.value

        return new_v

    def __add__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} + {})")

        new_v.value = self.value + x.value
        
        return new_v

    def __and__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} & {})")

        new_v.value = self.value & x.value

        return new_v

    def __floordiv__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} // {})")

        new_v.value = self.value // x.value

        return new_v

    def __lshift__(self, x):

        raise VariableException("Not supported.")

    def __matmul__(self, x):

        raise VariableException("Not supported.")

    def __mod__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} % {})")

        new_v.value = self.value % x.value

        return new_v

    def __mul__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} * {})")

        new_v.value = self.value * x.value

        return new_v

    def __or__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} | {})")

        new_v.value = self.value | x.value

        return new_v

    def __pow__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} ** {})")

        x_float = deepcopy(x)

        x_float.value['value'] = [float(i) for i in x.value['value']]
        
        new_v.value = self.value ** x_float.value

        return new_v
    
    def __rshift__(self, x):

        x = self._define_var(x)

        raise VariableException("Not supported.")

    def __sub__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} - {})")

        new_v.value = self.value - x.value

        return new_v

    def __truediv__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} / {})")

        new_v.value = self.value / x.value

        return new_v

    def __xor__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} ^ {})")

        new_v.value = self.value ^ x.value

        return new_v

    def __abs__(self):

        new_v = self._new_1_v("abs({})")

        new_v.value = abs(self.value)

        return new_v

    def __neg__(self):

        new_v = self._new_1_v("-({})")

        new_v.value = -self.value

        return new_v

    def __index__(self):

        raise VariableException("Not supported.")

    def __complex__(self):

        raise VariableException("For this type of function, user '.apply_for_each_element(complex)'")

    def __float__(self):

        raise VariableException("For this type of function, user '.apply_for_each_element(float)'")

    def __int__(self):

        raise VariableException("For this type of function, user '.apply_for_each_element(int)'")

    
    def __floor__(self):

        raise VariableException("For this type of function, user '.apply_for_each_element(math.floor)'")

    def __ceil__(self):

        raise VariableException("For this type of function, user '.apply_for_each_element(math.ceil)'")
    
    def __iadd__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} += {})")

        new_v.value['value'] = self.value['value']

        new_v.value['value'] += x.value['value']

        return new_v

    def __iand__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} &= {})")

        new_v.value['value'] = self.value['value']

        new_v.value['value'] &= x.value['value']

        return new_v

    def __ifloordiv__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} //= {})")

        new_v.value['value'] = self.value['value']

        new_v.value['value'] //= x.value['value']

        return new_v

    def __ilshift__(self, x):

        raise VariableException("Not supported.")

    def __irshift__(self, x):

        raise VariableException("Not supported.")

    def __imatmul__(self, x):

        raise VariableException("Not supported.")

    def __imod__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} %= {})")

        new_v.value['value'] = self.value['value']

        new_v.value['value'] %= x.value['value']

        return new_v

    def __imul__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} *= {})")

        new_v.value['value'] = self.value['value']

        new_v.value['value'] *= x.value['value']

        return new_v

    def __ior__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} |= {})")

        new_v.value['value'] = self.value['value']

        new_v.value['value'] |= x.value['value']

        return new_v

    def __ipow__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} **= {})")

        x_float = deepcopy(x)

        x_float.value['value'] = [float(i) for i in x.value['value']]

        new_v.value['value'] = self.value['value']

        new_v.value['value'] **= x_float.value['value']

        return new_v

    def __isub__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} -= {})")

        new_v.value['value'] = self.value['value']

        new_v.value['value'] -= x.value['value']

        return new_v

    def __itruediv__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} /= {})")

        new_v.value['value'] = self.value['value']

        new_v.value['value'] /= x.value['value']

        return new_v

    def __ixor__(self, x):

        x = self._define_var(x)

        new_v = self._new_2_v(x, "({} ^= {})")

        new_v.value['value'] = self.value['value']

        new_v.value['value'] ^= x.value['value']

        return new_v

    def __round__(self):

         raise VariableException("For this type of function, user '.apply_for_each_element(round)'")

    # properties

    @property
    def name(self):

        return self._name

    @name.setter
    def name(self, new_name):

        self._name = new_name

    @property
    def formula(self):

        return self._formula

    @property
    def datetime_index(self):

        return self.value.index

    @property
    def value(self,):

        return self._value

    @value.setter
    def value(self, x):

        if isinstance(x, pandas.DataFrame):

            if not 'value' in x.columns:

                raise VariableException("Dataframe passed as value doesn't have a 'value' columns.")

            self._value['value'] = x.loc[self._index_intersection(x)]['value']

        else:

            self._value['value'] = x