# OAS module
import shutil, os, signal
import re
import string
import pydoc
import types
import time
from io import StringIO
import copy
import itertools
import inspect
import sys
from collections import defaultdict
import collections.abc
import hyperc.poc_symex as hc_mod
from hyperc.util import get_object_by_custom_hash, get_work_dir, function_hash, custom_hash, get_class_by_qualname, get_class_by_str, get_class, check_user_disable_execution
from hyperc.solver import start_solve_proc, gen_search_proc, spawn_waiters, translate_only
import hyperc.arithmetic as arithmetic
import subprocess
from os.path import join
from hyperc import settings, sas_collector
import hyperc.text_pddlSplitter
import hyperc.util
import logging
import hashlib
from diskcache import Cache
log = logging.getLogger("hyperc")
progress = logging.getLogger("hyperc_progress")

filt = re.compile("^"+string.ascii_letters+string.digits+"-_:=")
transr = re.compile("([^\\[^\\]^\\s]+)")

def lisp_to_list(v):
    return [eval(",".join(transr.sub(r'"\1"', filt.sub('', v).replace("(", "[").replace(")", "]")).split()))]

# def list_to_lisp(v):
#     if not "(" in repr(v):
#         return repr(v).replace("[", "(").replace("]", ")").replace("'", "").replace(",", "")\
#             .replace("\"", "").replace(" {}", "")  # .replace("((","(").replace("))",")")
#     else:
#         return v


class HCPDDLNameNormalizer:
    def __init__(self):
        self._attr_map = {}
        self._class_map = {}

        self._map2class = {}
        self._map2attr = {}
    
    # def class2map_(self, sc):
    #     if sc in self.class_map:
    #         return self.class_mapp[sc]
    #     clean_name = re.sub(r'-\d+$', "-", sc)
    #     verified_name = clean_name+"0"
    #     i = 1
    #     while verified_name in self.map2class and self.map2class[verified_name] != sc:
    #         verified_name = clean_name + str(i)
    #         i += 1
    #     self.map2class[verified_name] = sc
    #     self.class_map[sc] = verified_name
    #     return verified_name

    def class2map(self, sc):
        return self._any2map(sc, self._class_map, self._map2class, r'-\d+$')

    def attr2map(self, sa):
        return self._any2map(sa, self._attr_map, self._map2attr, r"-\d+-")
    
    def parl2map(self, parl):
        pn, ppos = parl.split(":")
        new_pn = self.attr2map(pn)
        return f"{new_pn}:{ppos}"

    def _any2map(self, sc, dmap, rmap, rx):
        if sc in dmap:
            return dmap[sc]
        clean_name = re.sub(rx, "-", sc)
        verified_name = clean_name+"0"
        i = 1
        while verified_name in rmap and rmap[verified_name] != sc:
            verified_name = clean_name + str(i)
            i += 1
        rmap[verified_name] = sc
        dmap[sc] = verified_name
        return verified_name

    def map2class(self, ma):
        if not ma in self._map2class: return ma
        return self._map2class[ma]

    def map2attr(self, ma):
        return self._map2attr[ma]

    # def attr2map(self, sa):
        # return re.sub(r"-\d+-", "-", sa)



from os import SEEK_END

def readlast(f, sep, fixed=True):
    """Read the last segment from a file-like object.

    :param f: File to read last line from.
    :type  f: file-like object
    :param sep: Segment separator (delimiter).
    :type  sep: bytes, str
    :param fixed: Treat data in ``f`` as a chain of fixed size blocks.
    :type  fixed: bool
    :returns: Last line of file.
    :rtype  : bytes, str
    """
    bs   = len(sep)
    step = bs if fixed else 1
    if not bs:
        raise ValueError("Zero-length separator.")
    try:
        o = f.seek(0, SEEK_END)
        o = f.seek(o-bs-step)    # - Ignore trailing delimiter 'sep'.
        while f.read(bs) != sep: # - Until reaching 'sep': Read data, seek past
            o = f.seek(o-step)   #  read data *and* the data to read next.
    except (OSError,ValueError): # - Beginning of file reached.
        f.seek(0)
    return f.read()


try:
    import ctypes
    class IDPYResolver:
        def __init__(self, hash_map):
            self.obj_hash_map = hash_map
        def id_to_pyobj(self, id_: int):
            if id_ in self.obj_hash_map:
                return self.obj_hash_map[id_]
            return ctypes.cast(id_, ctypes.py_object).value
except ImportError:
    import gc
    class IDPYResolver:
        def __init__(self, hash_map):
            self.obj_hash_map = hash_map
            self.objects = gc.get_objects()
            self.obj_cache = {id(obj): obj for obj in self.objects}
        def id_to_pyobj(self, id_: int):
            if id_ in self.obj_hash_map:
                return self.obj_hash_map[id_]
            return self.obj_cache[id_]

def gen_heap(text_plan, hashes_map):
    s = StringIO(text_plan.lower())
    new_s = []
    id_resolver = IDPYResolver(hashes_map)
    for line in s:
        cont = False
        new_line = []
        if not ('-' in line) or len(line) < 3 or line[0] == ';' or len(line.split()) < 2:
            new_s.append(line)
            continue
        try:
            arr_line = line.replace("(", "").replace(")", "").split()
            # new_line.append(arr_line[0].lower())
            for x in arr_line[1:]:
                if not ('-' in x):
                    continue
                v = id_resolver.id_to_pyobj(int(x.lower().split("-")[-1]))
                new_line.append(v)
        except:
            cont = True
        if cont:
            continue

        new_s.append(new_line)

    return new_s

def get_human_readable_plan(text_plan, hashes_map):
    s = StringIO(text_plan.lower())
    new_s = []
    id_resolver = IDPYResolver(hashes_map)
    for line in s:
        cont = False
        new_line = []
        if not ('-' in line) or len(line) < 3 or line[0] == ';' or len(line.split()) < 2:
            new_s.append(line)
            continue
        try:
            arr_line = line.replace("(", "").replace(")", "").split()
            new_line.append(arr_line[0].lower())
            for x in arr_line[1:]:
                if not ('-' in x):
                    new_line.append(x)
                    continue
                v=[x.lower(), str(id_resolver.id_to_pyobj(int(x.lower().split("-")[-1])))]
                if ' object at ' in v[1]:
                    new_line.append(v[0])
                else:
                    new_line.append(f'{v[0]}({v[1]})')
        except:
            cont = True

        if cont:
            new_s.append(line)
            continue
        else:
            new_s.append(" ".join(new_line))
        

    return "\n".join(new_s)

class TextParameter():
    def __init__(self, self_id, name='', repr=None, qualname=None, module=None, var_name=None, is_instance=False, value=None, type=None, package=None, hash=None):
        self.self_id = self_id
        self.name = name
        self.repr = repr
        self.qualname = qualname
        self.module = module
        self.package = package
        self.var_name = var_name
        self.type = type
        self.is_instance = is_instance
        self.value = value
        self.hash = hash

    def __str__(self):
        return f'{self.self_id}'

class TextPredicate():
    """
    vars - list of _self_id() (Obj-1)

    """

    def __init__(self, fact=None, name=None, vars=None, negated=False, is_novalue_fact=False, element=False):
        self.fact = fact
        self.name = name
        self.is_novalue_fact = is_novalue_fact
        if vars is None:
            self.vars = []
        else:
            self.vars = vars
        self.negated = negated
        self.element = element

    def __str__(self):
        if (self.name):
            fact = self.name
        else:
            fact = self.fact
        space = ""
        if len(self.vars) > 0:
            space = " "
        if self.negated:
            return "(not ({fact}{space}{vars}))".format(fact=fact, space=space, vars=" ".join(map(str, self.vars)))
        else:
            return "({fact}{space}{vars})".format(fact=fact, space=space,vars=" ".join(map(str, self.vars)))

class Predicate():

    def __init__(self, fact=None, name=None, vars=None, negated=False, is_novalue_fact=False, 
                 element=False, comment="", alien=False, is_hasattr=False):
        self.element = element # means double concatenation with class
        self.fact = fact # can be renamed below
        self.name = name
        self.is_hasattr = is_hasattr  # Important novalue predicate from hasattr, don't ignore
        if comment:
            self.comment = f"  ; {comment}"
        else:
            self.comment = ""
        if self.name:
            #simple means that predicate without concatenation
            self.simple = False
        else:
            self.simple = True
        self.negated = negated
        self.is_novalue_fact = is_novalue_fact
        if vars is None:
            self.vars = []
        else:
            try:
                assert alien or (len(vars) == 2) or (len(vars) == 0), "Only triplesand lonely fact are supported "
            except Exception as e:
                raise e
            self.vars = vars
            if (len(vars) == 2) and (self.name ) and (isinstance(self.vars[0], hc_mod.HCProxy) or isinstance(self.vars[0], hc_mod.HCShadowProxy)):
                if self.element:
                    assert len(self.vars) == 2, "element {self.element} wrong"
                    if not (isinstance(self.vars[1], hc_mod.HCProxy) or isinstance(self.vars[1], hc_mod.HCShadowProxy)):
                        raise f"{self.vars[1]} isn't HCProxy or HCShadowProxy"
                    self.fact = f"{self.vars[0]._self_class_id()}-{self.name}-{self.vars[1]._self_class_id()}"
                else:
                    self.fact = f"{self.vars[0]._self_class_id()}-{self.name}"
        if self.fact is not None:
            self.clean_fact = self.fact.replace("-novalue", "")  # FIXME! Better method?
        else:
            self.clean_fact = ""

    def replace_class(self, pos, new_cls):
        assert len(self.vars), "Predicate must have parameters to be reclassified"
        assert type(self.vars[pos]) != str, "Class replacement not yet supported for text-loaded predicates"
        self.vars[pos]._self_substitute_class = new_cls

    def dump_as_text(self):
        vars = []
        for var in self.vars:
            if isinstance(var, hc_mod.HCProxy) or isinstance(var, hc_mod.HCShadowProxy):
                var._self_seal()
                self_id = var._self_id()
                self_class = var._self_class
                if '?' in self_id:
                    if self_class.__name__ in ['set']:
                        raise hyperc.exceptions.NotSupportInstaceType(f"{var._self_class}")
                    parameter = TextParameter(
                        self_id=self_id,
                        qualname=var._self_class.__qualname__, module=var._self_class.__module__,
                        type=self_class.__name__, repr=repr(self_class))
                    vars.append(parameter)
                    continue
                self_wrapped = var._self_wrapped
                if var._self_wrapped is None:
                    var = var._self_resolve_linked()
                # Export simplest literals as is
                if self_class.__name__ in ['float', 'int', 'bool', 'str', 'NoneType']:
                    if self_class.__name__ == 'NoneType':
                        parameter = TextParameter(self_id=self_id,
                                                  is_instance=True, value=var._self_wrapped,
                                                  type=self_class.__name__)
                    else:
                        parameter = TextParameter(self_id=self_id, is_instance=True,
                                                  value=var._self_wrapped, type=self_class.__name__)
                elif self_class.__name__ in ['module']:
                    parameter = TextParameter(self_id=self_id,
                                              is_instance=True, name=var._self_wrapped.__name__,
                                              type=self_class.__name__, hash=custom_hash(
                                                  var._self_wrapped))
                else:
                    raise hyperc.exceptions.NotSupportInstaceType(f"{self_class}")

            vars.append(parameter)

        return TextPredicate(fact=self.fact, name=self.name, vars=vars, is_novalue_fact=self.is_novalue_fact, element=self.element, negated=self.negated)

    # format of line like this "(super_predicat ?var1 ?var2)"
    def load_from_list(self, predicate):
        predicate = self.not_unpack(predicate)
        self.fact = predicate[0]
        self.vars = predicate[1:]

    def get_signature(self):
        if self.fact in ["="]: return EmptyPredicateDeclaration()
        boc = None
        if len(self.vars):
            boc = self.vars[0]
        # Drop selectivity of bool and int to str
        if settings.HYPERC_STRICT_TYPING:
            def dropped_cls_id(class_id):
                return class_id
        else:
            def dropped_cls_id(class_id):
                if class_id in ("int-%s"%hyperc.util.py_class_id(int), "bool-%s"%hyperc.util.py_class_id(bool)):
                    class_id = "str-%s"%hyperc.util.py_class_id(str)
                return class_id

        return PredicateDeclaration(self.fact, [f"?var-{i} - {dropped_cls_id(v._self_class_id())}" 
                        for v,i in zip(self.vars, range(len(self.vars)))], base_obj=boc, 
                        classes=[dropped_cls_id(v._self_class_id()) for v in self.vars], 
                        is_hasattr=self.is_hasattr, for_fact=self.clean_fact)

    def getVars(self):
        vars = []
        for v in self.vars:
            str = v
            if isinstance(v, hc_mod.HCProxy) or isinstance(v, hc_mod.HCShadowProxy):
                str = v._self_id()
            if str[0] == "?":
                vars.append(v)
        return vars

    def containVar(self, var):
        """
        Use this function if you d'like don't care aboute type of var or inner vars
        This function compare variables by its string representation.
        Be carefull this skip constants
        """
        vars = []
        for v in self.vars:
            str = v
            if isinstance(v, hc_mod.HCProxy) or isinstance(v, hc_mod.HCShadowProxy):
                str = v._self_id()
            if str[0] == "?":
                vars.append(str)
        if isinstance(var, hc_mod.HCProxy) or isinstance(var, hc_mod.HCShadowProxy):
            var = var._self_id()
        return var in vars

    def not_unpack(self, predicate):
        if predicate[0] == 'not':
            self.negated = True
            return predicate[1]
        else:
            self.negated = False
            return predicate

    def __str__(self):
        space = ""
        if len(self.vars) > 0:
            space = " "
        if self.negated:
            return "(not ({fact}{space}{vars})){comment}".format(fact=self.fact, space=space, \
                vars=" ".join(
                    [
                        x._self_id() if isinstance(x, hc_mod.HCProxy) or isinstance(x, hc_mod.HCShadowProxy)\
                                     else str(x) for x in self.vars
                    ]), comment=self.comment)
        else:
            return "({fact}{space}{vars}){comment}".format(fact=self.fact, space=space, \
                vars=" ".join([
                    x._self_id() if isinstance(x, hc_mod.HCProxy) or isinstance(x, hc_mod.HCShadowProxy) \
                    else str(x) for x in self.vars]), comment=self.comment)

    def __repr__(self):
        return self.fact

