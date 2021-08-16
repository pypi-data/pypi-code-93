import types
import itertools
from dataclasses import dataclass
import sys, os
import gc
import inspect
import traceback
from collections import defaultdict
import typing
from hyperc.se_decoder import SEDecoder 
import hyperc.mcdc
from hyperc.arithmetic import SumResult, DivResult, MulResult, GreaterThan, GreaterEqualThan
import hyperc.util
import hyperc
from hyperc import settings
from diskcache import Cache
import logging
log = logging.getLogger("hyperc")
progress = logging.getLogger("hyperc_progress")
import hyperc.exceptions
import hyperc.equal_object
from hyperc.util import check_user_disable_execution
import pathlib


_global_eq_cnt = 0


if settings.BROWSER_MODE:  # patch pyodide bug
    sys.modules["__main__"].__name__ = "__main__"


PROXY_STOPLIST = set(['__name__', '__doc__', '__package__', '__loader__', '__spec__', '__file__', '__cached__', 
                        '__builtins__'])

STATIC_PROXIES_NAMES = ['__name__', '__doc__', '__package__', '__loader__', '__spec__', '__file__', '__cached__', 
                        '__builtins__']


class TypeHintLike:
    def __init__(self, hints: dict):
        self.hints = hints
        self.new_hints = {}
    def __getitem__(self, idx):
        if idx in self.new_hints:
            return self.new_hints[idx]
        val = self.hints[idx]
        if type(val) == typing._GenericAlias:
            if val._name == "Set":
                val = set
            else:
                raise TypeError(f"Type {idx} for ? can not be resolved")
        return val
    def __setitem__(self, idx, value):
        self.new_hints[idx] = value
    def items(self):
        hints = {}
        for name, hint in self.hints.items():
            if type(hint) == typing._GenericAlias:
                if hint._name == "Set":
                    hint = set
                else:
                    raise TypeError(f"Type {hint} for {name} can not be resolved")
            hints[name] = hint
        return hints.items()
    def asdict(self):
        return dict(self.items())
    # def asdict_noself(self):
    #     """
    #     This is required as annotations get filled for self of every class method
    #     this triggers symbolic compiler to think that self is a free variable
    #     because realistically although 'self' is annotated for bound methods, there is no such parameter
    #     """
    #     annotations = dict(self.items())
    #     if 'self' in annotations:
    #         del annotations['self']
    #     return annotations
    def __contains__(self, name):
        return name in self.hints or name in self.new_hints

_hints_cache = {}

def get_type_hints(obj):
    # return TypeHintLike(typing.get_type_hints(obj))
    global _hints_cache
    if not obj in _hints_cache:
        _hints_cache[obj] = TypeHintLike(typing.get_type_hints(obj))
    return _hints_cache[obj]
    # hints = {}
    # for name, hint in typing.get_type_hints(obj).items():
    #     if type(hint) == typing._GenericAlias:
    #         if hint._name == "Set":
    #             hint = set
    #         else:
    #             raise TypeError(f"Type {hint} for {name} can not be resolved")
    #     hints[name] = hint
    # return hints
        

def safe_self_id(v):
    if isinstance(v, HCProxy):
        return v._self_id()
    return f"{repr(v)}"


STR_MAP = {}

def str_id(obj):
    global STR_MAP
    if isinstance(obj, str):
        if not obj in STR_MAP:
            STR_MAP[obj] = id(obj)
        return STR_MAP[obj]
    return id(obj)

def empty(*args, **kwargs):
    log.debug(f"Executed empty init which had parameters of {args} kw {kwargs}")
    pass


def set__init__(self, initial=None):
    "Initializer for sets"
    if initial:
        for v in initial:
            self.add(v)


def resolve_proxy(self, obj, name="<immutable>"):
    "Resolve HCProxy object from input parameters"
    if isinstance(obj, HCProxy):
        return obj
    elif isinstance(obj, HCShadowProxy):
        return obj.shadowed
    return HCProxy(wrapped=obj, parent=self, name=name, place_id="__STATIC") 


def resolve_shadow(self, obj, name="<immutable>"):
    if isinstance(obj, HCProxy):
        return obj._hc_shadow_proxy_
    elif isinstance(obj, HCShadowProxy):
        return obj
    return HCProxy(wrapped=obj, parent=self, name=name, place_id="__STATIC")._hc_shadow_proxy_


def _walk_equal(obj, memo=None):
    if memo is None:
        memo = set()
    if id(obj) not in memo:
        memo.add(id(obj)) 
        for key, value in obj._self_equal.items():
            for child in _walk_equal(value, memo):
                yield child
            yield value


def walk_self_equal(obj):
    return list(_walk_equal(obj)) + [obj]



