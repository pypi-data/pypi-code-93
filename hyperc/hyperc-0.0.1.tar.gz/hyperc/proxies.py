from hyperc.actions import BaseAction, ObjectGetattr, ObjectSetattr, ObjectEq, ParamSetattr, ParamGetattr, ParamEq
from hyperc.util import poodle_id, register
from hyperc.pddl import Predicate, Parameter
import wrapt


class HypercProxyClass:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, *args, **kwargs):
        return HypercProxyObject(self.inner(*args, **kwargs), name='proxied')


class HypercProxyParam:
    def __init__(self, wrapped_cls, name='', _id=None):
        self.__wrapped__ = wrapped_cls
        self._self_id = _id
        if not _id:
            self._self_id = poodle_id(id(object()))  # generate new
        self._self_name = name
        self._self_actions = list()
        self._self_attributes = dict()

    def _self_var(self):
        return f'?{self.__wrapped__.__name__}-{self._self_name}-{self._self_id}'

    def __deepcopy__(self, memodict={}):
        return HypercProxyParam(self.__wrapped__, self._self_name)

    def _self_preconditon(self):
        preconditons = list()
        for action in self._self_actions:
            preconditons.extend(action.precondition())
        return preconditons

    def _self_parameters(self):
        params = list()
        for action in self._self_actions:
            params.extend(action.params())
        params.append(Parameter(var=self._self_var(), type=self._self_cls()))
        return params

    def __str__(self):
        return self._self_var()

    def _self_cls(self):
        return self.__wrapped__.__name__

    def __hash__(self):
        return self._self_id

    def __repr__(self):
        return f'{self.__wrapped__.__name__}-{self._self_name}-{self._self_id}'

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            if name not in self.__wrapped__.__annotations__:
                raise Exception(f'__setattr__: {name} is not annotated for class {self.__wrapped__.__name__}')
            if name in self._self_attributes:
                prev = self._self_attributes[name]
            else:
                prev = HypercProxyParam(self.__wrapped__.__annotations__[name], name)
            value = HypercProxyObject(value, name=name) # TODO myact(param1,param2); myatc.param1=param2
            self._self_actions.append(ParamSetattr(self, value, name, prev))
            self._self_attributes[name] = value
        super().__setattr__(name, value)

    def __getattr__(self, name):
        if not name.startswith('_'):
            if name not in self.__wrapped__.__annotations__:
                raise Exception(f'__getattr__: {name} is not annotated for class {self.__wrapped__.__name__}')
            if name in self._self_attributes:
                value = self._self_attributes[name]
            else:
                value = HypercProxyParam(self.__wrapped__.__annotations__[name], name)
            self._self_actions.append(ParamGetattr(self, value, name))
            return value
        return super().__getattribute__(name)

    def __eq__(self, other):
        if isinstance(other, HypercProxyParam):
            raise Exception(f'Variable comparison with variable!: Cant compare {self} and {other}')
        if not hasattr(other, '_self_actions'):
            other = HypercProxyObject(other)
        self._self_actions.append(ParamEq(self, other))  # more sophisticated logic
        return True


class HypercProxyObject(wrapt.ObjectProxy):
    def __init__(self, wrapped, name=''):
        if isinstance(wrapped, HypercProxyObject):  # this may happen because of HypercProxyClass
            wrapped = wrapped.__wrapped__
        assert not isinstance(wrapped, HypercProxyObject)
        self._self_actions = list()
        self._self_name = name
        self._self_id = poodle_id(id(wrapped))
        super().__init__(wrapped)
        register(self)

    def __deepcopy__(self, memodict={}):
        return HypercProxyObject(self.__wrapped__, self._self_name)

    def _self_preconditon(self):
        preconditons = list()
        for action in self._self_actions:
            preconditons.extend(action.precondition())
        return preconditons

    def _self_goal(self):  # Simplest possible
        assert len(self._self_actions) == 1
        action = self._self_actions[0]
        assert isinstance(action, ObjectGetattr)
        return action.goal()

    def _self_parameters(self):
        params = list()
        for action in self._self_actions:
            params.extend(action.params())
        params.append(Parameter(var=self._self_var(), type=self._self_cls()))
        return params

    def _self_obj(self):
        return f'{self.__class__.__name__}-{self._self_id}'

    def __str__(self):
        return self._self_obj()

    def _self_cls(self):
        return self.__class__.__name__

    def _self_var(self):
        return f'?var-{self.__class__.__name__}-{self._self_name}-{self._self_id}'

    def __hash__(self):
        return self._self_id

    def __repr__(self):
        return f'{self.__class__.__name__}-{self._self_name}-{self._self_id}'

    def __call__(self, *args, **kwargs):
        self._self_actions.append(('__call__', args, kwargs))
        return self.__wrapped__(*args, **kwargs)

    def __setattr__(self, name, value):
        if not name.startswith('_self_'):
            prev = getattr(self.__wrapped__, name)
            self._self_actions.append(ObjectSetattr(
                self, HypercProxyObject(value, name),
                name, HypercProxyObject(prev, name)))
            return
        super().__setattr__(name, value)

    def __getattr__(self, name):
        if not name.startswith('_self_'):
            value = HypercProxyObject(getattr(self.__wrapped__, name), name)
            self._self_actions.append(ObjectGetattr(self, value, name))
            return value
        super().__getattr__(name)

    def __eq__(self, other):
        if not hasattr(other, '_self_actions'):
            other = HypercProxyObject(other)
        self._self_actions.append(ObjectEq(self, other))
        return True