class CustomPredicate(Predicate):
    def __init__(self, full_text, signature=""):
        self.full_text = full_text
        self.signature = CustomPredicateDeclaration(string_decl=signature)
        super().__init__(fact="=", name="hint", vars=[hc_mod.resolve_proxy(None, 1), hc_mod.resolve_proxy(None, 2)])
    
    def dump_as_text(self):
        return self.full_text
    
    def load_from_list(self, predicate):
        raise NotImplementedError()

    def replace_class(self, pos, new_cls):
        return
    
    def get_signature(self):
        return self.signature
    
    def getVars(self):
        return []
    
    def containVar(self, var):
        return False
    
    def __str__(self):
        return self.full_text


class Parameter():
    def __init__(self, var = None, type = None, orig_proxy=None):
        self.type = type
        self.orig_type = type
        self.var = var
        self.orig_proxy = orig_proxy

    def replace_class(self, new_class):
        self.type = new_class

    def get_value(self):
        return self.var

    def __str__(self):
        return "{var} - {type}".format(var=self.var, type=self.type)


class PredicateDeclaration():
    """
    self.vars is list of Parameters
    """
    def __init__(self, fact = None, vars = None, base_obj=None, classes = None, 
                 is_hasattr=False, for_fact=""):
        self.fact = fact
        self.for_fact = for_fact  # For use with is_hasattr
        self.is_hasattr = is_hasattr  # Important declaration for edge case to not ignore hasattr-only attr references
        self.base_obj = base_obj
        self.classes = classes or []
        if vars is None:
            self.vars = []
        else:
            self.vars = vars  # vars is list of Parameters
    
    def replace_class(self, pos, new_class):
        self.classes[pos] = new_class
        self.vars[pos] = self.vars[pos].split("-")[0]+"-"+str(pos) + " - " + new_class
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        space = ""
        if len(self.vars) > 0:
            space = " "
        return "({fact}{space}{vars})".format(fact=self.fact, space=space, vars=" ".join(map(str, self.vars)))

    def __repr__(self):
        return self.fact

class EmptyPredicateDeclaration(PredicateDeclaration):
    def __init__(self, fact=None, vars=None):
        super().__init__(fact=fact, vars=vars)
    
    def __str__(self):
        return ""


class CustomPredicateDeclaration(EmptyPredicateDeclaration):
    def __init__(self, fact=None, vars=None, string_decl=""):
        self.string_decl = string_decl
        super().__init__(fact=fact, vars=vars)

    def __str__(self):
        return self.string_decl


class ObjectDeclaration():

    def __init__(self, type = "object"):
        self.type = type
        self.variables = []

    def extend(self, variables):
        self.variables.extend(variables)
    
    def append(self, variable):
        self.variables.append(variable)

    def __str__(self):
        return "{variables} - {type}".format(variables=" ".join(self.variables), type=self.type)

class TextAction():
    def __init__(self, name, parameters=None, precondition=None, effect=None, cost=1, cost_target=None, idx=-1,
                 parent=None, function_hash=None, kwargs=None, gg_classes=None):
        self.name = name
        self.function_hash = function_hash
        self.kwargs = kwargs or {}
        self.parameters = parameters or {}
        self.parameters = parameters
        if precondition is None:
            self.precondition = []
        else:
            self.precondition = precondition
        if effect is None:
            self.effect = []
        else:
            self.effect = effect
        self.cost = cost
        self.cost_target = cost_target
        self.idx = idx
        self.parent = parent
        self.vars = []
        if gg_classes:
            self.gg_classes = gg_classes
        else:
            self.gg_classes = []

    def __str__(self):
        return """(:action {action_name}
        :parameters ({parameters})
        :precondition ({precondition})
        :effect ({effect})
    )""".format(action_name=f"{self.name}",
                    parameters=' ',
                    precondition='\n            '.join(map(str, self.precondition)),
                    effect='\n            '.join(map(str, self.effect)),

                )

class Action():
    """
    self.parameters is list of Parameter
    self.precondition is list of Predicate
    self.effect is list of Predicate
    self.parent is parent Action (for splitting)
    self.vars is pddl object list loaded from plan
    """
    def __init__(self, name, parameters=None, precondition=None, effect=None, cost=1, cost_target=None, idx=-1, 
                parent = None, copy_parent=None, function=None, kwargs=None, session_func_copies=None):
        self.name = name
        self.session_func_copies = session_func_copies or defaultdict(lambda: 100)
        self.function = function
        """
            In kwargs example
            __qualname__ test_if_pass.<locals>.ObjTest
            _self_class_id() ObjTest-15619856
            _self_id  ?ObjTest-2
        """
        self.kwargs = kwargs or {}
        self.parameters = parameters
        if precondition is None:
            self.precondition = []
        else:
            self.precondition = precondition
        if effect is None:
            self.effect = []
        else:
            self.effect = effect
        self.cost = cost
        self.cost_target = cost_target
        self.idx = idx
        self.parent = parent
        self.arguments = []
        self.vars = []
        self.replacements = {}  # Holds replacements for se_decorder
        # self.replacements_originals = {}  # object: value
        self.copy_num = self.new_copy_num()
        self.copy_parent = copy_parent

    def get_root(self):
        if self.copy_parent is not None:
            return self.copy_parent.get_root()
        return self
    
    def new_copy_num(self):
        self.session_func_copies[self.function] += 1  # WARNING: Thread-unsafe
        return self.session_func_copies[self.function]
    
    def get_copy_id(self):
        return str(self.copy_num).rjust(15, "0")
    
    def __deepcopy__(self, memo):
        # TODO: more deep copy
        new_act = Action(name=self.name, precondition=self.precondition.copy(), effect=self.effect.copy(), 
            function=self.function, kwargs=self.kwargs, session_func_copies=self.session_func_copies, copy_parent=self)
        new_act.copy_num = self.new_copy_num()
        new_act.name = f"{new_act.function.__name__}-{hyperc.util.h_id(new_act.function)}-{new_act.get_copy_id()}"
        if self.vars: new_act.vars = self.vars.copy()
        if self.parameters: new_act.parameters = self.parameters.copy()
        new_act.replacements = self.replacements.copy()
        # new_act.replacements_originals = self.replacements_originals.copy()
        return new_act

    def dump_as_text(self, gg_classes=None):
        precondition = []
        effect = []
        for p in self.precondition:
            precondition.append(p.dump_as_text())
        for e in self.effect:
            effect.append(e.dump_as_text())
        text_gg_classes = []
        if gg_classes:
            for garbage_class in gg_classes:
                text_gg_classes.append(TextParameter(self_id=None,qualname=garbage_class.__qualname__, module=garbage_class.__module__,
                                        type=garbage_class.__name__, repr=repr(garbage_class)))
        parent=None
        if self.parent:
            parent = self.parent.name

        parameters = {}
        for predicate in itertools.chain(self.precondition, self.effect):
            for var in predicate.vars:
                if '?' in var._self_id():
                    if var._self_id() in parameters:
                        continue
                    parameters[var._self_id()] = TextParameter(self_id=var._self_id(),
                                                               qualname=var._self_class.__qualname__, module=var._self_class.__module__, type=var._self_class.__name__)
                # else:
                    
                # print(var._self_id())

        kwargs={}
        for k in self.kwargs:
            log.debug("dump ",self.name, " ","var_name ",k ," ", type(self.kwargs[k]), " " ,self.kwargs[k]._self_id(), " name ", self.kwargs[k]._self_name , " resolve", self.kwargs[k]._self_resolve_linked()._self_id())
            kwargs[self.kwargs[k]._self_id()] = TextParameter(self_id=self.kwargs[k]._self_id(), name=self.kwargs[k]._self_name,
                                                              qualname=self.kwargs[k]._self_class.__qualname__, module=self.kwargs[k]._self_class.__module__, var_name=k)
        
        #   ? ObjTest-2 - ObjTest-40207840
          # _self_id()     _self_class_id()
        return TextAction(name=self.name, precondition=precondition, effect=effect, parent=parent,
                          function_hash=function_hash(self.function),
                          idx=self.idx, kwargs=kwargs, parameters=parameters, gg_classes=text_gg_classes)

    def get_action_signature(self):
        return "".join(
            [str(p) for p in self.precondition] + ["~EFF~"] + [str(e) for e in self.effect]
        )
    
    def grounding_size(self, problem):
        """
        Fill parameters before call
        """
        grounding = 1
        for p in self.parameters:
            grounding *= len(problem.d_objects[p.type])
        return grounding

    def get_classes_stats(self):
        "Return all classes for no-value predicate in this action"
        novalue_facts = set()
        used_classes = set()
        # log.debug(f"Check class stats for {self.name}")
        for p in self.precondition:
            if p.is_novalue_fact:
                novalue_facts.add(p.fact)
                # log.debug(f"No-value class: {self.name} {novalue_facts}")
            for v in p.vars:
                used_classes.add(v._self_class)
        return used_classes, novalue_facts

    def containVar(self, var):
        for p in self.precondition:
            if p.containVar(var):
                return True
        for e in self.effect:
            if e.containVar(var):
                return True
        return False

    def extract_type_by_variable_name(self, var):
        for par in self.parameters:
            if par.var == var:
                return par.type
        return None
    
    def generate_parameters(self):
        assert self.parameters is None, "Prevent double-generation of parameters"
        self.parameters = list()
        par_cache = set()
        for precond in itertools.chain(self.precondition, self.effect):
            for proxy_var in precond.vars:
                v_string = proxy_var._self_id()
                if v_string.startswith("?") and not v_string in par_cache:
                    par_cache.add(v_string)
                    class_id = proxy_var._self_class_id()
                    if (not settings.HYPERC_STRICT_TYPING and 
                        class_id in ("int-%s"%hyperc.util.py_class_id(int), "bool-%s"%hyperc.util.py_class_id(bool))):
                        class_id = "str-%s"%hyperc.util.py_class_id(str)
                    self.parameters.append(Parameter(v_string, class_id, orig_proxy=proxy_var))

    def get_vars(self):
        vars = []
        for precond in itertools.chain(self.precondition, self.effect):
            for var in precond.vars:
                if not var in vars:
                    vars.append(var)
        return vars

    def __str__(self):
        if not self.effect and not settings.HYPERC_DONT_REMOVE_ACTIONS:
            log.debug("WRN! dropping action with no effect: {0}".format(self.name))
            return ""
        if self.parameters is None:
            self.generate_parameters()
        effect_count = len(self.effect)
        #TODO cost is disabled
        self.cost_target = None
        
        if self.cost_target is None:
            cost = ""
        else:
            effect_count += 1
            cost = '\n            (increase ({cost_target}) {cost})'.format( cost_target=self.cost_target, cost=self.cost)
        if effect_count > 0:
            pre_eff = "(and\n            "
            post_eff = "\n        )"
        else:
            pre_eff = ""
            post_eff = ""
        precond_tag = ":precondition"
        if  len(self.precondition) > 1:
            pre_precond = "(and\n            "
            post_precond = "\n        )"
        else:
            pre_precond = ""
            post_precond = ""
        if len(self.precondition) == 0:
            precond_tag = ""
            pre_precond = ""
            post_precond = ""
        return """(:action {action_name}
        :parameters ({parameters})
        {precond_tag} {pre_precond}{precondition}{post_precond}
        :effect {pre_eff}{effect}{cost}{post_eff}
    )""".format(action_name=f"{self.name}",
                        parameters=' '.join(map(str, self.parameters)),
                        precond_tag=precond_tag,
                        precondition='\n            '.join(map(str, self.precondition)),
                        effect='\n            '.join(map(str, self.effect)),
                        cost=cost, pre_eff=pre_eff, post_eff=post_eff,
                        post_precond=post_precond, pre_precond=pre_precond
                       )