class HCShadowProxy:

    """
            Proxy object main methods example
            _self_class.__qualname__  - we you this field for cross session run (test_if_pass.<locals>.ObjTest )
            _self_class_id() object type in action parameters (ObjTest-15619856) 
            _self_id() local variable name in Action  (?ObjTest-2)
            example: (parameters: ?ObjTest-2 - ObjTest-15619856)
    """
    
    __slots__ = ('shadowed', '_self_parent', '_self_id_counter', '_self_id_position', '_self_fixed_id', 
                 '_self_actions', '_self_call_kwargs', '_self_name', '_self_wrapped', '_self_container',
                 '_self_self', '_self_sealed', '_self_equal', '_self_getattr', '_self_real_value',
                 '_self_class', '_self_setattr_fired', '_self_getattr_cache', '_self_mcdc_vals', 
                 '_self_cached_set_elements', '_self_root', '_self_proxy_globals', '_self_proxy_glo',
                 '_self_instantiated', '_self_instantiated_se', '_self_instantiations', '_self_substitute_class',
                 '_self_substitute_id', '_self_place_id')
    # HCShadowProxy(         self, wrapped, parent, class_, name, external_self, container, real_value)
    def __init__(self, shadowed, wrapped, parent, place_id: str="", class_=None, name='', 
                 external_self=None, container=None, real_value=None, mcdc_vals=None):
        # assert not isinstance(wrapped, HCProxy)
        # assert not isinstance(wrapped, HCShadowProxy)
        # assert not class_ == HCProxy
        # assert not class_ == HCShadowProxy 
        if isinstance(parent, HCProxy):
            parent = parent._hc_shadow_proxy_
        self.shadowed = shadowed
        self._self_parent = parent  # Used for action collecting
        self._self_id_counter = 0
        global _global_eq_cnt
        _global_eq_cnt += 1
        self._self_id_position = _global_eq_cnt  # FIXME: use _self_id_counter instead
        self._self_fixed_id = self._self_get_next_id()
        self._self_actions = list()  # Collects action (only in root proxy) TODO for branching, store nested
        self._self_call_kwargs = {}  # Original keyword arguments list this cation was called with, set externally
        self._self_name = name  # Used for pretty-printing with repr
        if type(wrapped) == str:
            self._self_wrapped = sys.intern(wrapped)  # None -> we're in 'search' mode 
        else:
            self._self_wrapped = wrapped  # None -> we're in 'search' mode 
            if type(wrapped) == int:
                if wrapped < settings.min_int: 
                    settings.min_int = wrapped
                if wrapped > settings.max_int and not settings.HYPERC_FORCE_LIN_COUNT: 
                    settings.max_int = wrapped
        self._self_container = container  # Container of this proxy, used to identify global
        self._self_self = external_self  # for object methods (MethodWrapperType equivalent)
        self._self_sealed = False  # for OAS interface compatibilty (__str__, __getitem__)
        self._self_equal = {}  # What object this object is equal to {eq_id(int): v(HCProxy)}
        self._self_getattr = None  # placeholder for current variable's getattr call, to be able to negate it
        self._self_real_value = real_value  # Used ONLY to generate global :init facts in SED!
        # if wrapped is None and class_ is None:
        #     raise AssertionError("__init__ invocation error")
        if not wrapped is None:  # TODO: protect from overwriting if it is not None
            self._self_class = wrapped.__class__
        if not class_ is None:
            if not wrapped is None: assert wrapped.__class__ == class_
            self._self_class = class_
        self._self_setattr_fired = {}  # Protection from re-accessing object after setattr 
        self._self_getattr_cache = {}  # Protection from re-accessing object after getattr 
        self._self_cached_set_elements = None
        self._self_proxy_globals = defaultdict(dict)  # Globals for every
        self._self_proxy_glo = defaultdict(lambda: None)  # Globals for every
        self._self_instantiated = False  # Check that this object has been instantiated at SAS run time (for LOAD!)
        self._self_instantiated_se = False  # For init optimization
        self._self_instantiations = set()  # All instantiations classes encountered
        self._self_substitute_class = ""  # For retaxonomizaion - substitute class
        self._self_substitute_id = ""  # For retaxonomizaion - substitute object ID 
        self._self_mcdc_vals = mcdc_vals 
        self._self_root = None
        if parent is None: 
            # self._self_mcdc_vals = hyperc.mcdc.McdcVals()  # MCDC related, set externally and not needed here
            self._self_root = self  # Reserved for future optimizations of root discovery
        else: 
            self._self_root = self._self_get_root()
        if not place_id:
            place_id = self._self_root._self_mcdc_vals.get_place_id(name)
        if place_id != "__STATIC":
            self._self_root._self_mcdc_vals.register_map(place_id=place_id, hcp=self)
        self._self_place_id = place_id
    
    def _self_get_root(self):
        if self._self_root: return self._self_root
        if self._self_parent:
            return self._self_parent._self_get_root()
        return self
 
    def _self_repr(self):
        if self._self_wrapped is None and hasattr(self, "_self_class"):
            return f'{self._self_name}({self._self_id()})={self._self_class}({str_id(self._self_wrapped)})'
        elif self._self_wrapped is None and not hasattr(self, "_self_class"):
            return f'{self._self_name}({self._self_id()})=<NO CLASS YET>({str_id(self._self_wrapped)})'
        # return f'{self._self_name}({id(self)})=<search {self._self_class}>'
        # return f'{self._self_name}({id(self)})={self._self_wrapped.__class__}({id(self._self_wrapped)})'
        return f'{self._self_name}({self._self_id()})={self._self_wrapped.__class__}({str_id(self._self_wrapped)})'

    def _self_get_next_id(self):
        if self._self_parent:
            return self._self_parent._self_get_next_id()
        global _global_eq_cnt
        _global_eq_cnt += 1
        self._self_id_counter += 1
        return self._self_id_counter

    def _self_get_root_mcdc(self):
        if self._self_parent:
            return self._self_parent._self_get_root_mcdc()
        return self._self_mcdc_vals

    def self_hash(self):
        try:
            if isinstance(self.wrapped, 'function'):
                return hash(self.wrapped.__code__)
        except:
            raise "self_hash available only for function.  %s is not implemented" % str(self.wrapped)


    def _self_seal(self):
        """
            Disable record move
        """
        self._self_sealed = True

    def _self_add_action(self, op: str, call_stack):
        if op == "op_getattr" and len(call_stack) == 3: 
            log.debug("AAA!!! negated GETATTR {0}".format(call_stack[-1]))
        my_stack = [op, self] + list(call_stack)  # TODO: replace this complex positional structure to dataclasses
        self._self_add_action_parent(my_stack)
        return my_stack

    def _self_add_action_parent(self, call_stack):
        if self._self_parent is None:
            self._self_actions.append(call_stack)
            return
        self._self_parent._self_add_action_parent(call_stack)

    def _self_is_cls_init(self):
        "Return True if we're __init__ of a class"
        if self._self_name == "<initializing>": return True
        if self._self_parent:
            return self._self_parent._self_is_cls_init()
        return False

    def _self_resolve_linked(self):
        "Returns the linked object that this object is equal to, for all __eq__ operations"
        if not self._self_equal: return self
        linked_including_self = [(v._self_fixed_id, v) for v in walk_self_equal(self)]
        lucky_first_variable = min(linked_including_self, key=lambda x: x[0])[1]
        real_objects = list(filter(lambda x: not x[1]._self_wrapped is None, linked_including_self))
        if real_objects:
            return real_objects[-1][1]  # hope that two real objects are equal...
        return lucky_first_variable

    def _self_place_id_linked(self):
        return self._self_resolve_linked()._self_place_id

    def _self_id(self, force_original=False):
        if not force_original and self._self_substitute_id:
            return self._self_substitute_id
        resolved_equals = self._self_resolve_linked()
        self = resolved_equals
        if hasattr(self, "_self_class") and  not hasattr(self._self_class, "__name__"): 
            return f"<Cant't generate ID of class {repr(self._self_class)}>"
        elif not hasattr(self, "_self_class"): 
            return f"<Cant't generate ID of class <NO KNOWN CLASS>"
        if self._self_wrapped is None:
            return f"?{self._self_class.__name__}-{self._self_fixed_id}"
        return f"{self._self_class.__name__}-{str_id(self._self_wrapped)}"
    
    def _self_real_id(self):
        if not self._self_real_value: return ""
        return f"{self._self_class.__name__}-{str_id(self._self_real_value)}"
    
    def _self_get_real_object(self):
        "Returns a real object for :init facts"
        return HCProxy(wrapped=self._self_real_value, name=self._self_name, parent=self._self_parent, 
                container=self._self_container)

    def _self_class_id(self, force_original=False):
        if not force_original and self._self_substitute_class: return self._self_substitute_class # for RTX
        return f"{self._self_class.__name__}-{hyperc.util.py_class_id(self._self_class)}"

    def _self_getattribute(self, name, _system_call=False, _setattr_call=False):
        global _global_eq_cnt
        if _system_call and not _setattr_call:
            place_id = f"{self._self_name}.{name}"  # Means we're call from globals
            me = self
            place_prepend = ""
            while me._self_parent:
                me = me._self_parent
                place_prepend = f"{place_prepend}.{me._self_name}"
            place_id = f"{place_id}.{place_prepend}"
        else:
            place_id = ""  # Continue to default place resolution
        # TODO: if name == "add" and type(self)==type(set()): return self._self_special_set_function
        if settings.DEBUG: log.debug(f"__getattr__({repr(self)}, {name}, _system_call={_system_call})")
        # if name in self._self_getattr_cache and not _system_call: 
        if name in self._self_getattr_cache: 
            if settings.DEBUG: log.debug(f"Getattr returning cached {repr(self._self_getattr_cache[name])} system={_system_call}")
            value = self._self_getattr_cache[name]
            if value._self_getattr or self._self_wrapped is None or self._self_setattr_fired:  # if we're NOT global - don't proceed 
                # FIXME: the whole mess above is becsuse I wanted a "cleaner globbals caching" in _call_ - FIX!
                return value
        else:
            if not self._self_wrapped is None and self._self_class == types.ModuleType:
                # This branch works for global and immutable objects only!
                # TODO This means that we're "hot-proxying" - we're creating a proxy object "on the fly"
                #    - we need to use sort-of "cache" because eventually we will end up having same objects
                #      with different proxies and no ability to optimize
                value = HCProxy(wrapped=None, class_=type(getattr(self._self_wrapped, name)), parent=self, name=name, 
                        container=self, real_value=getattr(self._self_wrapped, name), place_id=place_id)
                value2 = self._self_root._self_mcdc_vals.check_and_replace(value)
                if value is not value2:
                    _global_eq_cnt += 1  # Global eq counter is used to find the first "true" variable name that others are equal to
                    value._self_register_equals(_global_eq_cnt, value2)
                if settings.DEBUG: log.debug("GOT CONTAINER, value is {0}".format(value._self_id()))
            else:
                # Handle special case for object methods in "search mode":
                # TODO: handle case for object methods in normal mode (probably above?)
                if hasattr(self._self_class, name) and isinstance(getattr(self._self_class, name),
                                                                  types.WrapperDescriptorType):
                    if self._self_class == set:
                        def wrapped_set_init(data=None):
                            if not data: return 
                            return set__init__(self, data)  # FIXME: does not actually return anything?
                        value = wrapped_set_init 
                    else:
                        value = empty  # because there is nothing to "init" for user class here
                    _system_call = True
                elif hasattr(self._self_class, name) and isinstance(getattr(self._self_class, name),
                                                                    types.FunctionType):
                    value = HCProxy(wrapped=getattr(self._self_class, name), parent=self, name=name, 
                                    external_self=self.shadowed, container=None, place_id=place_id)
                    _system_call = True
                else:
                    # If we know the object, and know there is no value, don't delete the value
                    my_hints = get_type_hints(self._self_class)
                    if not name in my_hints:
                        raise TypeError(f"{self._self_class} has no annotation for '{name}' and type not resolved \
while compiling # {self._self_get_root()._self_name}. {self}")
                    value = HCProxy(wrapped=None, class_=my_hints[name], parent=self, name=name,
                                    container=None, place_id=place_id)
                    value2 = self._self_root._self_mcdc_vals.check_and_replace(value)
                    if value is not value2:
                        _global_eq_cnt += 1  # Global eq counter is used to find the first "true" variable name that others are equal to
                        value._self_register_equals(_global_eq_cnt, value2)
                    if self._self_container:
                        # We're global variable, do another getattr
                        if settings.DEBUG: log.debug(f"Getattr for global: {self._self_name} {repr(self)}")
                        self._self_container._self_add_action('op_getattr', [self._self_name, self])
        if not _system_call and not value._self_getattr:
            my_getattr = self._self_add_action('op_getattr', (name, value))
            if settings.DEBUG: log.debug("OP GET %s" % my_getattr)
            value._self_getattr = my_getattr  # FIXME: what dow _self_getattr mean? A: needed for negation
        self._self_getattr_cache[name] = value
        if settings.DEBUG: 
            log.debug(f"Getattr returning new {repr(self)}.{name} {repr(self._self_getattr_cache[name])} \
            system={_system_call}")
        return value
    
    def _self_setattr(self, name, value, op="op_setattr"):
        if name.startswith('_self_'):
            return super().__setattr__(name, value)

        if settings.DEBUG: log.debug(f"__setattr__ {repr(self)}.{name} = {repr(value)}")
        if isinstance(value, HCProxy):
            log.debug(f"SETATTR for name {self._self_id()}-{name} v={value._self_id()}")
        if isinstance(value, HCProxy): 
            log.debug("Untested path with HCProxy value")
            value = value._hc_shadow_proxy_
        if isinstance(value, HCShadowProxy) and value._self_container:
            if settings.DEBUG: 
                log.debug(f"__setattr__ w/container, run getattr: {repr(value._self_container)}.{value._self_name}")
            # Do additional getattr from global if we detect that we're setting a global variable
            self_value = value._self_container._self_getattribute(value._self_name, _setattr_call=False)
            # Now link newly extracted global with current value
            # TODO: if the value is a real value - we still should use it!
            global _global_eq_cnt
            _global_eq_cnt += 1
            value._self_register_equals(_global_eq_cnt, self_value)
            _global_eq_cnt += 1
            self_value._self_register_equals(_global_eq_cnt, value)
        # If it is a real object, don't do getattr from anywhere but instead just use its ID
        if not isinstance(value, HCProxy):
            value = resolve_proxy(self, value, name)
            log.debug("FIXME! untested path _setattr_ %s" % value._self_wrapped)  # FIXME: safe repr
        orig_type_hints = get_type_hints(self._self_class)
        if not name in orig_type_hints:
            log.debug(
                f"Inventing a new attribute and remembering type in self={safe_self_id(self)} v={safe_self_id(value)}")
            # TODO: infer full type system if possible
            # Required for new globals, and modified globals - because globals do not have type hints attached
            if self._self_class != types.ModuleType:  # TODO Py does not support type hints on modules!!
                if not hasattr(self._self_class, "__annotations__"):
                    self._self_class.__annotations__ = {}
                self._self_class.__annotations__[name] = value._self_class
            orig_type_hints[name] = value._self_class
            # FIXME: store annotations, check if they are changed for globals -> complain TypeError
        if name in self._self_setattr_fired:
            self._self_setattr_fired[name][0] = "op_none"  # cancel previous setattr as per Gree transform
            del self._self_setattr_fired[name]
            if name in self._self_getattr_cache: del self._self_getattr_cache[name]
        # TODO prev must be filled in with value set by equality operator!
        if self._self_is_cls_init() and self._self_parent._self_class == type:  # In __init__, we don't care about PREVious values (see SED op_setattr)
            if settings.DEBUG: log.debug("Special init optimization kicking in: no prev")
            prev = None
        else:
            try:
                if settings.DEBUG: log.debug("Getting prev ...")
                # !! We don't need a "real" call here as we're going to expand select-delete in setattr... (2 cases)
                prev = self._self_getattribute(name, _system_call=True, _setattr_call=True)  # FIXME: it does not seem like a system call...
                # This branch works for global and immutable objects only!
            except AttributeError:
                if settings.DEBUG: log.debug("... getting prev failed")
                if self._self_wrapped is not None:
                    # If we know the object, and know there is no value, we still MAY get the value ... so invent prev
                    prev = HCProxy(wrapped=None, class_=orig_type_hints[name], parent=self, name=name, container=None)
                    prev = self._self_root._self_mcdc_vals.check_and_replace(prev)
                else:
                    prev = None  # previous value was no value... (looks like only for GOAL insertion)
        if (not settings.HYPERC_STRICT_TYPING and 
            orig_type_hints[name] in (int, bool, str) and value._self_class in (int, bool, str)):
            pass
        elif not (orig_type_hints[name] == value._self_class):
            raise TypeError(f"Type mismatch {orig_type_hints[name].__name__} - {value._self_class.__name__}")

        set_op = self._self_add_action('op_setattr',
                                       (name, value, prev))  # Need to be able to cancel this for Gree transform
        log.debug("OP SET {0}".format(set_op))
        self._self_setattr_fired[name] = set_op
        self._self_getattr_cache[name] = value
        return value  # setattr always returns same value in Py3

    def _self_register_equals(self, cnt, who):
        if self._self_wrapped is not None and who._self_wrapped is not None and self._self_wrapped != who._self_wrapped:
            raise HCAbsurdException("Can not be equal to a different object")
        if cnt in self._self_equal: 
            return
        self._self_equal[cnt] = who
        if who._self_wrapped is not None: cnt = 0  # If we're immutable object, always prefer 
        # log.debug(f"Registering that {self._self_id()} is eq to {who._self_id()}")
        # if cnt in self._self_equal: 
        #     if cnt == 0 and self._self_equal[cnt]._self_wrapped != who._self_wrapped:
        #         log.debug("Found absurd rewrite attempt")
        #         raise HCAbsurdException("Can not be equal to a different object")
        #     return
        self._self_equal[cnt] = who
        for who_eq in self._self_equal.values():
            who_eq._self_register_equals(cnt, who)
    
    def _self_count_getattrs(self, obj_test):
        all_objects_with_getattrs = set()
        for obj in obj_test._self_equal.values():
            if obj._self_getattr and obj._self_fixed_id != obj_test._self_fixed_id:
                all_objects_with_getattrs.add(obj._self_fixed_id)
        return len(all_objects_with_getattrs) 

    def _self_eq(self, other, mcdc_locators=('==','!=')):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy):
            log.debug("FIXME! untested path _eq_ %s" % repr(other))  # FIXME: unsafe repr/str 
            other = HCProxy(wrapped=other, parent=self, name='<immutable>', container=None)  # FIXME: who is this object container?
        log.debug(f"__eq__ {repr(self)} <> {repr(other)}")

        global _global_eq_cnt
        _global_eq_cnt += 1  # Global eq counter is used to find the first "true" variable name that others are equal to

        # TODO: check that objects don't have fixed IDs, if all of them have fixed IDs - emit op_eq
        if id(self) == id(other):  # FIXME: handle this more politely - gibberish, absurd, impossible branch
            brresult = True  # No other branch when we're comparing two same objects
        else:
            brresult = hyperc.mcdc.check_and_expand(self, other, self._self_get_root_mcdc(), locators=mcdc_locators)

        if self._self_class in (int, bool, str) and other._self_class in (int, bool, str):
            pass
        else:
            assert self._self_class == other._self_class, f"Types mismatch: {self._self_class} != {other._self_class}"

        # Cover primitive compares
        if self._self_container is not None: 
            new_self = self._self_container._self_getattribute(self._self_name)  # this must return self
            if isinstance(self, HCShadowProxy):
                assert id(new_self) == id(self.shadowed), f"{repr(self)}<{type(self)}> != {repr(new_self)}<{type(new_self)}>"
            else:
                assert id(new_self) == id(self), f"{repr(self)}<{type(self)}> != {repr(new_self)}<{type(new_self)}>"
        if other._self_container is not None:
            new_other = other._self_container._self_getattribute(other._self_name)  # this must return self
            if isinstance(other, HCShadowProxy):
                assert id(new_other) == id(other.shadowed), f"{repr(other)}<{type(other)}> != {repr(new_other)}<{type(new_other)}>"
            else:
                assert id(new_other) == id(other), f"{repr(other)}<{type(other)}> != {repr(new_other)}<{type(new_other)}>"
        
        link_vals = True
        if brresult:
            pass
        else:
            log.debug("__eq__ negative branch")
            # import traceback
            # traceback.print_stack()
            # if self._self_getattr and not other._self_getattr and (other._self_wrapped is not None or 
            #    self._self_count_getattrs(self) > 0 or mcdc_locators == ("in",)):
            if mcdc_locators == ("in",):
                log.debug(f"__eq__ GA before: {self._self_getattr}")
                if len(self._self_getattr) < 5: self._self_getattr.append(True)  # 5th posarg is negation in op_getattr...
                log.debug(f"__eq__ GA after: {self._self_getattr}")
            elif False and other._self_getattr and not self._self_getattr and (self._self_count_getattrs(other) > 0 or
                    mcdc_locators == ("in",)):
                log.debug(f"__eq__ oGA before: {self._self_getattr}")
                if len(other._self_getattr) < 5: other._self_getattr.append(True)  # 5th posarg is negation in op_getattr...
                log.debug(f"__eq__ oGA after: {self._self_getattr}")
            else:  # Either of attempts to negate failed (probably because we're from global, getattr is rendered after)
                log.debug("WRN negative branch could not resolve objects")
                if other._self_id() == self._self_id():
                    raise HCAbsurdException("Not equal to self")
                # TODO: apply this optimization for globals too
                self._self_add_action('op_neq', (other,))  # TODO: branching optimization here?
                link_vals = False  # FIXME: is this on a correct indentation level???
        if link_vals:
            # We link the variables regardless the comparison result. In case of negation, we just negate the previous gettr
            log.debug(f"Registering equals for {repr(self)}, {repr(other)} with branch {brresult}")
            self._self_register_equals(_global_eq_cnt, other)  # FIXME: order matters???
            _global_eq_cnt += 1  # Global eq counter is used to find the first "true" variable name that others are equal to
            other._self_register_equals(_global_eq_cnt, self)
        return brresult
 
    def _self_call(_hcproxy_self, *args, **kwargs):
        if _hcproxy_self._self_name == "print": return None  # pyodide
        assert not _hcproxy_self._self_wrapped is None, f"__call__ not supported in search mode for \
{_hcproxy_self._self_name} while compiling {_hcproxy_self._self_get_root()._self_name}"
        if (isinstance(_hcproxy_self._self_wrapped, types.FunctionType) 
            or isinstance(_hcproxy_self._self_wrapped, types.MethodType)):
            if _hcproxy_self._self_wrapped == hyperc.side_effect: 
                log.debug("Cancel side-effect")
                return None
            if _hcproxy_self._self_wrapped == hyperc.ensure_ne: 
                _hcproxy_self._self_add_action('op_ensure_neq', (args[0],args[1],))  # TODO: branching optimization here?
                return None
            if _hcproxy_self._self_wrapped == hyperc.hint_exact: 
                _hcproxy_self._self_add_action('op_hint_exact', (args, _hcproxy_self._self_root._self_mcdc_vals.get_place_id()))
                return None
            if _hcproxy_self._self_wrapped == hyperc.not_hasattr: 
                # TODO: this implementation is incorrect! Will only work in `assert` mode
                _hcproxy_self._self_add_action('op_not_hasattr', (args, _hcproxy_self._self_root._self_mcdc_vals.get_place_id()))
                return True 
            # Function, class function, method call
            log.debug(f"Call on {repr(_hcproxy_self)}-{_hcproxy_self._self_wrapped} args {args} kwargs {kwargs}")
            if _hcproxy_self._self_get_root()._self_proxy_globals[id(_hcproxy_self._self_wrapped.__globals__)]:
                glo = _hcproxy_self._self_get_root()._self_proxy_glo[id(_hcproxy_self._self_wrapped.__globals__)]
                proxy_globals = \
                        _hcproxy_self._self_get_root()._self_proxy_globals[id(_hcproxy_self._self_wrapped.__globals__)]
                proxy_globals["_real_globals_dict"] = _hcproxy_self._self_wrapped.__globals__
                proxy_globals["hasattr"] = hyperc.hasattr
                proxy_globals["delattr"] = hyperc.delattr
            else:
                globals_dict = _hcproxy_self._self_wrapped.__globals__
                if settings.BROWSER_MODE and globals_dict["__name__"] == "builtins":  
                    # workaround for pyodide https://github.com/iodide-project/pyodide/issues/629
                    globals_ = sys.modules["__main__"]
                    glo = HCProxy(wrapped=globals_, parent=_hcproxy_self, name="__main__")
                else:
                    if not "__name__" in globals_dict:  # this is probably locals instead
                        globals_ = hyperc.util.ReadonlyLocals(globals_dict)
                        glo = HCProxy(wrapped=globals_, parent=_hcproxy_self, name=f"<locals of '{_hcproxy_self._self_name}'>")
                    else:
                        globals_ = sys.modules[globals_dict["__name__"]]
                        glo = HCProxy(wrapped=globals_, parent=_hcproxy_self, name=globals_dict["__name__"])
                # _hcproxy_self._self_globals = glo  # Store for external manipulation ability (e.g. goal-setting)

                # All global objects will be de-referenced from "global" at SE Decoder
                if settings.BROWSER_MODE:  # pyodide 
                    # proxy_globals = {k: HCProxy(wrapped=None, class_=v.__class__, parent=_hcproxy_self, name=k, 
                                                # container=glo) for k, v in globals_dict.items() if hasattr(v, "__class__")}
                    # proxy_globals = {k: HCProxy(wrapped=None, class_=v.__class__, parent=_hcproxy_self, name=k, 
                    #                 container=glo) for k, v in globals_dict.items() if (not k in PROXY_STOPLIST) and \
                    #                 not isinstance(v, types.FunctionType) and not inspect.isclass(v) and \
                    #                 hasattr(v, "__class__")}
                    proxy_globals = {k: glo._self_getattribute(k, _system_call=True) for k, v in globals_dict.items() 
                                    if (not k in PROXY_STOPLIST) and \
                                    not isinstance(v, types.FunctionType) and not inspect.isclass(v) and \
                                    hasattr(v, "__class__")}
                else:
                    # proxy_globals = {k: HCProxy(wrapped=None, class_=v.__class__, parent=_hcproxy_self, name=k, 
                                    # container=glo) for k, v in globals_dict.items() if (not k in PROXY_STOPLIST) and \
                                    # not isinstance(v, types.FunctionType) and not inspect.isclass(v)}
                    proxy_globals = {k: glo._self_getattribute(k, _system_call=True) for k, v in globals_dict.items() 
                                    if (not k in PROXY_STOPLIST) and \
                                    not isinstance(v, types.FunctionType) and not inspect.isclass(v)}
                proxy_globals.update(STATIC_PROXIES)
                # Functions are immutable, so wrap them
                proxy_globals.update({k: HCProxy(wrapped=v, parent=_hcproxy_self, name=k, container=glo)
                                    for k, v in globals_dict.items() if isinstance(v, types.FunctionType)})
                # Classes are immutable, so wrap them
                proxy_globals.update({k: HCProxy(wrapped=v, parent=_hcproxy_self, name=k, container=glo)
                                    for k, v in globals_dict.items() if inspect.isclass(v)})
                _hcproxy_self._self_get_root()._self_proxy_glo[id(_hcproxy_self._self_wrapped.__globals__)] = glo
                _hcproxy_self._self_get_root()._self_proxy_globals[id(_hcproxy_self._self_wrapped.__globals__)] \
                                = proxy_globals
                proxy_globals["_real_globals_dict"] = globals_dict
                proxy_globals["hasattr"] = hyperc.hasattr
                proxy_globals["delattr"] = hyperc.delattr
            initial_globals_status = proxy_globals.copy()  # Store original glo-module state

            root_f = _hcproxy_self._self_wrapped

            proxy_closure = []
            if root_f.__closure__:
                for vname, orig_cell in zip(root_f.__code__.co_freevars, root_f.__closure__):
                    proxy_cell = hyperc.util.mkcell(HCProxy(wrapped=orig_cell.cell_contents, name=vname, parent=_hcproxy_self))
                    proxy_closure.append(proxy_cell)
            
            # Now find argument defaults in proxy globals, and create proxied defaults
            proxied_defaults = None
            if root_f.__defaults__:
                proxied_defaults = []
                for v in root_f.__defaults__:
                    found = False
                    for kg, vg in root_f.__globals__.items():
                        if vg is v:
                            found = True
                            proxied_defaults.append(glo._self_getattribute(kg))
                    if not found:
                        if isinstance(v, int) or isinstance(v, str) or v is False or v is True or v is None:
                            proxied_defaults.append(v)  # Append literal as-is
                        else:
                            raise NotImplementedError(f"Non-global defaults are not supported: {repr(v)}")
                proxied_defaults = tuple(proxied_defaults)
            if root_f.__kwdefaults__:
                raise NotImplementedError("kw-based defaults are not supported")
            # If something is not found -> raise!

            log.debug(f"Wrapped freevar is {root_f.__code__.co_freevars} closure is {root_f.__closure__}")
            proxied_f = types.FunctionType(
                _hcproxy_self._self_wrapped.__code__,
                proxy_globals,
                name=root_f.__name__,
                argdefs=proxied_defaults,
                closure=tuple(proxy_closure), 
            )
            if isinstance(_hcproxy_self._self_wrapped, types.MethodType):
                self_object = _hcproxy_self._self_wrapped.__self__
                assert not isinstance(self_object, HCShadowProxy)
                if not isinstance(self_object, HCProxy):
                    self_proxy = HCProxy(wrapped=self_object, parent=_hcproxy_self, real_value=self_object, name="self")
                else:
                    self_proxy = self_object  # FIXME not sure this is at all necessary
                # FIXME WARNING! this is a hack and must be thoroughly tested - self is not immutable
                proxied_f = types.MethodType(proxied_f, self_proxy)
            else:
                proxied_f.__annotations__ = root_f.__annotations__  # here we must catch not annotated
            proxied_f.__dict__.update(root_f.__dict__)  # FIXME: rationalize this!
            if not _hcproxy_self._self_self is None:
                args = (_hcproxy_self._self_self,) + args
            # TODO: add branching detection here
            if settings.DEBUG: log.debug("Calling proxy with args %s kwargs %s", args, kwargs)
            fun_ret = proxied_f(*args, **kwargs)
            # Now check newly created globals and for modified globals - because we don't detect __setattr__ on modules 
            for k, v in proxy_globals.items():
                if not k in initial_globals_status:
                    log.debug(f"Found new global '{k}'")
                    if not isinstance(v, HCProxy):
                        v = HCProxy(wrapped=v, name=k, parent=_hcproxy_self)
                    v._self_name = k
                    # v._self_container = glo
                    setattr(glo, k, v)  # FIXME: new global val is erroneously pushed down
                elif id(v) != id(initial_globals_status[k]):
                    if not isinstance(v, HCProxy):
                        v = HCProxy(wrapped=v, name=k, parent=_hcproxy_self)
                    log.debug(f"Found modified global '{k}' type {type(v)}: {v._self_id()}")
                    v._self_name = k
                    v._self_parent = _hcproxy_self
                    # v._self_container = glo
                    # glo2 = HCProxy(wrapped=globals_, parent=_hcproxy_self, name=globals_dict["__name__"])
                    # initial_globals_status[k]._self_container = glo2
                    initial_globals_status[k]._self_container = glo
                    _hcproxy_self._self_add_action("op_none", [k, initial_globals_status[k]])  # store lost original
                    setattr(glo, k, v)  # FIXME: when overwriting, original global is lost
            return fun_ret
        elif isinstance(_hcproxy_self._self_wrapped, type):
            # Class instantiation
            # TODO: create a record that an object has been created (schema and stuff)
            _hcproxy_self._self_get_root()._self_instantiations.add(_hcproxy_self._self_wrapped)
            new_obj = HCProxy(wrapped=None, class_=_hcproxy_self._self_wrapped, name=f"<initializing>",
                              parent=_hcproxy_self, container=None, place_id="__STATIC")  # locals container, deleted after function exits
            new_obj._self_instantiated_se = True
            _hcproxy_self._self_add_action('op_instantiate', call_stack=(new_obj,))
            # TODO: init should call all initializers of original 
            new_obj._hc_shadow_proxy_._self_getattribute("__init__")(*args, **kwargs)
            new_obj._self_name = f"<new '{_hcproxy_self._self_wrapped.__name__}'>"  # Hack for inits without "prev" set branching
            return new_obj
        else:
            # TODO: add support for magic-method-enabled classes!
            raise TypeError(
                "Unsupported __call__ for %s of type %s" % (_hcproxy_self._self_wrapped, type(_hcproxy_self._self_wrapped)))  # TODO

    def add(self, value):
        # Check if add is defined in proxied object
        value = resolve_proxy(self, value)
        if self._self_class != set:
            try:
                add_method = self._self_getattribute("add")
                return add_method(value)
            except AttributeError:
                pass
        assert self._self_class == set, "Only set class is supported"
        if not isinstance(value, HCProxy): value = HCProxy(wrapped=value, parent=self, name='<immutable>') 
        # FIXME: proxy value if it is not proxied
        # assign to a special fact property (set-XXXXX-elements-className ?set-X ?v)
        # TODO: create these facts for init
        # TODO: also add to length?
        self._self_add_action("op_set_add", [value])
        return value
    
    def remove(self, value):
        value = resolve_proxy(self, value)
        if self._self_class != set:
            try:
                add_method = self._self_getattribute("remove")
                return add_method(value)
            except AttributeError:
                pass
        assert self._self_class == set, "Only set class is supported"
        # FIXME: proxy value if it is not proxied
        self._self_add_action("op_set_remove", [value])
    
    def _self_contains(self, value):
        value = resolve_proxy(self, value)
        assert self._self_class == set, f"Only set class is supported, but I have class {self._self_class}"
        # TODO: this must do eq with the imaginary object that we invent here
        if not isinstance(value, HCProxy): value = HCProxy(wrapped=value, parent=self, name='<immutable>') 
        v_name = f"elements-{value._self_class_id()}"
        contained_values = HCProxy(wrapped=None, class_=value._self_class, parent=self, 
                                name=v_name)
        contained_values2 = self._self_root._self_mcdc_vals.check_and_replace(contained_values)
        if contained_values is not contained_values2:
            global _global_eq_cnt
            _global_eq_cnt += 1  # Global eq counter is used to find the first "true" variable name that others are equal to
            contained_values._self_register_equals(_global_eq_cnt, contained_values2)
        self._self_cached_set_elements = contained_values
        contained_values._self_getattr = self._self_add_action("op_getattr", [v_name, contained_values])
        if contained_values._self_sealed:
            assert value._self_sealed
            return str(contained_values) == str(value)
        return contained_values._self_eq(value, mcdc_locators=('in',))

    def _self_getitem(self, idx):
        if self._self_sealed:  # XXX "Has weird behaviour for interface for OAS"
            return self._self_id()[idx]
        if idx == "AssertionError" and (self._self_class == types.ModuleType or self._self_name == "__builtins__"):
            return HCAssertionException("HCAssertionException")  # TODO: figure out why this happens
        elif idx == "print" and (self._self_class == types.ModuleType or self._self_name == "__builtins__"):
            return empty
        elif idx == "set" and (self._self_class == types.ModuleType or self._self_name == "__builtins__"):  # Returning native set class type for instantiation
            return HCProxy(wrapped=set, name="set", parent=self, place_id="__STATIC")
        if self._self_class == types.ModuleType and isinstance(idx, str):
            raise NameError(f"name '{idx}' is not defined")
        if self._self_name == "__builtins__":
            raise NameError("Global name not defined: %s in %s wrapped: %s" % 
                            (repr(idx), repr(self), repr(self._self_wrapped)))
        raise NotImplementedError("Getting item: %s on %s wrapped: %s class: %s" % 
                            (repr(idx), repr(self), repr(self._self_wrapped), repr(self._self_class)))

    def _self_str(self):
        if self._self_sealed:  # XXX "Has weird behaviour for interface for OAS"
            return self._self_id()
        raise NotImplementedError()

    def _self_add(self, other):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy): other = HCProxy(wrapped=other, parent=self, name='<immutable>') 
        if self._self_class in (int, bool, str):
            # Create new variable and select from heap
            sum_op = HCProxy(wrapped=None, class_=SumResult, parent=self, container=None, name=f"<SumResult>")
            result = HCProxy(wrapped=None, class_=int, parent=self, container=None, name="<result of sum>")
            if not sum_op.term1 == self: raise HCAssertionException("HCAssertionException")  # No other branch possible ...
            if not sum_op.term2 == other: raise HCAssertionException("HCAssertionException")  # __eq__ will auto-resolve non-proxied objects
            if not sum_op.summ == result: raise HCAssertionException("HCAssertionException")
            return result
        raise NotImplementedError(f"Calling magic method __add__ is not implemented yet for {self._self_class}")

    def _self_sub(self, other):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy): other = HCProxy(wrapped=other, parent=self, name='<immutable>') 
        if self._self_class in (int, bool, str):
            # Create new variable and select from heap
            sum_op = HCProxy(wrapped=None, class_=SumResult, parent=self, container=None, name=f"<SumResult>")
            result = HCProxy(wrapped=None, class_=int, parent=self, container=None, name="<result of sub>")
            if not sum_op.term1 == result: raise HCAssertionException("HCAssertionException")  # No other branch possible ...
            if not sum_op.term2 == other: raise HCAssertionException("HCAssertionException")
            if not sum_op.summ == self: raise HCAssertionException("HCAssertionException")
            return result
        raise NotImplementedError(f"Calling magic method __sub__ is not implemented yet for {self._self_class}")
 
    def _self_mul(self, other):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy): other = HCProxy(wrapped=other, parent=self, name='<immutable>') 
        if self._self_class in (int, bool, str):
            # Create new variable and select from heap
            sum_op = HCProxy(wrapped=None, class_=MulResult, parent=self, container=None, name=f"<MulResult>")
            result = HCProxy(wrapped=None, class_=int, parent=self, container=None, name="<result of mul>")
            if not sum_op.term1 == self: raise HCAssertionException("HCAssertionException")  # No other branch possible ...
            if not sum_op.term2 == other: raise HCAssertionException("HCAssertionException")
            if not sum_op.mul == result: raise HCAssertionException("HCAssertionException")
            return result
        raise NotImplementedError(f"Calling magic method __mul__ is not implemented yet for {self._self_class}")

    def _self_div(self, other):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy): other = HCProxy(wrapped=other, parent=self, name='<immutable>')
        if self._self_class in (int, bool, str):
            # Create new variable and select from heap
            div_op = HCProxy(wrapped=None, class_=DivResult, parent=self, container=None, name=f"<DivResult>")
            result = HCProxy(wrapped=None, class_=int, parent=self, container=None, name="<result of div>")
            if not div_op.term1 == self: raise HCAssertionException("HCAssertionException")  # No other branch possible ...
            if not div_op.term2 == other: raise HCAssertionException("HCAssertionException")
            if not div_op.div == result: raise HCAssertionException("HCAssertionException")
            return result
        raise NotImplementedError(f"Calling magic method __div__ is not implemented yet for {self._self_class}")

    def _self_gt(self, other, _locators=('>',)):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy): other = HCProxy(wrapped=other, parent=self, name='<immutable>') 
        log.debug("__gt__")
        if self._self_class in (int, bool, str):
            if hyperc.mcdc.check_and_expand(self, other, self._self_get_root_mcdc(), locators=_locators):
                return self._self_igt(other)
            else:
                if not isinstance(other, HCProxy):
                    # Looks like because we already proxied all global objects, we may only receive the immutable here
                    other = HCProxy(wrapped=other, parent=self, name='<immutable>', container=None)
                return not other._self_ige(self)
        raise NotImplementedError(f"Calling magic method __gt__ is not implemented yet for {self._self_class}")

    def _self_ge(self, other, _locators=('>=',)):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy): other = HCProxy(wrapped=other, parent=self, name='<immutable>') 
        log.debug("__ge__")
        if self._self_class in (int, bool, str):
            if hyperc.mcdc.check_and_expand(self, other, self._self_get_root_mcdc(), locators=_locators):
                return self._self_ige(other)
            else:
                if not isinstance(other, HCProxy):
                    other = HCProxy(wrapped=other, parent=self, name='<immutable>', container=None)
                return not other._self_igt(self)
        raise NotImplementedError(f"Calling magic method __ge__ is not implemented yet for {self._self_class}")

    def _self_lt(self, other):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy): other = HCProxy(wrapped=other, parent=self, name='<immutable>') 
        if self._self_class in (int, bool, str):
            if not isinstance(other, HCProxy):
                other = HCProxy(wrapped=other, parent=self, name='<immutable>', container=None)
            return other._self_gt(self, _locators=('<',))
        raise NotImplementedError(f"Calling magic method __lt__ is not implemented yet for {self._self_class}")
    
    def _self_le(self, other):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy): other = HCProxy(wrapped=other, parent=self, name='<immutable>') 
        log.debug("__le__")
        if self._self_class in (int, bool, str):
            if not isinstance(other, HCProxy):
                other = HCProxy(wrapped=other, parent=self, name='<immutable>', container=None)
            return other._self_ge(self, _locators=('<=',))
        raise NotImplementedError(f"Calling magic method __le__ is not implemented yet for {self._self_class}")
    
    def _self_igt(self, other):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy): other = HCProxy(wrapped=other, parent=self, name='<immutable>') 
        cmp_op = HCProxy(wrapped=None, class_=GreaterThan, parent=self, container=None, name=f"<GreaterThan>")
        if not cmp_op.less_val == other or not cmp_op.greater_val == self: 
            raise HCAssertionException("HCAssertionException")
        return True

    def _self_ige(self, other):
        other = resolve_proxy(self, other)
        if not isinstance(other, HCProxy): other = HCProxy(wrapped=other, parent=self, name='<immutable>') 
        cmp_op = HCProxy(wrapped=None, class_=GreaterEqualThan, parent=self, container=None, name=f"<GreaterEqual>")
        if not cmp_op.less_val == other or not cmp_op.greater_val == self: 
            raise HCAssertionException("HCAssertionException")
        return True
    
    def __repr__(self):
        return self._self_repr()


