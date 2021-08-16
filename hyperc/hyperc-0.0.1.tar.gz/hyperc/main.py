import itertools
import types
import inspect
from collections import defaultdict
from copy import deepcopy

from hyperc.pddl import *

from hyperc.util import get_registry

PROBLEM_TPL = '''
(define (problem poodle-generated)
    (:domain poodle-generated)
    (:objects 
    {objects}
    )
    (:init
        {init}
    )
    (:goal 
        {goal}
    )
)
'''


def pddl_preconditon(heap):
    preconditon = list()
    for obj in heap:
        preconditon.extend(obj._self_preconditon())
    return preconditon


def pddl_effect(heap):
    effect = list()
    for obj in heap:
        for action in obj._self_actions:
            effect.extend(action.effect())
    return effect


def pddl_parameters(heap):
    parameters = list()
    for obj in heap:
        parameters.extend(obj._self_parameters())
    return parameters


def pddl_predicates(heap):
    predicates = set()
    for obj in heap:
        if not hasattr(obj.__class__, '__annotations__'):
            continue
        for a in obj.__class__.__annotations__.items():
            name, child_cls = a
            predicates.add(gen_predicate(obj, child_cls, name))
    return predicates


def gen_predicate(parent, child_cls, name):
    return PredicateDeclaration(f'{parent._self_cls()}-{name}', [Parameter(parent._self_var(), parent._self_cls()),
                                                                 Parameter(f'?{name}', child_cls.__name__)])


def pddl_init(heap):
    from hyperc.proxies import HypercProxyObject, HypercProxyClass
    inits = set()
    for name, obj in heap.items():
        if not hasattr(obj.__class__, '__annotations__'):
            continue
        for a in obj.__class__.__annotations__.items():
            attr_name, child_cls = a
            child_obj = getattr(obj, attr_name)
            child = HypercProxyObject(child_obj, attr_name)
            parent = HypercProxyObject(obj, name)
            inits.add(gen_init(parent, child, attr_name))
    return inits


def gen_init(parent, child, name):
    return f'({parent._self_cls()}-{name} {parent._self_obj()} {child._self_obj()})'


def pddl_objects():
    objects = {}
    for _, ob in get_registry().items():
        type = ob._self_cls()
        obj = ob._self_obj()
        if type in objects:
            objects[type].append(obj)
        else:
            objects[type] = ObjectDeclaration(type)
            objects[type].append(obj)
    return objects.values()


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def pddl_types():
    types_ = set()
    res_dict = defaultdict(set)
    for ob in set(get_registry().values()):
        for child, parent in pairwise(inspect.getmro(ob.__class__)):
            res_dict[parent.__name__].add(child.__name__)
    for parent, children in res_dict.items():
        types_.add('{children} - {parent}'.format(children=' '.join(children), parent=parent))
    return types_


def namespaced_function(function, global_dict, defaults=None, preserve_context=True):
    fun_globals = dict()
    if defaults is None:
        defaults = function.__defaults__
    if preserve_context:
        fun_globals = function.__globals__.copy()
    fun_globals.update(global_dict)
    new_namespaced_function = types.FunctionType(
        function.__code__,
        fun_globals,
        name=function.__name__,
        argdefs=defaults,
        closure=function.__closure__,
    )
    new_namespaced_function.__dict__.update(function.__dict__)
    new_namespaced_function.__annotations__ = function.__annotations__  # here we must catch not annotated
    return new_namespaced_function


def get_caller_locals():
    f = inspect.stack()[2].frame
    locals_ = dict()
    for k, v in f.f_globals.items():
        if getattr(v, '__module__', None) == f.f_globals['__name__']:
            locals_[k] = v
    return locals_


def affected_objects(fn):
    affeted = dict()
    for k, obj in fn.__globals__.items():
        if hasattr(obj, '_self_actions') and obj._self_actions:
            affeted[k] = obj
    return affeted


def proxify(heap):
    from hyperc.proxies import HypercProxyObject, HypercProxyClass
    run_ns = dict()
    objects = dict()
    functions = dict()
    proxy_objects = dict()
    for name, obj in heap.items():
        if name.startswith('_'):
            continue
        if isinstance(obj, type):
            run_ns[name] = HypercProxyClass(obj)
        elif callable(obj):
            functions[name] = obj
        else:
            proxy = HypercProxyObject(obj)
            run_ns[name] = proxy
            proxy_objects[name] = proxy
            objects[name] = obj

    ns_functions = dict()
    for fname, f in functions.items():
        fns = deepcopy(run_ns)
        ns_functions[fname] = namespaced_function(f, global_dict=fns)  # m will run in it's own namespace
        # except the heap objects and their classes would be proxies
    return run_ns, objects, proxy_objects, functions, ns_functions


def exec_plan(plan, calables):
    retval = None
    for line in plan:
        if line.startswith(';'):  # not interesting
            continue
        # fn_ns_classes = defaultdict(list)
        funcname, *nskeys = re.sub('[)(]', '', line).split(' ')
        func, *args = calables[funcname]
        # print(func, args)
        # hyperc_ids = [int(key.strip('\n')[-1]) for key in nskeys]
        # fn_ns = [_registry[key] for key in hyperc_ids]
        # for ob in fn_ns:
        #     fn_ns_classes[ob.__class__].append(ob)
        # args = [fn_ns_classes[k][0].__wrapped__ for k in
        #         func.__annotations__.values()]  # Needs fixing, global and argument spaces are messed up
        retval = func(*args)
    return retval