class FullDomain():

    def __init__(self, domain=None, problem=None, work_dir=None, term_list=None, solver_lock=None, sas=None):
        """
        domain -- domain object
        problem -- one problem object or list of problem
        """
        self.domain:Domain = domain
        self.work_dir = work_dir
        if isinstance(object, list):
            self.problems = problem
        else:
            self.problems = []
            self.problems.append(problem)
        if term_list is None:
            self.term_list = []
        else:
            self.term_list = term_list
        self.solver_lock = solver_lock
        self.sas = sas
        # Now unmatch the generated garbage for new objects
        # self.inject_unmatch_garbage()  # Not needed... as any object would be selected and garbage guarantees no links
        for p in self.problems:
            self.domain.hashes_map.update(p.hashes_map)
    
    def inject_unmatch_garbage(self):
        "Injects unmatching of garbage in domain"
        # TODO: this may duplicate the predicates!!
        for act in self.domain.actions:
            act.generate_parameters()
            for p in act.parameters:  # TODO: not sure if parameters will always be there already...
                if p.orig_proxy and p.orig_proxy._self_class in self.problems[0].gg_classes:
                    # OK, now we need to check if there is no conflicting predicate...
                    c_predicate = str(Predicate(name="hcsystem-is-free", vars=[p.orig_proxy, hc_mod.resolve_proxy(None, True)]))
                    found = False
                    for pred in act.precondition:
                        if str(pred) == c_predicate:  # Means we actually want that selected here...
                            found = True 
                    if found: continue
                    act.precondition.insert(0, Predicate(name="hcsystem-is-free", vars=[p.orig_proxy, hc_mod.resolve_proxy(None, True)], negated=True))
        
    def get_domain(self):
        return self.domain
    
    def get_problem(self):
        return self.problems

    def add_problem(self, problem):
        """
        problem -- one problem object or list of problem
        """
        if isinstance(object, list):
            self.problems = problem
        else:
            self.problems = []
            self.problems.append(problem)

    def retaxonomize(self, used_classes=None, novalue_facts=None, rtx_runs=1):
        # print("RTX!")
        progress.info("Retaxonomizing")
        factions = self.domain.actions
        # 1. collect all parameters
        pred_params = {}
        predicates_map = {}
        nnr = HCPDDLNameNormalizer()
        gg_classes_ids = set([hc_mod.HCProxy(None, None, class_=v)._self_class_id() for v in self.problems[0].gg_classes])
        str_cls_id = hc_mod.HCProxy("", None, class_=str)._self_class_id()
        int_cls_id = hc_mod.HCProxy(0, None, class_=int)._self_class_id()
        bool_cls_id = hc_mod.HCProxy(True, None, class_=bool)._self_class_id()
        for preddcl in self.domain.predicates:
            if ( len(preddcl.vars) == 2 and 
                # not preddcl.classes[0] in gg_classes_ids and \
                    # not preddcl.classes[1] in gg_classes_ids and \
                        (
                            preddcl.classes[1] == str_cls_id or
                            preddcl.classes[1] == int_cls_id or
                            # preddcl.classes[1] == bool_cls_id or
                            preddcl.classes[0] == str_cls_id or 
                            preddcl.classes[0] == int_cls_id 
                            # preddcl.classes[0] == bool_cls_id
                         )):
                # pred_params[f"{preddcl.fact}:1"] = preddcl.classes[0]  # Not needed for str, int?
                pred_params[f"{preddcl.fact}:2"] = preddcl.classes[1]
                predicates_map[preddcl.fact] = preddcl
        # 2. collect all parameter link pairs
        pgroups = defaultdict(set)
        eq_cnt = 0
        for action in factions:
            for pre in itertools.chain(action.precondition, action.effect):
                if len(pre.vars) == 2 and pre.fact in predicates_map:
                    # if not pre.vars[0]._self_id().startswith("?"):
                        # pgroups[pre.vars[0]._self_id()].add(f"{pre.fact}:1")  # Not needed??? if preference impolemented
                    if pre.vars[1]._self_id().startswith("?"):
                        pgroups[action.name+pre.vars[1]._self_id()].add(f"{pre.fact}:2")
                if pre.fact == "=":
                    # TODO THINK: what happens with constants here?
                    pgroups[action.name+pre.vars[0]._self_id()].add(f"--eq{eq_cnt}:2")
                    pred_params[f"--eq{eq_cnt}:2"] = pre.vars[0]._self_class_id(True)
                    eq_cnt += 1
                    pgroups[action.name+pre.vars[1]._self_id()].add(f"--eq{eq_cnt}:2")
                    pred_params[f"--eq{eq_cnt}:2"] = pre.vars[1]._self_class_id(True)
                    eq_cnt += 1

            # for pre in action.effect:
                # if len(pre.vars) == 2 and pre.fact in predicates_map:
                    ## pgroups[pre.vars[0]._self_id()].add(f"{pre.fact}:1")  # Not needed??? if preference implemented
                    # pgroups[pre.vars[1]._self_id()].add(f"{pre.fact}:2")

        pred_pair_links = set()  # TODO HERE: this must be a SET, also clean up changed pairs!!
        # THINK: how would be automatically optimize this???
        for params in pgroups.values():
            for pair in list(itertools.product(params, repeat=2))[1:]:
                ver1 = (pair + (False,))
                ver2 = (pair[1], pair[0], False)
                if pair[0] == pair[1]: continue
                if not ver1 in pred_pair_links and not ver2 in pred_pair_links:
                    pred_pair_links.add(ver2)
            # pred_pair_links += ([list(v + (False,)) for v in list(itertools.product(params, repeat=2))[1:] if v])
        from . import xtj
        import os
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        xt = xtj.XTJ(open(os.path.join(dir_path, "rtx.xtj")), work_dir=self.work_dir)
        xt["Parameters"] = [["name", "class", "updated"]] + \
            [list((nnr.parl2map(v[0]), nnr.class2map(v[1]), False,)) for v in pred_params.items()]
        # for cls_ in set(pred_params.values()):
        #     xt["Class"].append([cls_, True])
        xt["Parameter_inks"] = [["p1", "p2", "checked"]] + \
            [list((nnr.parl2map(v[0]), nnr.parl2map(v[1]), v[2],)) for v in pred_pair_links]
        xt["GlobalVar"].C2 = len(pred_pair_links)
        # xt["GlobalVar"].B2 = int(xt["GlobalVar"].B2) + len(set(pred_params.values())) 
        # xt["GlobalVar"].A2 = int(xt["GlobalVar"].B2) + 2
        xt["GlobalVar"].A2 = int(xt["GlobalVar"].B2) + 1

        progress.info(f"Retaxonomizing {len(pred_pair_links)} parameter pairs")
        # xt["GlobalVar"].A2 = len(list(xt["Class"])) - 1
        with open("./pre.xtj", "w+") as fd:
            fd.write(xt.asjson())
        # no_var_ids = re.sub(r"-\d+-", "-", xt.asjson())
        # no_class_ids = re.sub(r'-\d+"', "-", no_var_ids)
        # sorted_task = ''.join(sorted(no_class_ids.split()))
        sorted_task = ''.join(sorted(xt.asjson().split()))
        task_hash = hashlib.md5(sorted_task.encode("utf-8")).hexdigest()
        # with open(f"./pre{task_hash}.log", "w+") as fd:
        #     fd.write(sorted_task)
        tf_file = f"TF_{task_hash}.xtj"
        xt_result = None
        try:
            xt_result = xtj.XTJ(open(tf_file))
            xt = xt_result
            progress.info(f"Loaded pre-computed taxonomy with {xt['GlobalVar'].B2} classes")
        except:
            pass

        old_loglevel = progress.level
        progress.setLevel(0)
        i = 0
        for i in range(rtx_runs):
            try:
                ret = xt.solve(solve_params = {"__no_rtx": True, # TODO: retaxonomize retaxonomixer?? than cache result?
                            "metadata": {"SOLVER_MAX_TIME": settings.HYPERC_RTX_TIMEOUT}})  
                with open(tf_file, "w+") as fd:
                    fd.write(xt.asjson())
            except hyperc.exceptions.SchedulingError:
                break
        progress.setLevel(old_loglevel)
        if i == 0 and xt_result is None:
            log.debug("Unable to retaxonomize task")
            progress.info("Unable to retaxonomize task")
            return
        with open("./aft.xtj", "w+") as fd:
            fd.write(xt.asjson())
        # print("New taxonomy is", list(xt["Parameters"]))
        progress.info("Rewriting domain taxonomy")

        # Calculate how many objects are affected by this RTX, disable all-list copying RTX >>>>>
        pred_p1_replacements = {}  # replacements for fact name - class for p1
        pred_p2_replacements = {}  # replacements for fact name - class for p1
        for p_tax in list(xt['Parameters'])[1:]:
            # print(p_tax)
            pred_name, par_pos = p_tax[0].split(":")
            if pred_name.startswith("--eq"): continue
            pred_name = nnr.map2attr(pred_name)
            par_pos = int(par_pos)-1
            p_class = nnr.map2class(p_tax[1])
            orig_pred = predicates_map[pred_name]
            if p_class != orig_pred.classes[par_pos]:
                old_class = orig_pred.classes[par_pos]
                for preddcl in self.domain.predicates:
                    if preddcl.fact == pred_name:
                        if par_pos == 0:
                            pred_p1_replacements[pred_name] = p_class
                        if par_pos == 1:
                            pred_p2_replacements[pred_name] = p_class
        obj_fact_classes = defaultdict(set)
        # # TODO HERE: also scan all predicates in domain too!! for constants
        all_predicates_ever = []
        for a in factions:
            for p in itertools.chain(a.precondition, a.effect):
                all_predicates_ever.append(p)
        for init_fact in itertools.chain(self.problems[0].init, all_predicates_ever):
            if len(init_fact.vars) == 2:
                if  not init_fact.vars[0]._self_id().startswith("?"):
                    if init_fact.fact in pred_p1_replacements:
                        obj_fact_classes[init_fact.vars[0]._self_id()].add(pred_p1_replacements[init_fact.fact])
                    else: 
                        obj_fact_classes[init_fact.vars[0]._self_id()].add(init_fact.vars[0]._self_class_id(True))
                if  not init_fact.vars[1]._self_id().startswith("?"):
                    if init_fact.fact in pred_p2_replacements:
                        obj_fact_classes[init_fact.vars[1]._self_id()].add(pred_p2_replacements[init_fact.fact])
                    else: 
                        obj_fact_classes[init_fact.vars[1]._self_id()].add(init_fact.vars[1]._self_class_id(True))
        ignore_classes = set()
        for obj_id, classes in obj_fact_classes.items():
            if len(classes) > 1:
                for c in classes:
                    ignore_classes.add(c)
        # <<<<<<< END calculate how many objects

        rtx_map = {}
        pred_p1_replacements = {}  # replacements for fact name - class for p1
        pred_p2_replacements = {}  # replacements for fact name - class for p1
        const_preds = [defaultdict(list),defaultdict(list)]
        for p_tax in list(xt['Parameters'])[1:]:
            # print(p_tax)
            pred_name, par_pos = p_tax[0].split(":")
            if pred_name.startswith("--eq"): continue
            pred_name = nnr.map2attr(pred_name)
            par_pos = int(par_pos)-1
            p_class = nnr.map2class(p_tax[1])


            if p_class in ignore_classes: continue
            
            # Find the predicate, find original class
            orig_pred = predicates_map[pred_name]
            if p_class != orig_pred.classes[par_pos]:
                old_class = orig_pred.classes[par_pos]
                rtx_map[f"{pred_name}-{par_pos}-{old_class}"] = p_class
                # The above will be used to re-pack the objects

                # Now, change the classes of ALL predicates
                for act in self.domain.actions:
                    parnames_replaced = set()
                    for p in itertools.chain(act.precondition, act.effect):
                        if p.fact == pred_name:
                            p.replace_class(par_pos, p_class)
                            parnames_replaced.add(p.vars[par_pos]._self_id())
                            if not p.vars[par_pos]._self_id().startswith("?"):
                                const_preds[par_pos][p.vars[par_pos]._self_id()].append(p)
                    
                    if act.parameters is None:
                        act.generate_parameters()
                    for par in act.parameters:
                        if par.type == old_class and par.var in parnames_replaced:
                            par.replace_class(p_class)

                # 1. change in predicate declarations (easy, as they are already text-based only)
                for preddcl in self.domain.predicates:
                    if preddcl.fact == pred_name:
                        preddcl.replace_class(par_pos, p_class)
                        if par_pos == 0:
                            pred_p1_replacements[pred_name] = p_class
                        if par_pos == 1:
                            pred_p2_replacements[pred_name] = p_class

            # 2. Now change in every predicate of every action
            # 2.1 add a replacement attribute for every HCShadowProxy, fill in the replacement attribute
            # 2.2 If class replacement is present - send replacement in class id instead

        # Add new classes from trx map to classes list in domain
        old_objects = None
        new_objects = None
        if not self.domain.types:
            self.domain.types = pddl_types(self.domain.classes)
        for cls_def in self.domain.types:
            if "- object" in cls_def:
                new_objects = ' '.join(list(set(rtx_map.values()))) + ' ' + cls_def
                old_objects = cls_def
        assert new_objects is not None
        self.domain.types.remove(old_objects)
        self.domain.types.append(new_objects)

        # Create facts cache: how many classes does this object have according to (replaced) facts
        obj_fact_classes = defaultdict(set)
        for init_fact in self.problems[0].init:
            if len(init_fact.vars) == 2:
                if init_fact.fact in pred_p1_replacements:
                    obj_fact_classes[init_fact.vars[0]._self_id()].add(pred_p1_replacements[init_fact.fact])
                else: 
                    obj_fact_classes[init_fact.vars[0]._self_id()].add(init_fact.vars[0]._self_class_id(True))
                if init_fact.fact in pred_p2_replacements:
                    obj_fact_classes[init_fact.vars[1]._self_id()].add(pred_p2_replacements[init_fact.fact])
                else: 
                    obj_fact_classes[init_fact.vars[1]._self_id()].add(init_fact.vars[1]._self_class_id(True))
        # Now do the same for all constants
        for const_id, lpars in const_preds[0].items():
            for par in lpars:
                if par.fact in pred_p1_replacements:
                        obj_fact_classes[par.vars[0]._self_id()].add(pred_p1_replacements[par.fact])
        for const_id, lpars in const_preds[1].items():
            for par in lpars:
                if par.fact in pred_p2_replacements:
                        obj_fact_classes[par.vars[1]._self_id()].add(pred_p2_replacements[par.fact])

        # Move objects to new classes
        flat_const_preds = [item for sublist in const_preds[0].values() for item in sublist] + \
                                        [item for sublist in const_preds[1].values() for item in sublist]
        for fact in itertools.chain(self.problems[0].init, flat_const_preds):
            if not fact.fact in predicates_map: continue
            if len(fact.vars) == 2:
                p1_cls = fact.vars[0]._self_class_id(force_original=True)
                p2_cls = fact.vars[1]._self_class_id(force_original=True)
                obj1_classes = obj_fact_classes[fact.vars[0]._self_id()]
                obj2_classes = obj_fact_classes[fact.vars[1]._self_id()]
                rtx1_rec = f"{fact.fact}-0-{p1_cls}"
                rtx2_rec = f"{fact.fact}-1-{p2_cls}"
                if rtx1_rec in rtx_map and fact.fact in pred_p1_replacements:
                    if len(obj1_classes) == 1:  # safe to move object
                        assert next(iter(obj1_classes)) == rtx_map[rtx1_rec]
                        if  fact.vars[0]._self_id() in self.problems[0].d_objects[p1_cls]:
                            self.problems[0].d_objects[p1_cls].remove(fact.vars[0]._self_id())
                            self.problems[0].d_objects[rtx_map[rtx1_rec]].add(fact.vars[0]._self_id())
                    else:  # need to copy
                        old_id = fact.vars[0]._self_id(True)
                        if not old_id.startswith("?"):
                            new_id = f"_RTX_COPY_{rtx_map[rtx1_rec]}_"+fact.vars[0]._self_id()
                            self.problems[0].d_objects[rtx_map[rtx1_rec]].add(new_id)
                            # fact.vars[0]._self_fixed_id = new_id
                            # fact.vars[0] = new_id
                            fact.vars[0]._self_substitute_id = new_id
                            fact.vars[0]._self_substitute_class = rtx_map[rtx1_rec]
                            # Now replace in all domain predicates all constants for these facts
                            # TODOD IF...
                            if old_id in const_preds[0]:
                                for p in const_preds[0][old_id]:
                                    if p.fact == fact.fact:
                                        # p.vars[0] = new_id
                                        p.vars[0]._self_substitute_id = new_id
                                        p.vars[0]._self_substitute_class = rtx_map[rtx1_rec]
                if rtx2_rec in rtx_map and fact.fact in pred_p2_replacements:
                    if len(obj2_classes) == 1:  # safe to move object
                        assert next(iter(obj2_classes)) == rtx_map[rtx2_rec], f"{obj2_classes} != {rtx_map[rtx2_rec]}({p2_cls})"
                        if  fact.vars[1]._self_id() in self.problems[0].d_objects[p2_cls]:
                            self.problems[0].d_objects[p2_cls].remove(fact.vars[1]._self_id())
                            self.problems[0].d_objects[rtx_map[rtx2_rec]].add(fact.vars[1]._self_id())
                    else:  # need to copy
                        old_id = fact.vars[1]._self_id(True)
                        if not old_id.startswith("?"):
                            new_id = f"_RTX_COPY_{rtx_map[rtx2_rec]}_"+old_id
                            self.problems[0].d_objects[rtx_map[rtx2_rec]].add(new_id)
                            # fact.vars[1]._self_fixed_id = new_id
                            # fact.vars[1] = new_id
                            fact.vars[1]._self_substitute_id = new_id
                            fact.vars[1]._self_substitute_class = rtx_map[rtx2_rec]
                            # Now replace in all domain predicates all constants for these facts
                            if old_id in const_preds[1]:
                                for p in const_preds[1][old_id]:
                                    if p.fact == fact.fact:
                                        # p.vars[1] = new_id
                                        p.vars[1]._self_substitute_id = new_id
                                        p.vars[1]._self_substitute_class = rtx_map[rtx2_rec]

            # there are also free-standing objects like new objects garbage
            # they must be excluded from retaxonomization!!! (gg is already excluded)
            # hope that it will not be able to retaxonomize math...

    def export_pddl(self):
        problem = self.problems[0]

        if not hasattr(self, 'work_dir'):
            self.work_dir = get_work_dir()
        elif self.work_dir is None:
            self.work_dir = get_work_dir()
        domain_str = self.domain.render(used_classes=problem.used_classes, novalue_facts=problem.novalue_facts)
        problem_str = str(problem)
        if len(self.domain.cache_stat) > 0:
            f_count = 0
            a_count = 0
            with open(join(self.work_dir, 'cache_stat.txt'), 'w') as file:
                for func in self.domain.cache_stat:
                    f_count += 1
                    file.write(f'function {func}:\n')
                    file.write('\taction:\n')
                    for a in self.domain.cache_stat[func]:
                        a_count += 1
                        file.write(f'\t{a}\n')
                file.write(f'total:\nfunctions - {f_count}\nactions - {a_count}\n')

        with open(join(self.work_dir, 'domain.pddl'), 'w') as f:
            f.write(domain_str)

        with open(join(self.work_dir, 'problem.pddl'), 'w') as f:
            f.write(problem_str)

        return domain_str, problem_str

    def solve(self, metadata=None):
        problem = self.problems[0]
        max_time = settings.SOLVER_MAX_TIME
        gen_invariants = False
        if metadata:
            if "SOLVER_MAX_TIME" in metadata:
                max_time = metadata["SOLVER_MAX_TIME"]
            if "GENERATE_INVARIANTS" in metadata:
                gen_invariants = True

        if not hasattr(self, 'work_dir'):
            self.work_dir = get_work_dir()
        elif self.work_dir is None:
            self.work_dir = get_work_dir()
        domainpth = join(self.work_dir, 'domain.pddl')
        domain_str = self.domain.render(used_classes=problem.used_classes, novalue_facts=problem.novalue_facts)
        problem_str = str(problem)
        old_split = False
        progress.info("Splitting action schema")
        if settings.HYPERC_OLD_SPLITTER == 1 and not "poodle-split-math-not-in-progress" in domain_str:
            with open(join(self.work_dir, 'problem_orig.pddl'), 'w') as f:
                f.write(problem_str)
            with open(join(self.work_dir, 'domain_orig.pddl'), 'w') as f:
                f.write(domain_str)
            import hyperc.text_pddlSplitter  # ?? python bug?
            asplitter = hyperc.text_pddlSplitter.ActionSplitter(domain=domain_str, problem=problem_str)
            domain_str = asplitter.split()
            problem_str = asplitter.fix_problem()
            old_split = True

        if len(self.domain.cache_stat) > 0:
            f_count = 0
            a_count = 0
            with open(join(self.work_dir, 'cache_stat.txt'), 'w') as file:
                for func in self.domain.cache_stat:
                    f_count += 1
                    file.write(f'function {func}:\n')
                    file.write('\taction:\n')
                    for a in self.domain.cache_stat[func]:
                        a_count += 1
                        file.write(f'\t{a}\n')
                file.write(f'total:\nfunctions - {f_count}\nactions - {a_count}\n')

        with open(domainpth, 'w') as f:
            f.write(domain_str)

        problempth = join(self.work_dir, 'problem.pddl')
        with open(problempth, 'w') as f:
            f.write(problem_str)

        returncodes = []
        
        if settings.BROWSER_MODE:
            import hyperc.web_ff_inter
            # global reload_lock
            # if not reload_lock.acquire(): raise EnvironmentError("WASM Vritual Machine busy; please wait.")
            try:
                hyperc.web_ff_inter.select_frame()
                hyperc.web_ff_inter.write_domain_file(domain_str)
                hyperc.web_ff_inter.write_problem_file(problem_str)
                hyperc.web_ff_inter.run_ff_solver()
                plan = hyperc.web_ff_inter.read_plan()
                if plan == "NoSolutionProven":
                    hyperc.web_ff_inter.reset()  # FIXME: exit runtime, re-run Module instead of reloading else:
                    raise hyperc.exceptions.NoSolutionProven("The problem has no solution (guaranteed).")
                if plan == "NoSolution":
                    hyperc.web_ff_inter.reset()  # FIXME: exit runtime, re-run Module instead of reloading else:
                    raise hyperc.exceptions.SchedulingError("Could not find solution")
                if old_split:
                    plan = asplitter.unsplit_plan(plan.lower())
            except AttributeError:
                raise EnvironmentError("WASM Vritual Machine busy; please wait.")
            except TypeError:
                raise EnvironmentError("WASM Vritual Machine busy; please wait.")
            # reload_lock.release()
            # if not reload_lock.acquire(): raise EnvironmentError("WASM Vritual Machine busy; please wait.")
            # hyperc.web_ff_inter.reset(reload_lock.release)  # FIXME: exit runtime, re-run Module instead of reloading else:
            hyperc.web_ff_inter.reset()  # FIXME: exit runtime, re-run Module instead of reloading else:
        else:

            check_user_disable_execution(self.solver_lock)

            settings.HYPERC_MAX_PROC_COUNTER = 0
            if gen_invariants:
                sas_file = None
                running_translator = translate_only(max_time=settings.SOLVER_MAX_TIME,
                                                    work_dir=self.work_dir, term_list=self.term_list)
                wait_loop = True
                last_message = ""
                stop_time = time.time() + max_time 
                while wait_loop:
                    check_user_disable_execution(self.solver_lock)
                    retcode = running_translator.proc.poll()
                    if retcode is not None:
                        if retcode == 0:
                            file_name = os.path.join(running_translator.run_dir, 'output.sas')
                            with open(file_name, 'r') as file:
                                sas_file = sas_collector.SASFile(file)
                            break
                        else:
                            output, err = r_p.proc.communicate(timeout=max_time)
                            with open("{0}/stderr.log".format(r_p.run_dir), 'w') as f:
                                f.write(err)
                                f.write(f'exit code {retcode}\n')
                                
                            import hyperc.exceptions
                            retline = ["Could not generate plan#"]
                            rc =[retcode, err.replace('\n', ' ')]

                            if rc[0] == 11 or rc[0] == 12:
                                retline.insert(0, "The task likely has no solution#")
                            if rc[0] == 150:
                                retline.insert(0, "Problem too big; too many pushes#")
                            if rc[0] == 10:
                                retline.insert(0, "Obtained proof that task has no solution#")
                            if isinstance(rc, str):
                                retline.append(rc)
                            try:
                                import downward_ch.driver.returncodes
                                for key, value in downward_ch.driver.returncodes.__dict__.items():
                                    if rc[0] == value:
                                        if isinstance(key, str):
                                            key = key.lower().replace("_", " ")
                                            key = key[0].upper() + key[1:]
                                            retline.append(f'{key} {rc[1]}')
                                            continue
                                retline.append(f'{rc[0]} {rc[1]}')
                            except ImportError:
                                retline.append("Code N/A")

                            raise hyperc.exceptions.SchedulingError("\n".join(retline) + "#")
                assert sas_file is not None
                p = PDDLPlan(self.domain.actions, problem, str(sas_file))
                p.plan_to_obj()
                print(p)
                return gen_heap(str(sas_file), self.domain.hashes_map)

            else:
                progress.info("Groudning, computing heuristic and searching")
                running_planners = start_solve_proc(max_time=settings.SOLVER_MAX_TIME, work_dir=self.work_dir, term_list=self.term_list)

                wait_loop = True
                last_message = ""
                stop_time = time.time() + max_time 
                while wait_loop:
                    if self.solver_lock is not None:
                        if not self.solver_lock.locked():
                            time.sleep(1)
                            for r_p in running_planners:
                                r_p.kill()
                            if settings.HYPERC_HR_LOG == '1':
                                for dir in os.walk(self.work_dir):
                                    if "stdout.log" in dir[2]:
                                        with open(join(dir[0], "stdout.log"), "r") as f:
                                            with open(join(dir[0], "stdout_hr.log"), "w") as f_hr:
                                                f_hr.write(get_human_readable_plan(f.read(), self.domain.hashes_map))
                            import hyperc.exceptions
                            raise hyperc.exceptions.UserInterrupt("user disable execution#")
                    time.sleep(0.1)
                    spawn_waiters(running_planners)
                    for r_p in running_planners:
                        if r_p.proc is None:
                            continue
                        retcode = r_p.proc.poll()
                        if retcode is not None:
                            running_planners.remove(r_p)
                            settings.HYPERC_MAX_PROC_COUNTER -= 1
                            if retcode == 0:
                                if r_p.translator is not None:
                                    parent_copy = copy.deepcopy(r_p.parent)
                                    parent_copy.translator = None
                                    parent_copy.work_dir = r_p.run_dir
                                    running_planners.extend(gen_search_proc(parent_copy))
                                    break
                                else:
                                    try:
                                        with open(join(r_p.run_dir, 'out.plan'), 'r') as f:
                                            plan = f.read().lower()
                                            if old_split:
                                                plan = asplitter.unsplit_plan(plan)
                                                open(join(r_p.run_dir, 'out_unsplit.plan'), 'w').write(plan)
                                        if settings.STORE_SAS == '0':
                                            sas_file = os.path.join(r_p.run_dir, 'output.sas')
                                            try:
                                                os.remove(sas_file)
                                            except:
                                                log.info("cant remove %s", sas_file)
                                        wait_loop = False
                                    except FileNotFoundError:
                                        pass
                            else:
                                output, err = r_p.proc.communicate(timeout=max_time)
                                if os.path.exists(r_p.run_dir):
                                    with open("{0}/stderr.log".format(r_p.run_dir), 'w') as f:
                                        f.write(err)
                                        f.write(f'exit code {retcode}\n')
                                        
                                if retcode != 0:
                                    returncodes.append([retcode, err.replace('\n', ' ')])

                            # We should break because we iterate changed list
                            break
                        else:
                            if r_p.check_timeout():
                                log.info('Solver %s TIMEOUT', r_p.name)
                                r_p.kill()
                                running_planners.remove(r_p)
                                returncodes.append(f'Solver {r_p.name} TIMEOUT')
                    if wait_loop:
                        for r_p in running_planners:
                            try:
                                if r_p.proc is None: continue
                                with open(join(r_p.run_dir, "stdout.log"), "rb") as f:
                                    first = f.readline()
                                    last = readlast(f, b"\n")
                                if len(last) < 60 and last != last_message and len(last) > 3:
                                    last_message = last
                                    progress.info(last.decode("utf-8").split("[")[0])
                            except:
                                pass
                        if time.time() > stop_time:
                            import hyperc.exceptions
                            raise hyperc.exceptions.SchedulingTimeout("Timed out searching")
                        if len(running_planners) == 0:
                            import hyperc.exceptions
                            retline=["Could not generate plan#"]
                            for rc in returncodes:
                                if rc[0] == 11 or rc[0] == 12:
                                    retline.insert(0, "The task likely has no solution#")
                                if rc[0] == 150:
                                    retline.insert(0, "Problem too big; too many pushes#")
                                if rc[0] == 10:
                                    retline.insert(0, "Obtained proof that task has no solution#")
                                if isinstance(rc, str):
                                    retline.append(rc)
                                    continue
                                try:
                                    import downward_ch.driver.returncodes
                                    for key, value in downward_ch.driver.returncodes.__dict__.items():
                                        if rc[0] == value:
                                            if isinstance(key, str):
                                                key = key.lower().replace("_", " ")
                                                key = key[0].upper() + key[1:]
                                                retline.append(f'{key} {rc[1]}')
                                                continue
                                    retline.append(f'{rc[0]} {rc[1]}')
                                except ImportError:
                                    retline.append("Code N/A")
                                
                            raise hyperc.exceptions.SchedulingError("\n".join(retline) + "#")
                    else:
                        for r_p in running_planners:
                            log.info('Kill %s loser', r_p.name)
                            r_p.kill()

                settings.HYPERC_MAX_PROC_COUNTER = 0

                log.debug(f'Output path: {self.work_dir}')


        p = PDDLPlan(self.domain.actions, problem, plan)
        p.plan_to_obj()
        try:
            for dir in os.walk(self.work_dir):
                if "stdout.log" in dir[2]:
                    with open(join(dir[0], "stdout.log"), "rb") as f:
                        import hyperc.util
                        lines = hyperc.util.tail(f, lines=20)
                        for l in str(lines).split("\\n"): 
                            if "Evaluations" in l:
                                try:
                                    new_evals = int(l.split()[1].strip())
                                    if self.metadata["stats"]["evaluations"] == -1 or self.metadata["stats"]["evaluations"] > new_evals:
                                        self.metadata["stats"]["evaluations"] = new_evals
                                except IndexError:
                                    pass
                                break
        except IOError:
            log.debug("Could not load stdout.log to generate stats")

        if settings.HYPERC_HR_LOG == '1':
            with open(os.path.join(self.work_dir, 'out.plan'), 'w') as f:
                f.write(get_human_readable_plan(plan, self.domain.hashes_map))
            with open(os.path.join(self.work_dir, 'out_unsplitted.plan'), 'w') as f:
                f.write(str(p))
                
            for dir in os.walk(self.work_dir):
                if "stdout.log" in dir[2]:
                    with open(join(dir[0], "stdout.log"), "r") as f:
                        with open(join(dir[0], "stdout_hr.log"), "w") as f_hr:
                            f_hr.write(get_human_readable_plan(f.read(), self.domain.hashes_map))
        log.debug('Resulting plan:\n{}'.format(plan))

        if settings.HYPERC_CLEANUP == '1':
            try:
                shutil.rmtree(self.work_dir)
            except:
                log.info("can't remove work dir folder %s", self.work_dir)

    
        return p 
    
    def run():
        # TODO
        raise AssertionError()

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def getmro_patched(cls_):
    if settings.HYPERC_STRICT_TYPING:
        if cls_ == bool:
            return (bool, object)
        return inspect.getmro(cls_)
    if cls_ == int:
        return (int, str, object)
    else:
        return inspect.getmro(cls_)