class HCProxy:
    __slots__ = ('_hc_shadow_proxy_')
    def __init__(self, wrapped, parent, place_id="", class_=None, name='', external_self=None, container=None, real_value=None, mcdc_vals=None):
        self._hc_shadow_proxy_ = HCShadowProxy(self, wrapped, parent, place_id, class_, name, external_self, container, real_value, mcdc_vals=mcdc_vals)

    def __call__(_hcproxy_self, *args, **kwargs):
        return _hcproxy_self._hc_shadow_proxy_._self_call(*args, **kwargs)

    def __repr__(self):
        if not hasattr(self, "_hc_shadow_proxy_"):
            return "<UNINITIALIZED PROXY>"
        return self._hc_shadow_proxy_._self_repr()
    
    def self_hash(self):
        return self._hc_shadow_proxy_.self_hash()

    def __getattribute__(self, name):
        if name == "_hc_shadow_proxy_":
            return super().__getattribute__(name)
        if self._hc_shadow_proxy_._self_class == set and (name == "add" or name == "remove"):
            return self._hc_shadow_proxy_.__getattribute__(name)
        if name.startswith('_self') or hasattr(self._hc_shadow_proxy_, name):
            return self._hc_shadow_proxy_.__getattribute__(name)
        return self._hc_shadow_proxy_._self_getattribute(name)

    ###
    # Precondition-generating operations below
    ##

    def __setattr__(self, name, value):
        if name == "_hc_shadow_proxy_":
            return super().__setattr__(name, value)
        return self._hc_shadow_proxy_._self_setattr(name, value)
    
    def __contains__(self, value):
        return self._hc_shadow_proxy_._self_contains(value)

    def __eq__(self, other):
        if self._self_sealed: 
            assert other._self_sealed
            return str(self) == str(other)
            # return super().__eq__(other)
        other = resolve_proxy(self, other)
        return self._self_eq(other)

    def __getitem__(self, idx):
        if hasattr(self._hc_shadow_proxy_._self_wrapped, '__getitem__'):
            return self._hc_shadow_proxy_._self_getattribute('__getitem__')(idx)
        return self._hc_shadow_proxy_._self_getitem(idx)

    def __str__(self):
        return self._hc_shadow_proxy_._self_str()

    def __add__(self, other):
        other = resolve_proxy(self, other)
        return self._hc_shadow_proxy_._self_add(other)
    
    def __sub__(self, other):
        other = resolve_proxy(self, other)
        return self._hc_shadow_proxy_._self_sub(other)

    def __mul__(self, other):
        other = resolve_proxy(self, other)
        return self._hc_shadow_proxy_._self_mul(other)

    def __floordiv__(self, other):
        other = resolve_proxy(self, other)
        return self._hc_shadow_proxy_._self_div(other)

    def __gt__(self, other):
        other = resolve_proxy(self, other)
        return self._hc_shadow_proxy_._self_gt(other)
    
    def __ge__(self, other):
        other = resolve_proxy(self, other)
        return self._hc_shadow_proxy_._self_ge(other)

    def __lt__(self, other):
        other = resolve_proxy(self, other)
        return self._hc_shadow_proxy_._self_lt(other)

    def __le__(self, other):
        other = resolve_proxy(self, other)
        return self._hc_shadow_proxy_._self_le(other)
    
    __rmul__ = __mul__
    __rfloordiv__ = __floordiv__
    __radd__ = __add__
    __rsub__ = __sub__