# Object taxonomy generator
def pddl_types(classes):
    "Generate object taxonomy in PDDL schmema compatible textual format"
    types_ = list()
    res_dict = defaultdict(list)
    sorted_classes = sorted(list(set(classes)), key=lambda x: x.__name__)
    for cls_ in sorted_classes:
        for child, parent in pairwise(getmro_patched(cls_)):
            parent_name = parent.__name__
            if parent_name != 'object':
                parent_name = f"{parent.__name__}-{hyperc.util.h_id(parent)}"
            new_res = f"{child.__name__}-{hyperc.util.h_id(child)}"
            if new_res not in res_dict[parent_name]:
                res_dict[parent_name].append(new_res)
    for parent, children in res_dict.items():
        new_type = '{children} - {parent}'.format(children=' '.join(children), parent=parent)
        if new_type not in types_:
            types_.append(new_type)
    return types_

class TextDomain():
    def __init__(self,actions=None):
        if actions:
            self.actions = actions
        else:
            self.actions = []
        self.func_action_dict = defaultdict(list)


class Domain():
    """
        self.types is list of ObjectDeclaration
        self.predicates is PredicateDeclaration
        self.dummy == True means that the Domain is simple text created by self.load_from_file()
    """
    def __init__(self, classes=None, predicates=None, actions=None):
        self.dummy= False
        self.actions = actions or []
        self.types = []
        self.classes = classes if classes is not None else set()
        self.predicates = predicates or []
        self.domain_name = 'poodle-generated'
        self.function_name = None
        if not settings.HYPERC_DONT_REMOVE_ACTIONS:
            self.deduplicate_actions()
        self.cache_stat = {}
        self.hashes_map = {}  # Will be filled in by FullDomain initialization...

    def get_predicate_declaration_names(self):
        names=set()
        for p in self.predicates:
            names.add(p.fact)
        return names
    
    def deduplicate_actions(self):
        all_act_sigs = set()
        new_actions = []
        for act in self.actions:
            act_sig = act.get_action_signature()
            if not act_sig in all_act_sigs:
                all_act_sigs.add(act_sig)
                new_actions.append(act)
            else:
                log.debug("Deleting duplicate action %s" % act.name)
        self.actions = new_actions

    def dump_to_cache(self, cache: Cache, is_test=False, gg_classes=None):
        func_action_dict = defaultdict(list)
        skipped_function_hash = set()
        for a in self.actions:
            try:
                candidate_for_dump = function_hash(a.function)
                print(f"candidate for dump {a.function.__name__} {candidate_for_dump}")
            except TypeError as e:
                if is_test:
                    raise e
                try:
                    log.warning("Bad function for hashing ", a.function.__name__, " error is ", e)
                except:
                    log.error("Very bad function for hashing ")
                continue
            if candidate_for_dump in skipped_function_hash:
                continue
            if candidate_for_dump in cache:
                continue
            try:
                t_a = a.dump_as_text(gg_classes=gg_classes)
                func_action_dict[t_a.function_hash].append(t_a)
            except hyperc.exceptions.NotSupportInstaceType as e:
                f_hash = function_hash(a.function)
                skipped_function_hash.add(f_hash)
                if f_hash in func_action_dict:
                    del func_action_dict[f_hash]

        for hash in func_action_dict:
            # default expire time 1 month
            cache.set(key=hash, value=func_action_dict[hash], expire=settings.HYPERC_CACHE_EXPIRE_TIME)
                
    def load_action_from_text(self, text_action: TextAction, global_objects, initial_globals, f, modules, all_classes, gg_classes):
        print(f"load from dump {text_action}")
        resolver = IDPYResolver(self.hashes_map)
        if f'{f.__module__}.{f.__qualname__}' in self.cache_stat:
            self.cache_stat[f'{f.__module__}.{f.__qualname__}'].append(text_action.name)
        else:
            self.cache_stat[f'{f.__module__}.{f.__qualname__}']=[(text_action.name)]
        action = Action(name=text_action.name, idx=text_action.idx, function=f)
        for name in text_action.kwargs:
            log.debug(name," ", text_action.kwargs[name].var_name)
        # print("from dump")
        # print(text_action.function_hash, " ", text_action.name, " ", f)
        #shadow[_self_id()] = HCProxy
        kwargs = {}

        known_types = {
            'SumResult': arithmetic.SumResult, 'MulResult': arithmetic.MulResult, 'DivResult': arithmetic.DivResult, 'GreaterThan': arithmetic.GreaterThan, 'GreaterEqualThan':arithmetic.GreaterEqualThan
        }
        #load garbage
        for gg in text_action.gg_classes:
            c = get_class(f'{gg.module}.{gg.qualname}', all_classes=itertools.chain(
                initial_globals.values(), all_classes))
            assert c is not None, f'Cant load garbage object {gg.module}.{gg.qualname} not found'
            gg_classes.add(c)

        # all_classes.update(known_types.values())
        parent = hc_mod.HCProxy(wrapped=f, name=f.__name__, parent=None, container=None, place_id="__STATIC")
        for p in itertools.chain(text_action.precondition, text_action.effect):
            vars=[]
            for v in p.vars:
                if "?" in v.self_id:
                    if v.self_id in kwargs:
                        vars.append(kwargs[v.self_id])
                        continue
                    # print(v.self_id)
                    if (v.self_id in text_action.kwargs) or (v.self_id in text_action.parameters):
                        if v.type in ['int', 'float', 'bool', 'str']:
                            proxy_obj = hc_mod.HCProxy(wrapped=None, name=v.name,
                                                       class_=pydoc.locate(v.type), parent=parent, place_id="__STATIC")
                        elif v.type in known_types:
                            proxy_obj = hc_mod.HCProxy(wrapped=None, name=v.name, class_=known_types[v.type], parent = parent, place_id="__STATIC")
                        else:
                            c = get_class_by_qualname(all_classes=global_objects, qualname=v.qualname, module=v.module)
                            if c is None:
                                c = get_class(f'{v.module}.{v.qualname}', all_classes=self.classes)
                                if c is None:
                                    c = get_class(f'{v.module}.{v.qualname}', all_classes=initial_globals.values())
                                    if c is None:
                                        c = get_class(f'{v.module}.{v.qualname}')
                                assert c is not None, f'Not found {v.module}.{v.qualname}'
                                all_classes.add(c)
                                proxy_obj = hc_mod.HCProxy(wrapped=None, name=v.name, class_=c, parent=parent, place_id="__STATIC")
                            else:
                                c._self_seal()
                                # assert c is not None, "{0} {1} {2} {3}".format(v, v.qualname , v.module, global_objects)
                                proxy_obj = hc_mod.HCProxy(wrapped=None, name=v.name,
                                                           class_=c._self_class, parent=parent, place_id="__STATIC")
                                all_classes.add(c._self_class)
                        proxy_obj._self_seal()
                        proxy_obj._self_fixed_id = v.self_id.split('-')[-1]
                        #Fill kwargs for action here
                        
                        if v.self_id in text_action.kwargs:
                            kwargs[v.self_id] = proxy_obj
                            action.kwargs[text_action.kwargs[v.self_id].var_name] = proxy_obj
                            log.debug("load ", action.name, " ", "var_name ",
                                  text_action.kwargs[v.self_id].var_name, " ", v.self_id, text_action.kwargs[v.self_id].name, " proxy: ", proxy_obj)

                        vars.append(proxy_obj)
                        continue


                    c = get_class_by_str(all_classes=global_objects, name=v.self_id)
                    assert c is not None, f"{v.self_id} {text_action.parameters}"
                    if c:
                        vars.append(c)

                    # if not found in global_objects, create new type for planner

                    # proxy_obj = hc_mod.HCProxy(wrapped=None, name=v.name, class_=c._self_class, parent=None)

                    # vars.append(v)
                    #TODO may be useless and should be removed
                elif int(str(v).split('-')[-1]) <= 99999999:
                    const_id = int(str(v).split('-')[-1])
                    const = resolver.id_to_pyobj(const_id)
                    proxy_obj = hc_mod.HCProxy(wrapped=const, name=v.name, parent=parent, place_id="__STATIC")
                    proxy_obj._self_seal()
                    vars.append(proxy_obj)
                    all_classes.update([type(const)])
                elif v.type in ['int', 'float', 'bool', 'str']:
                    proxy_obj = hc_mod.HCProxy(wrapped=v.value, name=v.name, parent=parent, place_id="__STATIC")
                    proxy_obj._self_seal()
                    vars.append(proxy_obj)
                    all_classes.update([type(v.value)])
                elif v.type in ['module']:
                    if v.name in sys.modules:
                        obj = sys.modules[v.name]
                        modules[v.name].add(p.name) # add global variable reference
                    else:
                        raise hyperc.exceptions.NotSupportInstaceType(f"Unsupport {v.self_id} type {v.type} ")
                    proxy_obj = hc_mod.HCProxy(wrapped=obj, name=v.name, parent=parent, place_id="__STATIC")
                    global_objects.append(proxy_obj)
                    proxy_obj._self_seal()
                    vars.append(proxy_obj)
                    all_classes.update([type(obj)])
                else:
                    raise hyperc.exceptions.NotSupportInstaceType(f"Unsupport {v.self_id} type {v.type} ")
            
            # Add lonely kwarg
            for kwarg_self_id in text_action.kwargs:
                log.debug(kwarg_self_id, "==", kwargs)
                if kwarg_self_id not in kwargs:
                    v = text_action.kwargs[kwarg_self_id]
                    if '?' in kwarg_self_id:
                        c = get_class_by_qualname(
                            all_classes=global_objects, qualname=text_action.kwargs[kwarg_self_id].qualname,
                            module=text_action.kwargs[kwarg_self_id].module)
                        if c is None:
                            c = get_class(f'{v.module}.{v.qualname}', all_classes=self.classes)
                            if c is None:
                                c = get_class(f'{v.module}.{v.qualname}', all_classes=initial_globals.values())
                                if c is None:
                                    c = get_class(f'{v.module}.{v.qualname}')
                            assert c is not None, "{0} {1}".format(text_action.kwargs[kwarg_self_id], text_action.kwargs[kwarg_self_id].qualname)
                            proxy_obj = hc_mod.HCProxy(wrapped=None, name=v.name, class_=c, parent=parent, place_id="__STATIC")
                        else:
                            c._self_seal()
                            # assert c is not None, "{0} {1} {2} {3}".format(v, v.qualname , v.module, global_objects)
                            proxy_obj = hc_mod.HCProxy(wrapped=None, name=v.name, class_=c._self_class, parent=parent, place_id="__STATIC")
                        proxy_obj._self_seal()
                        proxy_obj._self_fixed_id = kwarg_self_id.split('-')[-1]
                        log.debug("!!!!!!!!!!!!!", proxy_obj._self_id(),
                            proxy_obj._self_resolve_linked()._self_id())
                    elif int(kwarg_self_id.split('-')[-1]) <= 99999999:
                        const_id = int(kwarg_self_id.split('-')[-1])
                        # if str(v).split('-')[0] == 'int':
                        log.debug("id is ", const_id, " ", kwarg_self_id)
                        const = resolver.id_to_pyobj(const_id)
                        proxy_obj = hc_mod.HCProxy(wrapped=const, name=v.name, parent=parent, place_id="__STATIC")
                        proxy_obj._self_seal()
                    elif text_action.kwargs[kwarg_self_id].type in ['int', 'float', 'bool', 'str']:
                        proxy_obj = hc_mod.HCProxy(wrapped=v.value, name=v.name, parent=parent)
                        proxy_obj._self_seal()
                    elif text_action.kwargs[kwarg_self_id].type in ['module']:
                        if v.name in sys.modules:
                            obj = sys.modules[v.name]
                            modules[v.name].add[p.name]
                        else:
                            raise hyperc.exceptions.NotSupportInstaceType(
                                f"Unsupport {text_action.kwargs[kwarg_self_id].self_id} type {text_action.kwargs[kwarg_self_id].type} {text_action.kwargs[kwarg_self_id]}")
                        proxy_obj = hc_mod.HCProxy(wrapped=obj, name=v.name, parent=parent, place_id="__STATIC")
                        global_objects.append(proxy_obj)
                        proxy_obj._self_seal()
                        vars.append(proxy_obj)
                        all_classes.update([type(obj)])
                    else:
                        raise hyperc.exceptions.NotSupportInstaceType(
                            f"{text_action.kwargs[kwarg_self_id].self_id} const_id > 99999999 Unsupport ID")
                    
                    action.kwargs[text_action.kwargs[kwarg_self_id].var_name] = proxy_obj


            obj_predicate = Predicate(fact=p.fact, name=p.name, vars=vars, element=p.element,
                                              negated=p.negated, is_novalue_fact=p.is_novalue_fact)

            if p in text_action.precondition:
                action.precondition.append(obj_predicate)
            else:
                action.effect.append(obj_predicate)

        # action.generate_parameters()
        self.actions.append(action)

            
    def get_filtered_actions(self, p_novalue_facts, used_classes):
        if settings.HYPERC_DONT_REMOVE_ACTIONS: return self.actions
        "Filter actions for non-existing branches with novalue"
        # TODO: more generic filtration: filter out all actions that have preconditions that are never added in effect
        delete_actions = set()
        # log.debug(f"Sets of objects: nov:{p_novalue_facts}, used:{used_classes}")
        # Now scan for anything that adds a novalue fact
        #   ... and add to "imaginary" facts as we never know if this is going to happen
        for a in self.actions:
            for pred in a.effect:
                if pred.is_novalue_fact and not pred.negated:  # adding novalue..
                    p_novalue_facts.add(pred.fact)
        for a in self.actions:
            object_classes, no_v_fact_set = a.get_classes_stats()  # Get classes with novalue
            if not no_v_fact_set <= p_novalue_facts:
                # Can only ignore the branch if no effect creates this novalue fact!
                log.debug(f"Ignoring {a.name} no-value branch as all values are present")
                delete_actions.add(a)
            # Now filter out actions that have no objects to select
            if not settings.HYPERC_STRICT_TYPING:
                used_classes.add(str)
                used_classes.add(int)
                used_classes.add(bool)
            if not object_classes <= used_classes:
                delete_actions.add(a)
        # log.debug(f"Filtered out {len(delete_actions)} actions: {delete_actions} due to no facts or no objects")
        return [a for a in self.actions if not a in delete_actions]

    def get_filtered_object_taxonomy(self):
        "Filter object taxonomy to only include definitions for objects that exist (for full PDDL format compliance)"
        # TODO
        pass

    def load_from_file(self, line):
        self.dummy = True
        full_list = lisp_to_list(line)
        self.types = []
        for i in full_list[0]:
            if isinstance(i, list):
                # domain name load
                if i[0] == 'domain':
                    self.domain_name = i[1]
                if i[0] == ':functions':
                    self.function_name = i[1][0]
                # types load
                if i[0] == ':types':
                    type = ObjectDeclaration()
                    skipMe = False
                    for idx, val in enumerate(i[1:]):
                        if skipMe:
                            skipMe = False
                            type.type = val
                            self.types.append(type)
                            type = ObjectDeclaration()
                            continue
                        if val == '-':
                            skipMe = True
                            continue
                        type.append(val)
                # predicate declaration load
                if i[0] == ':predicates':
                    for pd_str in i[1:]:
                        skipMe = False
                        self.predicates.append(PredicateDeclaration(fact=pd_str[0]))
                        # self.predicates[-1].vars =[]
                        for val in pd_str[1:]:
                            # log.debug(val)
                            if skipMe:
                                skipMe = False
                                parameter.type = val
                                continue
                            if val == '-':
                                skipMe = True
                                continue
                            parameter = Parameter(var=val)
                            # log.debug(id(parameter))
                            self.predicates[-1].vars.append(parameter)
                    #     log.debug("predicate ->>{0}".format(self.predicates[-1]))
                    # log.debug(" \n".join(map(str,self.predicates)))

                # action load
                if i[0] == ':action':
                    action = Action(name=i[1], cost_target=None)
                    action.parameters = []
                    self.actions.append(action)
                    skipMe = False
                    # load :parameters
                    for val in i[3]:
                        if skipMe:
                            skipMe = False
                            parameter.type = val
                            continue
                        if val == '-':
                            skipMe = True
                            continue
                        parameter = Parameter(var=val)
                        action.parameters.append(parameter)
                    # load p:precondition
                    if i[5][0] == 'and':
                        for val in i[5]:
                            if not isinstance(val, list):
                                continue
                            predicate = Predicate()
                            predicate.load_from_list(val)
                            action.precondition.append(predicate)
                    else:
                        predicate = Predicate()
                        predicate.load_from_list(i[5])
                        action.precondition.append(predicate)

                    # load p:effect
                    if i[7][0] =='and':
                        for val in i[7]:
                            if not isinstance(val, list):
                                continue
                            if val[0] == 'increase':
                                action.cost = val[2]
                                action.cost_target = val[1][0]
                                continue
                            predicate = Predicate()
                            predicate.load_from_list(val)
                            action.effect.append(predicate)
                    else:
                        predicate = Predicate()
                        predicate.load_from_list(i[7])
                        action.effect.append(predicate)

    def __str__(self):
        return self.render()

    def render(self, used_classes=None, novalue_facts=None):
        # if not used_classes is None and not novalue_facts is None:
        #     factions = self.get_filtered_actions(p_novalue_facts=novalue_facts, used_classes=used_classes)
        #     log.debug(f"Filtered actions: {len(factions)} < {len(self.actions)}")
        # else:
        #     factions = self.actions
        factions = self.actions
        
        # log.debug(f"Actions rendered: {[a.name for a in factions]}")

        if not self.types:
            self.types = pddl_types(self.classes)
        #TODO disable function
        self.function_name = None
        if self.function_name is None:
            function_pddl = """"""
        else:
            function_pddl = """    (:functions
        ({function_name})
    )\n""".format(function_name=self.function_name)

        return """(define (domain {domain_name})
    (:requirements :strips :typing :equality :negative-preconditions :disjunctive-preconditions)
    (:types {types})
    (:predicates {predicate_declaration}
    )
{functions}    {actions}
)
""".format(domain_name=self.domain_name, types=" ".join(map(str, self.types)),
            predicate_declaration="\n        ".join(map(str, self.predicates)),
            functions=function_pddl,
            actions="\n    ".join(map(str, factions))
            )

# SO https://stackoverflow.com/a/91430
def unique(l):
    s = set(); n = 0
    for x in l:
        if x not in s: s.add(x); l[n] = x; n += 1
    del l[n:]

class Problem():
    """
        self.objects is list of ObjectDeclaration
        self.init and self.goal are lists of Predicate
    """
    def __init__(self, classes=None, metric="minimize", metric_target="total-cost", gg_classes=None,
                predicates=None, global_facts=None, global_objects=None, attrs_init=None, solver_lock=None,
                module_names=None, referenced_set_objects=None):
        self.solver_lock = solver_lock
        self.referenced_set_objects = referenced_set_objects or []
        self.gg_classes = gg_classes or []
        self.attrs_init = attrs_init or {}
        self.module_names = module_names or {}
        self.classes = classes or set()  # All possible classes
        self.novalue_facts = set()  # Classes of objects that have no values at all
        self.used_classes = set()  # All classes that we have added init for/registered in d_objects
        self.classes.add(bool)
        self.predicates = predicates or set()
        self.global_facts = global_facts or set()
        self.objects = []
        self.init = []
        self.old_init = []  # Holds original, non-filtered init
        self.goal = []
        self.metric = metric
        self.metric_target = metric_target
        self.garbage = [] # Holds all the garbage
        self.d_objects = defaultdict(set)
        self.objid_obj_map = dict()
        for fact in self.global_facts:
            for v in fact.vars:
                self.register_object(v)
        self.init.extend(list(self.global_facts))
        # These two bastards are hard to catch
        # TODO: figure out why we miss them and implement generalized fix
        bool_true = hc_mod.HCProxy(wrapped=True, name="True", parent=None, place_id="__STATIC")
        bool_false = hc_mod.HCProxy(wrapped=False, name="False", parent=None, place_id="__STATIC")
        self.register_object(bool_true)
        self.register_object(bool_false)
        self.global_objects = global_objects
        if self.global_objects is None:
            self.global_objects =[]
        for obj in self.global_objects:
            self.register_object(obj)
        self.hashes_map = {}  # Hashes to store stable classes, functions mappings
    
    def register_object(self, obj):
        self.d_objects[obj._self_class_id()].add(obj._self_id())
        self.objid_obj_map[obj._self_id()] = obj
        self.used_classes.add(obj._self_class)
    
    def reset(self):
        if self.old_init:
            self.init = self.old_init
        self.old_init = []

    def generate_garbage(self):
        for cls_ in self.gg_classes:
            first = True
            prev = None
            for i in range(settings.HYPERC_NEW_OBJECTS):  # FIXME: dynamic new class garbage
                new_garbage = cls_.__new__(cls_)
                self.garbage.append(new_garbage)
                h_new_gb = hc_mod.HCProxy(wrapped=new_garbage, name=f"<garbage {cls_.__name__}>", parent=None, place_id="__STATIC")
                h_new_gb._self_seal()
                self.init.append(Predicate(name="hcsystem-is-free", vars=[h_new_gb, hc_mod.resolve_proxy(None, True)]))
                if first:
                    first = False
                    self.init.append(Predicate(name="hcsystem-is-free-current", vars=[h_new_gb, hc_mod.resolve_proxy(None, True)]))
                    prev = h_new_gb
                    continue
                self.init.append(Predicate(name="hcsystem-is-free-next", vars=[prev, h_new_gb]))
                prev = h_new_gb
    
    def generate_math_garbage(self):
        progress.info("Propagating numbers")
        self.classes.add(int)  # No point in doing this as Py doesn't have literals garbage
        self.classes |= set(
            [arithmetic.SumResult, arithmetic.MulResult, arithmetic.DivResult, arithmetic.GreaterThan, arithmetic.GreaterEqualThan])
        math_garbage = []
        for i in range(settings.min_int, settings.max_int + 1):  # FIXME: 16-bit math?
            check_user_disable_execution(self.solver_lock)
            if i % 10: progress.info("Propagating numbers %s", i)
            i_prox = hc_mod.HCProxy(wrapped=i, name="<new int>", parent=None, place_id="__STATIC")
            if settings.DEBUG:
                log.debug(f"{i} = {i_prox._self_id()}")
            i_prox._self_seal()
            math_garbage.append(i)
            self.register_object(i_prox)
        self.sif = arithmetic.SimpleIntegerFactory(math_garbage)  # will generate objects into heap
        import gc
        i = 0
        total = float(self.sif.heap_len())
        term = "??"
        for obj in itertools.chain(*self.sif.heap):
            if i % 100 == 0: 
                if hasattr(obj, "term1"): term = obj.term1
                pp = int(i / total * 100)
                progress.info("Propagating numbers heap (%s) - %s %%" % (term, pp))
            hc_parent = hc_mod.HCProxy(wrapped=obj, parent=None, place_id="__STATIC")
            hc_parent._self_seal()
            self.register_object(hc_parent)
            obj_refs = gc.get_referents(obj)
            for attr_name, attr_value in obj_refs[0].items(): 
                if attr_value.__class__ in self.classes:
                    hc_ob = hc_mod.HCProxy(wrapped=attr_value, name=f"{attr_name}>", parent=None, place_id="__STATIC")
                    hc_ob._self_seal()
                    self.register_object(hc_ob)
                    self.init.append(Predicate(name=f"{attr_name}", vars=[hc_parent, hc_ob]))
            i += 1


    def inject_novalue_facts(self):  # generate novalue facts
        "Injects the facts about known missing values of properties ever used, for missing-property path to work"
        class_props = defaultdict(set)
        object_props = defaultdict(set)

        for pred in self.init:
            if len(pred.vars) == 2:  # Means this is Object-property predicate
                if pred.is_novalue_fact: continue
                # 1. Collect (to set) all properties for every object class that we need to have according to predicates
                class_props[pred.vars[0]._self_class_id()].add(pred.fact)
                # 2. Collect (to set) all property pairs that we have defined in init for every object
                object_props[pred.vars[0]._self_id()].add(pred.fact)
        
        # Now do the same for every predicate (because some properties may not exist in init but only in predicates)
        for pred_decl in self.predicates:
            if not pred_decl.base_obj: continue
            if pred_decl.is_hasattr:  # Is a fact from hasattr, pay attention!
                class_props[pred_decl.base_obj._self_class_id()].add(pred_decl.for_fact)
            if "novalue" in pred_decl.fact:
                continue
            class_props[pred_decl.base_obj._self_class_id()].add(pred_decl.fact)
        
        for obj_class, objid_set in self.d_objects.items():
            for obj_id in objid_set:
                missing_value_facts = class_props[self.objid_obj_map[obj_id]._self_class_id()] ^ object_props[obj_id]
                for missing_value in missing_value_facts:
                    # if self.objid_obj_map[obj_id]._self_wrapped in self.garbage:
                        # Don't generate novalues for garbage if we're always initting...
                        # FIXME: first check that __init__ of this class sets this prop
                        # continue
                    # 3. For every object, create a set-diff and inject the novalue predicates. 
                    # TODO: skip generating novalue facts for objects that are guaranteed not to have novalue
                    attr_name = missing_value.split("-")[-1]
                    attr_class = self.objid_obj_map[obj_id]._self_class
                    if attr_class in self.attrs_init and attr_name in self.attrs_init[attr_class]: 
                        log.debug("Skipping novalue gen for %s.%s", attr_class.__name__, attr_name)
                        continue
                    # Should be same as in se_decoder
                    noval_pred = Predicate(fact=f"{missing_value}-novalue", vars=[self.objid_obj_map[obj_id], hc_mod.resolve_proxy(None, True)], is_novalue_fact=True)
                    self.init.append(noval_pred)
                    log.debug(f"Adding novalue data {str(noval_pred)}")
                    self.novalue_facts.add(noval_pred.fact)
        # NOTE: novalue facts can later be removed at filter_facts

    def load_heap(self):
        # TODO: optimze this hot loop!
        self.generate_garbage()
        import gc
        obj_count = 0
        obj_total = 0
        add_sets = []
        processed_set_ids = set()
        get_objects_ret = gc.get_objects()
        for obj in get_objects_ret:
            obj_total += 1
            if obj_total % 1000 == 0:
                progress.info(f"Loading Python heap into SAS: {int(obj_count/1000)}k/{obj_total/1000}k objects")
            if (not isinstance(obj, hc_mod.HCProxy) and not isinstance(obj.__class__, hc_mod.HCProxy) 
                    and not isinstance(obj, types.ModuleType) and obj.__class__ in self.classes):
                obj_count += 1
                obj_refs = gc.get_referents(obj)
                if not isinstance(obj, set) or not obj_refs:
                    hc_parent = hc_mod.HCProxy(wrapped=obj, parent=None, place_id="__STATIC")
                    hc_parent._self_seal()
                    self.register_object(hc_parent)
                if not obj_refs: continue
                # Now check if the objects we're scanning IS 'our' object and contains some SETs
                if type(obj) != set:  # as we only support 'set' built-in objects as compound type
                    if not isinstance(obj_refs[0], dict): 
                        log.warning("Skipping compound object where is should not be! Check interfaces consistency!")
                        continue
                    for el in obj_refs[0].values():
                        if type(el) == set:
                            add_sets.append(el)
                # TODO: remove expensive references check
                if not isinstance(obj_refs[0], dict): 
                    # It's probably a set
                    if isinstance(obj, set):
                        # refs = gc.get_referrers(obj) # remove this, does not work and is expensive
                        # used_in_our_obj = False
                        referenced_directly = False
                        contains_our_elements = False
                        # for r in refs[:20]:
                        #     if type(r) in self.classes:
                        #         used_in_our_obj = True
                        #         break
                        if obj in self.referenced_set_objects:
                            referenced_directly = True
                        for set_el in obj_refs:
                            if type(set_el) in self.classes and not type(set_el) in [int, str, set, bool]: 
                                # rclasses = set([type(r) for r in refs])
                                contains_our_elements = True
                                break
                        if (not referenced_directly and 
                            # not used_in_our_obj and 
                            not contains_our_elements):
                            continue
                        # Workaround for pollution bug #400
                        only_nums = list(filter(lambda x: type(x) == int, obj))
                        if len(only_nums) == len(obj) and max(only_nums) > 10000 and max(only_nums) > settings.max_int:
                            continue
                        # end workaround
                        hc_parent = hc_mod.HCProxy(wrapped=obj, parent=None, place_id="__STATIC")
                        hc_parent._self_seal()
                        self.register_object(hc_parent)
                        # Check if this set contains "our" objects
                        # FIXME: only add a set if it is in any of our accessible globals
                        # FIXME: or it is referenced by any of our objects
                        processed_set_ids.add(id(obj))
                        for set_el in obj_refs:
                            if not type(set_el) in self.classes: 
                                # log.debug("Skipping set bevcause element is not ours")
                                break
                            hc_ob = hc_mod.HCProxy(wrapped=set_el, name="<set elememnt>", parent=None, place_id="__STATIC")
                            hc_ob._self_seal()
                            self.register_object(hc_ob)
                            self.init.append(Predicate(name="elements", vars=[hc_parent, hc_ob], element=True))
                    continue
                for attr_name, attr_value in obj_refs[0].items(): # TODO: use filter() to speed up filtering?
                    if attr_name.startswith("__"): continue
                    # TODO: check for set()'s
                    if attr_value.__class__ in self.classes:
                        hc_ob = hc_mod.HCProxy(wrapped=attr_value, name=f"{attr_name}>", parent=None, place_id="__STATIC")
                        hc_ob._self_seal()
                        self.register_object(hc_ob)
                        self.init.append(Predicate(name=f"{attr_name}", vars=[hc_parent, hc_ob]))

                    # if isinstance(attr_value, set):
                    #     obj_refs2 = gc.get_referents(attr_value)
                    #     # Check if this set contains "our" objects
                    #     # FIXME: only add a set if it is in any of our accessible globals
                    #     # FIXME: or it is referenced by any of our objects
                    #     for set_el in obj_refs2:
                    #         if not type(set_el) in self.classes: 
                    #             # log.debug("Skipping set bevcause element is not ours")
                    #             break
                    #         hc_ob = hc_mod.HCProxy(wrapped=set_el, name="<set elememnt>", parent=None)
                    #         hc_ob._self_seal()
                    #         self.register_object(hc_ob)
                    #         name = f"elements-{hc_ob._self_class_id()}"
                    #         self.init.append(Predicate(f"{hc_parent._self_class_id()}-{name}", [hc_parent, hc_ob]))
        # for proxy_obj in self.global_objects:
        #     if not proxy_obj._self_wrapped: continue
        #     obj = proxy_obj._self_wrapped
        #     obj_refs = gc.get_referents(obj)
        #     if not obj_refs: continue
        #     if not isinstance(obj_refs[0], dict): 
        #         if 0 and isinstance(obj, set):
        #             # Check if this set contains "our" objects
        #             # FIXME: only add a set if it is in any of our accessible globals
        #             # FIXME: or it is referenced by any of our objects
        #             for set_el in obj_refs:
        #                 if not type(set_el) in self.classes: 
        #                     # log.debug("Skipping set bevcause element is not ours")
        #                     break
        #                 hc_ob = hc_mod.HCProxy(wrapped=set_el, name="<set elememnt>", parent=None)
        #                 hc_ob._self_seal()
        #                 self.register_object(hc_ob)
        #                 name = f"elements-{hc_ob._self_class_id()}"
        #                 self.init.append(Predicate(f"{hc_parent._self_class_id()}-{name}", [hc_parent, hc_ob]))
    
        for module_name, module_globals in self.module_names.items():
            if module_name.startswith("<locals"):  # ignore locals
                continue
            module_obj = sys.modules[module_name]
            for glob_name in module_globals:
                hc_module = hc_mod.HCProxy(wrapped=module_obj, name=module_name, parent=None, place_id="__STATIC")
                hc_module._self_seal()
                hc_glob_value = hc_mod.HCProxy(wrapped=getattr(module_obj, glob_name), name=glob_name, parent=None, place_id="__STATIC")
                hc_glob_value._self_seal()
                self.register_object(hc_module)
                self.register_object(hc_glob_value)
                self.init.append(Predicate(name=f"{glob_name}", vars=[hc_module, hc_glob_value]))
    
        # Now clean sets FIXME: this is a workaround for #106
        sets_with_facts = set()
        for pred in self.init:
            if len(pred.vars) == 2:  # Means this is Object-property predicate
                if "novalue" in pred.fact: continue
                if pred.vars[0]._self_class == set:
                    sets_with_facts.add(pred.vars[0]._self_id())
                if pred.vars[1]._self_class == set:
                    sets_with_facts.add(pred.vars[1]._self_id())
        if sets_with_facts:
            set_class_id = hc_mod.HCProxy(wrapped=set(), parent=None, place_id="__STATIC")._self_class_id()
            filtered_set = self.d_objects[set_class_id] = sets_with_facts
        
        for setobj in add_sets:
            if not id(setobj) in processed_set_ids:
                obj_refs = gc.get_referents(obj)
                for set_el in obj_refs:
                    if not type(set_el) in self.classes: 
                        log.warning("Skipping set bevcause element is not ours (when set is ours!)")
                        break
                    hc_ob = hc_mod.HCProxy(wrapped=set_el, name="<set elememnt>", parent=None, place_id="__STATIC")
                    hc_ob._self_seal()
                    self.register_object(hc_ob)
                    self.init.append(Predicate(name="elements", vars=[hc_parent, hc_ob], element=True))

        self.generate_math_garbage()
        self.inject_novalue_facts()

    def filter_facts(self, predicate_declarations: set):
        self.old_init = self.init
        self.init = list(filter(lambda x: x.get_signature() in predicate_declarations, self.init))
        if len(self.init) != len(self.old_init):
            log.debug("WRN! dropped unused predicates")
    
    def load_goal(self, goal_obj, state_obj):
        self.goal.append(Predicate(name="reached", vars=[goal_obj, state_obj]))

    def load_from_file(self, line):
        pass
    
    def __str__(self):
        if not self.goal:
            # TODO: generate goal
            pass
        if not self.objects:
            self.objects = [f"{' '.join(list(s_objs))} - {cls_}" for cls_, s_objs in self.d_objects.items() if s_objs]
        dedup_init = list(map(str, self.init))
        unique(dedup_init)
        return self.human_readable_str(init=dedup_init)

    def human_readable_str(self, init):
        #todo metric disabled
        self.metric = None
        if (self.metric is None) or (self.metric_target is None):
            metric = ""
        else:
            metric = f"\n    (:metric {self.metric} ({self.metric_target}))"
        return """(define (problem poodle-generated)
    (:domain poodle-generated)
    (:objects {objects})
    (:init
        {init}
    )
    (:goal
        (and
            {goal}
        )
    ){metric}
)
""".format(objects="\n    ".join(map(str, self.objects)),
                    init="\n    ".join(init),
                    goal="\n    ".join(map(str, self.goal)),
                    metric=metric)