STATIC_PROXIES = {k: HCProxy(wrapped=None, class_=globals()[k].__class__, parent=None, name=k, place_id="__STATIC") 
                  for k in STATIC_PROXIES_NAMES}


def get_caller_locals():
    import inspect
    f = inspect.stack()[2].frame
    locals_ = dict()
    for k, v in f.f_globals.items():
        if getattr(v, '__module__', None) == f.f_globals['__name__']:
            locals_[k] = v
    return locals_

class HCAssertionException(Exception):
    def __call__(self, txt): # make callable to support assertions with text strings
        pass
    pass


class HCAbsurdException(Exception):
    "Absurd situation"
    pass

# def watch_dog(solver_lock, hyperc_lock):
#     import _thread
#     solver_lock.acquire()
#     if hyperc_lock.locked():
#         _thread.interrupt_main()

import hyperc.equal_object

def solve(goal: types.FunctionType, globals_=None, extra_heap=None, extra_instantiations=None, metadata=None, 
          __ignore_non_annotated=False, __ignore_no_self=False, self_load=False, solver_lock=None, __no_rtx=False, gen_pddl_only=False, work_dir=None, addition_modules=None):
    # if settings.BROWSER_MODE:  # patch the pyodide if needed
    #     caller = inspect.stack()[1][0]
    #     if caller.f_locals['__name__'] == 'builtins':  # impossible
    #         caller.f_locals['__name__'] = '__main__'
    settings.min_int = settings.HYPERC_INT_START
    settings.max_int = settings.HYPERC_INT_START + settings.HYPERC_LIN_COUNT
    
    if metadata is None: metadata = {}
    metadata["stats"] = {
        "evaluations": -1
    }
    if addition_modules is None: addition_modules = []
    if not extra_instantiations: extra_instantiations = []
    gen_invariants = False
    if "GENERATE_INVARIANTS" in metadata:
        gen_invariants = True
    term_list = []
    hash_func_map = {}  # Hashes to functions map
    session_func_copies = {}
    try:
        # if solver_lock is not None:
        #     import threading
        #     hyperc_lock = threading.Lock()
        #     hyperc_lock.acquire()
        #     threading.Thread(target=watch_dog, args=(solver_lock, hyperc_lock,)).start()
        
        global STR_MAP
        STR_MAP = {}
        progress.info("Running garbage collection")
        gc.collect()
        extra_heap = extra_heap or {}
        globals_ = globals_ or get_caller_locals()
        domain_actions = defaultdict(list)
        domain_cache = None
        cached_func_action_dict = {}

        caller = inspect.stack()[1][0]
        class_methods = {}
        if settings.USE_CACHE == "1":
            pathlib.Path(settings.HYPERC_CACHE_DIR).mkdir(parents=True, exist_ok=True)
            domain_cache = Cache(directory=settings.HYPERC_CACHE_DIR, eviction_policy='least-recently-used')


        # print("domain_cache", domain_cache)
        # for f_h in domain_cache:
        #     print(f_h)
            
        progress.info("Doing symbolic execution")

        br_count = 0
        stacks_count = 0

        attrs_init = {}
        all_instantiations = set()  # Set of class instantiations
        for fname, f in itertools.chain(globals_.items(), caller.f_locals.items(), extra_heap.items(), [(goal.__name__, goal)]):
            if solver_lock is not None:
                if not solver_lock.locked():
                    raise hyperc.exceptions.UserInterrupt("user disable execution")
            if isinstance(f, type):
                all_instantiations.add(f)
                if f.__name__ == "Console" and settings.BROWSER_MODE: continue  # pyodide FIXME
                for func_name in dir(f):
                    if hasattr(f, '__side_effect__'):
                        if f.__side_effect__: continue
                    if func_name == "__init__": continue  # Class instantiations are handled separately
                    try:
                        method = getattr(f, func_name)
                    except AttributeError:  # pyodide
                        continue
                    if hasattr(method, '__side_effect__'):
                        if method.__side_effect__: continue
                    if not isinstance(method, types.FunctionType): continue
                    if not "self" in method.__code__.co_varnames: 
                        if __ignore_no_self or settings.BROWSER_MODE: continue
                        raise TypeError(f"Class method without 'self' argument not supported: {method}")
                    if method.__code__.co_argcount > 1 and not method.__annotations__:
                        if __ignore_non_annotated or settings.BROWSER_MODE: 
                            log.debug(f"Ignoring non-annotated method {fname}")
                            continue
                        raise TypeError(f"Method {repr(method)} not annotated, stop.")
                    method.__annotations__["self"] = f
                    class_methods[f"{repr(f)}-{method.__name__}"] = method

        for fname, f in itertools.chain(globals_.copy().items(), caller.f_locals.items(), extra_heap.items(),
                                        class_methods.items(), [(goal.__name__, goal)]):
            branch_replacements_first_run = True
            all_branch_replacements = [([], {})]  # put all replacements here, pull by one
            while all_branch_replacements:
                current_eq_formula, current_replacements = all_branch_replacements.pop()
                if len(set(current_eq_formula)) > 1 and not hyperc.equal_object.is_correct(list(set(current_eq_formula))):
                    continue
                if settings.DEBUG:
                    log.debug(f"Running EQ branch {current_eq_formula}, {current_replacements}")
                # 1. if some same-branch is available, fix the kwargs
                # 2. send the same-branch replacement map to root (what_place -> where_place)
                # 3. in symex, maintain local places/hcproxy map TODO: update the map at each INIT, set _self_place_id_linked()
                # 4. in SYMEX, for every created object, check for replacements before returning it
                if solver_lock is not None:
                    if not solver_lock.locked():
                        raise hyperc.exceptions.UserInterrupt("user disable execution")
                if fname.startswith('_') or fname.startswith('test_') or fname == "print":  # skipping utility stuff for now
                    continue
                if f == solve: continue
                if f == hyperc.side_effect: continue
                if f == hyperc.ensure_ne: continue
                if not isinstance(f, types.FunctionType):
                    log.debug(f"Not a function: {f}, ignoring.")
                    if f == goal:
                        assert isinstance(goal, types.MethodType), "Goal must be either a function or a method"
                        log.debug("WRN! Goal is a class method.")
                    else:
                        continue
                if f.__code__.co_argcount and not f.__annotations__:
                    if __ignore_non_annotated: 
                        log.debug(f"Ignoring non-annotated {fname}")
                        continue
                    raise TypeError(f"Funciton {fname} not annotated, stop.")

                hash_func_map[hyperc.util.h_id(f)] = f
                session_func_copies[f] = 0

                if domain_cache:
                    # print("try load from cache ", f.__qualname__, " type ", type(f))
                    #we don't cache goals and lambda
                    if '<lambda>' not in f.__qualname__:
                    # if (f != goal) and (not ('<lambda>' in f.__qualname__)):
                        try:
                            f_hash = hyperc.util.function_hash(f)
                        except TypeError as e:
                            try:
                                log.warning(f"Bad function for hashing {f} error is {e}")
                            except:
                                log.error(f"Very bad function for hashing {e}")
                            f_hash = None
                        if (f_hash is not None) and (f_hash in domain_cache):  # check that function in cache
                            # print("load from cache ", f.__qualname__)
                            # load action corresponding this function
                            cached_func_action_dict[f_hash] = [domain_cache[f_hash], f]
                            domain_cache.touch(key=f_hash, expire=settings.HYPERC_CACHE_EXPIRE_TIME)
                            continue
                    
                log.debug(f"Compiling {fname} ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                mcdc_vals = hyperc.mcdc.McdcVals()
                mcdc_vals.current_replacements = current_replacements

                type_hints = get_type_hints(f).asdict()
                fun_args = [x for x in inspect.signature(f).parameters.keys()]
                assert (len([x for x in fun_args if x != "self"]) 
                        == len([x for x in type_hints if x != "self"])), f"Function {f} has missing annotations {list(type_hints.keys())}, {fun_args}"
                f_old = None
                if isinstance(f, types.MethodType):
                    f_old = f
                    f = f_old.__func__

                root_f = HCProxy(wrapped=f, parent=None, name=fname, container=None, place_id="root_f", mcdc_vals=mcdc_vals)  # TODO: who is container?
                
                params = {k: HCProxy(wrapped=None, class_=cls_, parent=root_f, name=k, container=None, place_id=f"arg:{k}") \
                        for k, cls_ in type_hints.items()}

                for k, v in params.items():
                    # Now create any replacement that is needed for parameters
                    params[k] = mcdc_vals.check_and_replace(v)

                if f_old: params["self"] = HCProxy(wrapped=f_old.__self__, parent=root_f, name='self', place_id="root_self")
                root_f._self_call_kwargs = params
                try:
                    log.debug(f"Calling {repr(f)} with params {params}")
                    root_f(**params)
                    places_map = mcdc_vals.export_places_maps()
                    for stmt in current_eq_formula:
                        if stmt[0]:
                            comp_op = "op_eq"
                        else:
                            comp_op = "op_neq"
                        if (stmt[1][0] not in mcdc_vals.places2proxies_map 
                            or stmt[1][1] not in mcdc_vals.places2proxies_map):
                            continue  # ignore absent identifiers because branching may go around them
                        root_f._self_actions.append(
                            (
                                comp_op, 
                                mcdc_vals.ids_map[mcdc_vals.places2proxies_map[stmt[1][0]]], 
                                mcdc_vals.ids_map[mcdc_vals.places2proxies_map[stmt[1][1]]]
                            )
                        )
                    domain_actions[f].append((root_f._self_actions, root_f._self_call_kwargs, places_map, current_eq_formula))
                    # for non-first run, append current eq/neq ops
                    stacks_count += 1
                    all_instantiations |= root_f._self_instantiations
                except HCAssertionException as e:
                    pass
                    # log.debug("No initial branch for %s, reason %s" % (fname, traceback.format_exc()))
                except HCAbsurdException:
                    log.debug(f"Dropping absurd branch in {fname}")
                except TypeError as e:  # workaround for pyodide bug?
                    if "exceptions must derive from BaseException" in str(e):
                        pass
                    else:
                        raise e
                # TODO: for every other exception, there is no branch from original code...
                mcdc_it = hyperc.mcdc.gen_mcdc(root_f._self_mcdc_vals.new_eqs)
                try:
                    mcdc_vals.eqs_vals = next(mcdc_it)
                    while mcdc_it:  # if there was branching
                        br_count += 1
                        if br_count % 100 == 0:
                            hyperc.util.check_user_disable_execution(solver_lock)
                            progress.info(f"Symbolic execution `{fname.split('-')[-1][:8]}...`: {stacks_count}/{br_count} ({len(all_branch_replacements)}) branches")
                        log.debug(f"Branch! {mcdc_vals.eqs_vals}")
                        for k, v in mcdc_vals.eqs_vals.items():
                            if "HCAssertionException" in k and v == False:
                                continue

                        mcdc_vals.before() 

                        root_f = HCProxy(wrapped=f, parent=None, name=fname, container=None, place_id="root_f",
                                         mcdc_vals=mcdc_vals)  # TODO: who is container?

                        params = {k: HCProxy(wrapped=None, class_=cls_, parent=root_f, name=k, container=None, place_id=f"arg:{k}") \
                                for k, cls_ in type_hints.items()}

                        for k, v in params.items():
                            # Now create any replacement that is needed for parameters
                            params[k] = mcdc_vals.check_and_replace(v)

                        root_f._self_call_kwargs = params
                        if f_old: params["self"] = HCProxy(wrapped=f_old.__self__, parent=root_f, name='self', place_id="root_self")
                        try:
                            root_f(**params)
                            places_map = mcdc_vals.export_places_maps()
                            for stmt in current_eq_formula:
                                if stmt[0]:
                                    comp_op = "op_eq"
                                else:
                                    comp_op = "op_neq"
                                if (stmt[1][0] not in mcdc_vals.places2proxies_map 
                                    or stmt[1][1] not in mcdc_vals.places2proxies_map):
                                    continue  # ignore absent identifiers because branching may go around them
                                root_f._self_actions.append(
                                    (
                                        comp_op, 
                                        mcdc_vals.ids_map[mcdc_vals.places2proxies_map[stmt[1][0]]], 
                                        mcdc_vals.ids_map[mcdc_vals.places2proxies_map[stmt[1][1]]]
                                    )
                                )
                            domain_actions[f].append((root_f._self_actions, root_f._self_call_kwargs, places_map, current_eq_formula))
                            # for non-first run, append current eq/neq ops
                            stacks_count += 1
                            all_instantiations |= root_f._self_instantiations
                        except HCAssertionException:
                            log.debug("No other branch for %s" % fname)
                        except HCAbsurdException:
                            log.debug(f"Dropping absurd branch in {fname}")
                        except TypeError as e:  # workaround for pyodide bug?
                            if "exceptions must derive from BaseException" in str(e):
                                pass
                            else:
                                raise e
                        # TODO: for every other exception, there is no branch from original code...
                        mcdc_vals.after(mcdc_it)
                except StopIteration:
                    pass
                if not len(domain_actions[f]):
                    log.debug(f"No branches generated for {fname}")
                    if f == goal:
                        raise hyperc.exceptions.SchedulingError("No branches generated for goal")

                # log.debug('\n'.join([repr(x) for x in root_f._self_actions]))
                # generate possible combinations of equal object branches
                if branch_replacements_first_run: 
                    branch_replacements_first_run = False
                    icnt = 0
                    for schema, kwargs, mcdc, eq_formula in domain_actions[f]: 
                        if not settings.IGNORE_EQ_BRANCH:
                            if icnt % 100 == 0: 
                                progress.info(f"Processing EQ replacements for {fname.split('-')[-1][:8]}..({icnt}/{len(domain_actions[f])})")
                            icnt += 1
                            potential_replacements_logix, potential_replacements_maps = hyperc.equal_object.generate_potentially_equal_objects(schema)
                            if len(potential_replacements_logix) == 0:
                                continue
                            # flatten all grouped logic formulas
                            potential_replacements_logix = [hyperc.equal_object.l1_flatten(x) for x in potential_replacements_logix]
                            all_false_logix = list(filter(lambda x: all([not v[0] for v in x]), potential_replacements_logix))
                            assert len(all_false_logix) == 1, f"{all_false_logix}, {potential_replacements_logix}, {potential_replacements_maps}"
                            zipped_logmap = list(zip(potential_replacements_logix, potential_replacements_maps))
                            # logmap now contains:  [([(True,..),(True,...)],{}),([],{}),(...)]
                            # remove all-false branch because it was the one executed first time
                            zip_replacements_only = list(filter(lambda x: any([v[0] for v in x[0]]), zipped_logmap))
                            # now use replacements map to create a position_ids map of same value
                            for formula, merged_replacements_map in zip_replacements_only:
                                places_replacement_map = {mcdc.proxies2places_map[k]: mcdc.proxies2places_map[v] for k,v in merged_replacements_map.items()}
                                places_formula = [(stmt[0], (mcdc.proxies2places_map[stmt[1][0]], mcdc.proxies2places_map[stmt[1][1]])) for stmt in formula]
                                all_branch_replacements.append((places_formula, places_replacement_map))
                        #            for first run, add the generated eq/neq statements (all neq)
                        #            add directly to schema op_eq, op_neq
                        else:  # ignoring all potential EQ values
                            all_false_logix = [[]]
                        for stmt in all_false_logix[0]:
                            # all false, no need to check
                            # print("RWB>>> FIRST RUN", f, ("op_neq", mcdc.ids_map[stmt[1][0]], mcdc.ids_map[stmt[1][1]]))
                            schema.append(("op_neq", mcdc.ids_map[stmt[1][0]], mcdc.ids_map[stmt[1][1]]))  # No replacement needed as all was generated here
                # we cannot append if it is conflicting. Hopefully conflicts are resolved in generate_potentially_equal_objects

        # Now we have collected same-vars here
        
        progress.info("Optimizing novalue code")

        for f in itertools.chain(all_instantiations, extra_instantiations):
            if solver_lock is not None:
                if not solver_lock.locked():
                    raise hyperc.exceptions.UserInterrupt("user disable execution")
            # novalue detection block - check which attributes are guaranteed to receive a value in __init__
            if hasattr(f, "__init__"):
                if settings.DEBUG: 
                    log.debug("Running init inspection for %s", f.__name__)
                    # log.debug("CODE is %s", inspect.getsource(f.__init__))
                init_branches = []
                mcdc_vals = hyperc.mcdc.McdcVals()
                type_hints = get_type_hints(f.__init__).asdict()
                fun_args = [x for x in inspect.signature(f).parameters.keys()]
                has_correct_annotations = (len([x for x in fun_args if (x != "self" and x != "optional")])  # XXX WHAT IS `optional` ???
                        == len([x for x in type_hints if x != "self" and x != "return"]))
                if not __ignore_non_annotated:
                    assert has_correct_annotations, f"Function __init__ {f} has missing annotations {list(type_hints.keys())}, {fun_args}"
                elif not has_correct_annotations:
                    continue
                root_f = HCProxy(wrapped=f.__init__, parent=None, name="__init__", container=None, place_id="__STATIC") 
                params = {k: HCProxy(wrapped=None, class_=cls_, parent=root_f, name=k, container=None, place_id="__STATIC") \
                        for k, cls_ in type_hints.items()}
                params["self"] = HCProxy(wrapped=None, class_=f, parent=root_f, name="self", container=None, place_id="__STATIC")
                root_f._self_mcdc_vals = mcdc_vals
                try:
                    root_f(**params)
                    init_branches.append(root_f._self_actions)
                except (HCAssertionException, HCAbsurdException, TypeError) as e:
                    log.debug("No main branch for init!")
                    pass
                mcdc_it = hyperc.mcdc.gen_mcdc(root_f._self_mcdc_vals.new_eqs)
                try:
                    mcdc_vals.eqs_vals = next(mcdc_it)
                    while mcdc_it:  # if there was branching
                        for k, v in mcdc_vals.eqs_vals.items():
                            if "HCAssertionException" in k and v == False: continue
                        mcdc_vals.before()
                        root_f = HCProxy(wrapped=f, parent=None, name=f.__name__, container=None, place_id="__STATIC")
                        params = {k: HCProxy(wrapped=None, class_=cls_, parent=root_f, name=k, container=None, place_id="__STATIC") \
                                for k, cls_ in type_hints.items()}
                        params["self"] = HCProxy(wrapped=None, class_=f, parent=root_f, name="self", container=None, place_id="__STATIC")
                        root_f._self_mcdc_vals = mcdc_vals
                        try:
                            root_f(**params)
                            init_branches.append(root_f._self_actions)
                        except (HCAssertionException, HCAbsurdException, TypeError) as e:
                            log.debug("No other branch for init!")
                            pass
                        mcdc_vals.after(mcdc_it)
                except StopIteration:
                    pass
                all_setting = []
                for init_br in init_branches:
                    if settings.DEBUG: log.debug("INIT BR IS %s", init_br)
                    setting = set()
                    for op in init_br:
                        if op[0] == "op_setattr":
                            if settings.DEBUG: log.debug("Detected init setattr for %s", op[2])
                            setting.add(op[2])
                    all_setting.append(setting)
                if all_setting: 
                    if settings.DEBUG: log.debug("All values init for %s: %s", f.__name__, all_setting)
                    attrs_init[f] = set.intersection(*all_setting)
            # END novalue detection block 

        
        new_instance_classes = set()  # new classes that we instantiated
        all_classes = set()  # all other classes ever used in any function
        all_predicates = set()
        all_actions = []
        all_global_facts = set()
        all_global_objects = []
        all_set_objects = []
        all_module_names = defaultdict(set)

        log.debug("<<<<<<<<<===========================================>>>>>>>>>>>>>>>>>>>>")
        progress.info("Decoding symbolic execution stack")
        
        i = 0
        cutd = int(stacks_count/20) + 1
        for f, l_root_f in domain_actions.items():
            if solver_lock is not None:
                if not solver_lock.locked():
                    raise hyperc.exceptions.UserInterrupt("user disable execution")

            log.debug("Working with %s hash is %s", f, hash(f.__code__))

            for branch in l_root_f:
                if i % cutd == 0: 
                    progress.info(
                        f"Decoding symbolic execution stack: {len(all_actions)} actions, {int(i*100/stacks_count)}%")
                ssd = SEDecoder(func=f, schema=branch[0], orig_kwargs=branch[1], attrs_init=attrs_init, 
                                session_func_copies=session_func_copies, goal=goal)
                eq_formula = branch[3]
                decoded_actions = ssd.get_actions()
                new_instance_classes |= ssd.get_instantiations_classes()
                all_classes |= ssd.get_all_classes()
                all_predicates |= ssd.get_predicate_declarations()
                all_actions.extend(decoded_actions)
                if len(eq_formula) == 0:  # FIXME: required to protect from registering dirty global facts
                                          #        because same-obj replacements mess up with linking and pollute facts
                    all_global_facts |= ssd.get_global_facts()
                all_global_objects.extend(ssd.global_objects)
                all_set_objects.extend(list(ssd.referenced_set_objects))
                for k, v in ssd.module_names_used.items():
                    all_module_names[k] |= v
                i += 1
            # log.debug([str(x) for x in all_global_facts])
            # log.debug(all_predicates)
            # for act in decoded_actions:
            # log.debug(act)
        # print(all_classes)

        # print("classes")
        # for c in itertools.chain(all_global_objects, all_classes):
        #     print(" type ", type(c), " str ", str(c))#, " path ", c._self_class.__qualname__, c._self_id())

        if not settings.HYPERC_ASE_OFF:
            import hyperc.auto_side_effect as ase
            ase.remove_side_effects(all_actions)

        import hyperc.pddl as pddl
        domain = pddl.Domain(classes=all_classes, predicates=list(all_predicates), actions=all_actions)
        if settings.USE_CACHE == "1":
            domain.dump_to_cache(cache=domain_cache, is_test=True, gg_classes=new_instance_classes)
            domain_cache.close()

        # print(all_predicates)
        # print(all_global_objects)
        # print(all_global_facts)
        # print(all_classes)
        # raise

        some_function_loaded = False
        if settings.USE_CACHE == "1":
            for func_hash in cached_func_action_dict:
                cache = cached_func_action_dict[func_hash][0]
                f = cached_func_action_dict[func_hash][1]
                for a in cache:
                    some_function_loaded = True
                    domain.load_action_from_text(
                        a, global_objects=all_global_objects, initial_globals=globals_, f=f,
                        modules=all_module_names, all_classes=all_classes, gg_classes=new_instance_classes)
        
        if some_function_loaded:
            all_classes.update(new_instance_classes)
            all_classes.update([types.ModuleType, bool, str, int])

        problem = pddl.Problem(classes=all_classes, gg_classes=list(new_instance_classes), attrs_init=attrs_init,
                        predicates=all_predicates, global_facts=all_global_facts, global_objects=all_global_objects,
                        solver_lock=solver_lock, module_names=all_module_names)
        problem.hashes_map.update(hash_func_map)
        progress.info("Loading Python heap into SAS space")
        problem.load_heap()
        # log.debug(str(problem))
        problem.goal = [pddl.Predicate(name='MagicGoal', fact='MagicGoal')]
        progress.info("Filtering and optimizing schema")
        predicate_declaration = set()
        for act in domain.actions:
            for predicate in itertools.chain(act.precondition, act.effect):
                predicate_declaration.add(predicate.get_signature())
        domain.predicates = list(predicate_declaration)
        # TODO fix bug and uncomment
        if not problem.used_classes is None and not problem.novalue_facts is None:
            domain.actions = domain.get_filtered_actions(
                p_novalue_facts=problem.novalue_facts, used_classes=problem.used_classes)
        if not settings.HYPERC_DONT_FILTER_FACTS:
            progress.info("Filtering and optimizing facts")
            problem.filter_facts(set(domain.predicates))  # Filter facts that have no usable predicates in any action

        rtx_runs = metadata.get("rtx_runs", settings.HYPERC_RTX_RUNS)
        if "render_pddl" in metadata:
            metadata["render_pddl"]["domain"] = domain.render(used_classes=problem.used_classes, 
                                                                            novalue_facts=problem.novalue_facts)
            metadata["render_pddl"]["problem"] = str(problem)
            return
        progress.info("Constructing problem domain definition")
        domain.classes.update(problem.classes)
        if gen_invariants or int(hyperc.settings.HYPERC_SPLIT_OFF) == 1:  # WARNING! SPLITTER DISABLED
            dp = pddl.FullDomain(domain=domain, problem=problem, term_list=term_list,
                                 solver_lock=solver_lock, work_dir=work_dir)
            if not __no_rtx and settings.HYPERC_RTX_OFF == "0": dp.retaxonomize(rtx_runs=rtx_runs)
            if gen_invariants:
                return dp.solve(metadata=metadata)
        else:
            import hyperc.pddlSplitter as pddl_splitter
            rdp = pddl.FullDomain(domain=domain, problem=problem, work_dir=work_dir)
            if not __no_rtx and settings.HYPERC_RTX_OFF == "0": rdp.retaxonomize(rtx_runs=rtx_runs)
            splitter = pddl_splitter.ActionSplitter(
                domain=rdp.domain, problem=rdp.problems[0],
                term_list=term_list, solver_lock=solver_lock, work_dir=work_dir)
            progress.info("Splitting action schema interface")
            dp = splitter.split()
        
        dp.metadata = metadata
        if gen_pddl_only:
            return dp.export_pddl()
        else:
            plan = dp.solve(metadata=metadata)

        if settings.DEBUG:
            log.debug("STR_MAP %s" % STR_MAP)

        if metadata is not None:
            metadata["plan"] = plan.plan
            metadata["work_dir"] = dp.work_dir
        progress.info("Executing")
        return plan.execute_plan(metadata)
    # TODO: handle return values from the plan execution
    finally:
        # if hyperc_lock is not None:
        #     try:
        #         hyperc_lock.release()
        #     except:
        #         log.error("hyperc main thread cant release lock")
        import signal
        import platform
        for r_p in term_list:
            try:
                log.info(f"kill pid group {r_p.main_pid}")
                r_p.kill()
            except:
                log.warning('Warning can\'t kill subprocess group')