class InstCount:
    def __init__(self):
        self.counter = 0


def get_instantiator(class_, ordered_noninit_objects, inst_count: InstCount):
    "Gets instantiator for garbage object when loaded in Python"
    def instantiator(*args, **kwargs):
        try:
            obj = ordered_noninit_objects[inst_count.counter]
        except IndexError:
            obj = class_(*args, **kwargs)
            # Possible BUG: ASE may remove unexpected
        assert type(obj) == class_
        obj.__init__(*args, **kwargs)
        inst_count.counter += 1
        return obj
    return instantiator


class PDDLPlan():

    def __init__(self, actions, problem, plan=None):
        self.actions = actions
        self.plan = []
        self.problem = problem
        if plan is not None:
            self.text_plan = plan.replace("(", "").replace(")", "")
            self.load_n_unsplit_plan(self.text_plan)

    def load_n_unsplit_plan(self, plan_text):
        s = StringIO(plan_text.lower())
        index = -1
        action_copy = None
        plan = []
        # Separate splitted and not splitted
        for line in s:
            if len(line) < 3: continue
            arr_line = line.split()
            action_found = False
            if arr_line[0][0] == ';':
                continue
            for a in self.actions:
                if arr_line[0].lower() == a.name.lower():
                    action_found = True
                    action_copy = copy.copy(a)
                    action_copy.vars = [x.lower() for x in arr_line[1:]]
                    if action_copy.parent is None:
                        plan.append(action_copy)
                        # log.debug(action_copy.vars)
                    else:
                        if index + 1 != a.idx:
                            plan.append([action_copy])
                        else:
                            if len(plan) > 0  and isinstance(plan[-1], list):
                                plan[-1].append(action_copy)
                            else:
                                plan.append([action_copy])
                        index = a.idx            
            assert action_found, f"Action not found for {arr_line[0]} in: {[a.name for a in self.actions]}"

        # Load variables in parameters(kwargs) direction
        log.debug(f"Loading plan of size {len(plan)}")
        for p in plan:
            if isinstance(p, list):
                action_copy = copy.deepcopy(p[0].parent)
            else:
                action_copy = copy.deepcopy(p)
            self.plan.append(action_copy)

            vars = {}
            log.debug(action_copy.kwargs.values())
            for par in action_copy.kwargs:
                log.info(f"look for par {par} id {action_copy.kwargs[par]._self_id()}")
                if isinstance(p, list):
                    br = False
                    par_index = -1
                    slice_index = -1
                    for s_index, slice in enumerate(p):
                        for p_index, par_slice in enumerate(slice.parameters):
                            log.debug(f"look in {par_slice.var}")
                            if par_slice.var == action_copy.kwargs[par]._self_id():
                                log.debug(f"{par} found")
                                slice_index = s_index
                                par_index = p_index
                                br = True
                                break
                        if br:
                            break
                    # assert not par_index == -1
                    # assert not slice_index == -1
                    # if not hasattr(action_copy, 'vars'):
                    #     action_copy.vars = []
                    if par_index == -1 or slice_index == -1:
                        vars[par] = None
                        log.debug("append None")
                    else:
                        vars[par] = p[slice_index].vars[par_index]
                else:
                    ok = False
                    for p_index, par_act in enumerate(p.parameters):
                        log.debug(f"look by {par_act.var} {action_copy.kwargs[par]._self_id()}")
                        if par_act.var == action_copy.kwargs[par]._self_id():
                            log.debug(f"{par} found")
                            vars[par] = p.vars[p_index]
                            ok = True
                    if not ok:
                        vars[par] = None
            matched_params = {}
            if action_copy.parameters is None:
                action_copy.generate_parameters()
            for par in action_copy.parameters:
                if isinstance(p, list):
                    br = False
                    par_index = -1
                    slice_index = -1
                    # TODO: rewrite this to zip():
                    for s_index, slice in enumerate(p):
                        for p_index, par_slice in enumerate(slice.parameters):
                            if par_slice.var == str(par.var):
                                log.debug(f"{par} found for params")
                                slice_index = s_index
                                par_index = p_index
                                br = True
                                break
                        if br:
                            break
                    if par_index == -1 or slice_index == -1:
                        matched_params[par.var] = (par.orig_proxy, None)
                        # matched_params[par.orig_proxy] = None
                        log.debug("append None")
                    else:
                        matched_params[par.var] = (par.orig_proxy, p[slice_index].vars[par_index])
                        # matched_params[par.orig_proxy] = p[slice_index].vars[par_index]
                else:
                    ok = False
                    for p_index, par_act in enumerate(p.parameters):
                        if par_act.var == str(par.var):
                            log.debug(f"{par} found for param")
                            matched_params[par.var] = (par.orig_proxy, p.vars[p_index])
                            # matched_params[par.orig_proxy] = p.vars[p_index]
                            ok = True
                    if not ok:
                        matched_params[par.var] = (par.orig_proxy, None)
                        # matched_params[par.orig_proxy] = None

            action_copy.vars_matched = vars
            action_copy.pars_matched = matched_params
    
    def __str__(self):
        str = []
        for a in self.plan:
            s = (f"{a.function.__name__}(")
            for p, obj in a.arguments.items():
                s += f'{p}({obj}),'
            if len(a.arguments) > 0:
                s = s[:-1]
            s += ')'
            str.append(s)
        return "\n".join(str)

    def plan_to_obj(self):
        # convert plan to object
        id_resolver = IDPYResolver(self.problem.hashes_map)
        for a in self.plan:
            a.arguments = {}
            a.objects = {}  # mathec objects
            func = a.name.split("-")
            a.function = id_resolver.id_to_pyobj(int(func[-2]))
            log.debug(f"Vars for {a.name}")
            obj = None
            for var_kwname, var_str in a.vars_matched.items():
                if var_str is not None:
                    log.debug(f"var_kwname is {var_kwname} var_str is {var_str}")
                    if var_str == "None":
                        # FIXME: never gets here
                        # If HyperC was able to solve the variable before the search...
                        log.debug(f"Looks like we have a vairable already for %s= %s %s %s", var_kwname, var_str, a.kwargs[var_kwname]._self_id(), a.kwargs[var_kwname]._self_resolve_linked()._self_wrapped)
                        obj = a.kwargs[var_kwname]._self_resolve_linked()._self_wrapped
                    else:
                        var = var_str.split("-")
                        # obj = ctypes.cast(int(var[-1]), ctypes.py_object).value   
                        log.debug(f"Resolving %s= %s %s %s", var_kwname, var, var[-1], int(var[-1]))
                        obj = id_resolver.id_to_pyobj(int(var[-1]))
                    a.arguments[var_kwname] = obj
                    log.debug(f"Argument is {a.arguments}")
                else:
                    # If HyperC was able to solve the variable before the search...
                    log.debug(f"2Looks like we have a vairable already for %s= %s %s %s", var_kwname, var_str, a.kwargs[var_kwname]._self_id(), a.kwargs[var_kwname]._self_resolve_linked()._self_wrapped)
                    if a.kwargs[var_kwname]._self_resolve_linked()._self_wrapped:
                        obj = a.kwargs[var_kwname]._self_resolve_linked()._self_wrapped
                        a.arguments[var_kwname] = obj
                    else:
                        class__ = a.kwargs[var_kwname]._self_resolve_linked()._self_class
                        import gc
                        gc_objects = gc.get_objects()
                        for obj in gc_objects:
                            if isinstance(obj, class__):
                                a.arguments[var_kwname] = obj
                                break
            for par_name, var_str in a.pars_matched.items():
                if var_str[1] is not None and var_str[1] != "None":
                    a.objects[par_name] = (var_str[0], id_resolver.id_to_pyobj(int(var_str[1].split("-")[-1])))

    def execute_plan(self, metadata=None):
        if settings._old_trace:
            import sys
            # sys.settrace(settings._old_trace)
            frame = sys._getframe().f_back
            complete = 0
            incomplete = 0
            last_restored = None
            while frame:
                got_trace = settings._old_trace.get(frame, None)
                if got_trace:
                    # print(f"RESETTING TRACE TO {got_trace}")
                    last_restored = got_trace
                    frame.f_trace = got_trace
                    complete += 1
                else:
                    incomplete += 1
                    # frame.f_trace = last_restored
                frame = frame.f_back
            # print(f"Restored {complete}/{len(settings._old_trace)}, tot {complete+incomplete}")
            # sys.settrace(last_restored)
            # sys.settrace(sys.gettrace())
        import logging
        log = logging.getLogger("hyperc")
        ret = None
        i = 0
        if metadata: metadata["plan_steps"] = []
        store_only = False
        store = False
        if "plan_exec" in metadata:
            if metadata.get("force_exec",False):
                store = True
            else:
                store_only = True
        for a in self.plan:
            i += 1
            log.debug(f"STEP {i} func ->{repr(a.function)}")
            if metadata:
                s_arguments = []
                for k, v in a.arguments.items():
                    arg_obj = {"name": k, "type": type(v).__name__, "dict": {}}
                    if v is None: continue
                    if not hasattr(v, "__annotations__"):
                        log.debug("No annotations for %s" % v)
                        continue
                    for attr, attrtype in v.__annotations__.items():
                        try:
                            arg_obj["dict"][attr] = getattr(v, attr)
                        except AttributeError:
                            log.debug("Can't extract annotated attrbute")
                    s_arguments.append(arg_obj)
                step = {"function": a.function.__name__, "arguments": s_arguments}
                metadata["plan_steps"].append(step)
            log.debug("arguments ->>{0}".format(a.arguments))
            if settings.DEBUG:
                for k, v in a.arguments.items():
                    if hasattr(v, "__class__") and hasattr(v.__class__, "__annotations__"):
                        try:
                            log.debug(f"Details for {k}: "+'; '.join([parn+":"+str(getattr(v, parn)) \
                                for parn,t in v.__class__.__annotations__.items()]))
                        except AttributeError:
                            log.debug(f"No attribute {k} {v} - can't fetch details")
            log.debug("kwargs ->>{0}".format(a.kwargs))
            if isinstance(a.function, types.MethodType):
                assert a.function.__self__ == a.arguments["self"], \
                    "Internal error: bound method must be solved with its bound class"
                assert "self" in a.arguments, "No 'self' in bound method supplied arguments"
                del a.arguments["self"]

            generators = defaultdict(list)
            # generators_len = 0

            for par, prox_and_obj in sorted(list(a.objects.items()), key=lambda x: int(str(x[0]).split("-")[-1])):
                if prox_and_obj[0]._self_instantiated:
                    generators[type(prox_and_obj[1])].append(prox_and_obj[1])
                    # generators_len += 1
            gens_unpacked = 0
            if generators:
                # TODO: support for class methods???
                fun_globals = a.function.__globals__.copy()
                # upd_globals = {}
                for k, v in fun_globals.items():
                    if isinstance(v, collections.abc.Hashable) and v in generators:
                        fun_globals[k] = get_instantiator(v, generators[v], InstCount())
                        gens_unpacked += 1
                # assert gens_unpacked == generators_len, \
                    # f"Internal: inconsistency in amount of instantiations {gens_unpacked} != {generators_len}"
                assert gens_unpacked == len(generators), \
                    f"Internal: inconsistency in amount of instantiations {gens_unpacked} != {len(generators)}"
                new_f = types.FunctionType(
                    a.function.__code__,
                    fun_globals,
                    name=a.function.__name__,
                    argdefs=a.function.__defaults__,  # ?? defaults?
                    closure=a.function.__closure__  # FIXME: closure must also be checked for params!!
                )
                
                if store_only:
                    metadata["plan_exec"].append((new_f, a.arguments))
                elif store:
                    metadata["plan_exec"].append((new_f, a.arguments))
                    ret = new_f(**a.arguments)
                    # now check if any global ids have changed
                    for old_g, new_g in zip(list(a.function.__globals__.items()), list(fun_globals.items())):
                        if old_g[1] is not new_g[1]:
                            if isinstance(old_g[1], collections.abc.Hashable) and old_g[1] in generators:
                                continue
                            a.function.__globals__[old_g[0]] = new_g[1]
                else:
                    ret = new_f(**a.arguments)
                    # now check if any global ids have changed
                    for old_g, new_g in zip(list(a.function.__globals__.items()), list(fun_globals.items())):
                        if old_g[1] is not new_g[1]:
                            if isinstance(old_g[1], collections.abc.Hashable) and old_g[1] in generators:
                                continue
                            a.function.__globals__[old_g[0]] = new_g[1]

            else:
                if store_only:
                    metadata["plan_exec"].append((a.function, a.arguments))
                elif store:
                    metadata["plan_exec"].append((a.function, a.arguments))
                    ret = a.function(**a.arguments)
                else:
                    ret = a.function(**a.arguments)
            # log.debug(f"Executing {a.function} -> {ret}")
        # log.debug(f"Plan of length {len(self.plan)} execution finished, returning {ret}")
        return ret


