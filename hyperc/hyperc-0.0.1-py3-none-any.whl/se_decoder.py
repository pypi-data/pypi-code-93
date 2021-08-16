import types
import hyperc.poc_symex as hc
import hyperc.pddl as pddl
import hyperc.util

import copy
import itertools
from collections.abc import Set
from collections import defaultdict

import logging
log = logging.getLogger("hyperc")


class ObjectIdCollection:
    _c: dict
    def __init__(self):
        self._c = {}
    def add(self, obj):
        self._c[id(obj)] = obj
    def extend(self, other):
        self._c.update(other._c)
    def __contains__(self, obj):
        return id(obj) in self._c
    def __iter__(self):
        return iter(self._c.values())
    def __str__(self):
        return str(self._c)
    def __repr__(self):
        return f"<ObjectIdCollection [{self._c.keys()}]>"


class SEDecoder:
    """
    This class decodes Symbolic Execution plans into OAS
    """

    def __init__(self, func, schema, orig_kwargs, attrs_init, session_func_copies, goal):
        self.f = func
        self.actions = []
        self.attrs_init = attrs_init
        self.orig_kwargs = {k: self.resolve_linked(v) for k,v in orig_kwargs.items()}
        act = pddl.Action(name="", function=func, kwargs=self.orig_kwargs, session_func_copies=session_func_copies)
        act.name = f"{func.__name__}-{hyperc.util.h_id(func)}-{act.get_copy_id()}"
        self.actions.append(act)
        self.instantiations = set()  # Placeholder for instantiation classes
        self.classes = set()  # All classes ever referenced
        self.predicate_declarations = set()
        self.globals_facts = set()
        self.referenced_set_objects = ObjectIdCollection()
        self.module_names_used = defaultdict(set)
        self.lost_objects = []  # Hold the objects that were lost due to cancelled effects. Will have globlas.
        self.global_objects = []  # All "module" objects that are ever used
        log.debug(f"RWB>>> -------------------------- {func.__name__} ------------------------------")
        # print(f"RWB>>> -------------------------- {func.__name__} ------------------------------")
        self.true = hc.resolve_proxy(None, True)
        self.absurd = False
        for a in schema:
            if self.absurd:
                self.actions = []
                break
            getattr(self, a[0])(*a[1:])
        # if goal is method we should filter corresponding self value
        if hasattr(goal, '__self__') and (func in goal.__self__.__class__.__dict__.values()):
            self_args = None
            for arg_ar in schema:
                for arg in arg_ar:
                    if getattr(arg, "_self_name", None) == 'self':
                        self_args = arg
                        break
            assert self_args is not None, "self(instance) for Goal method not found"
            self_instance = hc.HCProxy(wrapped=goal.__self__, parent=None,
                                    name=str(goal.__self__), place_id="__STATIC")
            self.append_branch([
                [[
                    pddl.Predicate(fact="=", vars=[self_args, self_instance])
                ],
                [
                    pddl.Predicate(name='MagicGoal', fact='MagicGoal')
                ]],
                [[],[]]
            ])
        elif func is goal:
            #TODO should be append_branch for instance method_class
            self.append_all(
                preconditions=[],
                effects=[
                    pddl.Predicate(name='MagicGoal', fact='MagicGoal')
                ]
            )

    def get_actions(self):
        "Gets actions and 'seals' proxies so they now look as strings"
        new_globals = []
        for act in self.actions:
            for predicate in itertools.chain(act.precondition, act.effect):
                linked_vars = predicate.vars.copy()
                for v in predicate.vars:
                    for lv in v._self_equal.values():
                        # also continue for all linked variables to check if any of them is module-related
                        linked_vars.append(lv)
                for v in linked_vars:
                    v._self_seal()  # To make compatible with OAS interface
                    self.classes.add(v._self_class)
                    if v._self_wrapped is not None: 
                        self.global_objects.append(v)
                        if v._self_class == set:
                            self.referenced_set_objects.add(v._self_wrapped)
                    if v._self_container: # TODO: not all variables will have container?? FIXME
                        log.debug("Checking pass:{0}".format(v))
                        found = False
                        for ob in new_globals:
                            if id(ob) == id(v): found = True
                        if found: continue
                        new_globals.append(v)
                        log.debug("Checking pass: {0} Asdded".format(v))
                        # Do not inject selector from global value if it is present (as it may be negated explicitly)
                        found = False
                        for p in act.precondition:
                            if p.vars[0]._self_id() == v._self_container._self_id() \
                                and p.vars[1]._self_id() == v._self_id():
                                found = True
                        if found:
                            log.debug("Not injecting")
                        else:
                            log.debug(f"INJECTING GET FOR {v._self_id()}")
                            self.op_getattr(v._self_container, v._self_name, v)  # So far works for goals only..
        log.debug("LOST {0}".format(self.lost_objects))
        for v in new_globals + list(self.lost_objects):
            if not v._self_container: continue  # re-check for lost objects 
            v._self_container._self_seal()
            if v._self_container._self_class == types.ModuleType:
                self.module_names_used[v._self_container._self_name].add(v._self_name)
            if v._self_wrapped is not None: 
                if not v in self.global_objects: 
                    self.global_objects.append(v)
            v._self_seal()
            log.debug("adding global {0} {1}".format(v._self_name, v))
            glob_cur_value = v._self_container._self_getattribute(v._self_name)
            glob_cur_value._self_seal()
            log.debug("WOULD BE Adding to globals {0}".format(pddl.Predicate(
                name=f'{v._self_name}', vars=[v._self_container, glob_cur_value])))
            
            if glob_cur_value._self_real_value: 
                pass
            elif glob_cur_value._self_wrapped is None and v._self_wrapped is not None:
                # Means it has been rewritten in globals but we were able to recover it
                glob_cur_value = v
            else:
                # This path is for getting global preconditions
                log.debug(f"Does not have wrapped:{v._self_name}")
                continue
            if glob_cur_value._self_wrapped is not None and not glob_cur_value in self.global_objects:
                # FIXME: this may not be needed
                self.global_objects.append(glob_cur_value)
            glob_cur_value = glob_cur_value._self_get_real_object()
            glob_cur_value._self_seal()
            if glob_cur_value._self_wrapped is not None and not glob_cur_value in self.global_objects:
                # FIXME: this may not be needed
                self.global_objects.append(glob_cur_value)
            log.debug("Adding to globals {0}".format(pddl.Predicate(name=f"{v._self_name}", vars=[v._self_container, glob_cur_value])))
            self.globals_facts.add(pddl.Predicate(name=f"{v._self_name}", vars=[v._self_container, glob_cur_value]))
            self.classes.add(v._self_class)
            self.classes.add(v._self_container._self_class)
        for act in self.actions:
            for predicate in itertools.chain(act.precondition, act.effect):
                self.predicate_declarations.add(predicate.get_signature())
            # Now deduplicate. Probably needed due to Py's global dicts-object inconsistency handling
            p_cache = set()
            new_precond = []
            new_effect = []
            for predicate in act.precondition:
                pred_str = str(predicate)
                if not pred_str in p_cache: 
                    p_cache.add(pred_str)
                    new_precond.append(predicate)
            p_cache = set()
            for predicate in act.effect:
                pred_str = str(predicate)
                if not pred_str in p_cache: 
                    p_cache.add(pred_str)
                    new_effect.append(predicate)
            act.precondition = new_precond
            act.effect = new_effect
        return self.actions

    def was_set_different(self, hc_obj, name):
        "Returns True if setter was called for this class and property with a different object"
        prop_name = f"{hc_obj._self_class_id()}-{name}"
        # print("RWB>>> WILL CHECK", prop_name, "WITH", self.set_events)
        if prop_name in self.set_events:
            for obj in self.set_events[prop_name]:
                if obj._self_id() != hc_obj._self_id():
                    # print("RWB>>>     WAS !!! SET DIFFERENT", hc_obj._self_id(), name, "before:", obj._self_id())
                    return True
        # print("RWB>>>    WAS NOT SET DIFFERENT", hc_obj._self_id(), name)
        return False
    
    def get_values_of(self, class_, name, selfobj):
        # TODO: do we return our own set values?? obviously not!
        clsid = hyperc.util.class_id(class_)
        pname = f"{clsid}-{name}"
        ret = {}
        # print("RWB>>> attr_set_values[", pname, "] =", self.attr_set_values.get(pname))
        for dat in self.attr_set_values[pname]:
            if dat[0]._self_id() != selfobj._self_id():
                ret[dat[0]._self_id()] = dat
        return ret.values() 
    
    def get_instantiations_classes(self):
        return self.instantiations

    def get_all_classes(self):
        return self.classes
    
    def get_predicate_declarations(self):
        return self.predicate_declarations
    
    def get_global_facts(self):
        return self.globals_facts
    
    def extend_action(self, act: pddl.Action, pre, eff):
        act.precondition.extend(pre)
        act.effect.extend(eff)

    def append_all(self, preconditions, effects):
        "Append preconditions and effects to all actions"
        for p in preconditions:
            log.debug(f"Appending PRE: {p}")
        for e in effects:
            log.debug(f"Appending EFF: {e}")
        for act in self.actions:
            self.extend_action(act, preconditions, effects)

    def append_branch(self, pre_eff: list, replacements=None):
        "Append and create branches for all current actions"
        log.debug(f"Appending branched: {pre_eff}")
        new_actions = []
        for act in self.actions:
            i = 0
            for pre, eff in pre_eff:
                new_act = copy.deepcopy(act)
                if replacements:
                    new_act.replacements.update(replacements[i])
                # print("RWB>>> New replacements after branching", [(r[0], r[1][-1]._self_id()) for r in act.replacements.items()], "->" ,[(r[0], r[1][-1]._self_id()) for r in new_act.replacements.items()])
                self.extend_action(new_act, pre, eff)
                new_actions.append(new_act)
                # print("new actiona", len(new_actions), act.name)
                i += 1
        self.actions = new_actions

    def resolve_linked(self, hcp):
        "Return the variable that this is equal to, instead of this variable"
        # Globals will still be resolved as we're scanning all _self_equal links list!
        if hcp._self_equal:
            return min(hcp._self_equal.items(), key=lambda x: x[0])[1]
        else:
            return hcp

    def op_instantiate(self, func_obj, new_obj: "hc.HCProxy"):
        "Object instantiation: select an object from 'free' objects that need to be generated"
        next_free = hc.HCProxy(None, None, place_id="__STATIC", class_=new_obj._self_class, name="is-free-next")
        self.append_all(
            preconditions=[
                pddl.Predicate(name="hcsystem-is-free-next", vars=[new_obj, next_free]),
                pddl.Predicate(name="hcsystem-is-free-current", vars=[new_obj, self.true]),
                pddl.Predicate(name="hcsystem-is-free", vars=[new_obj, self.true])
            ],
            effects=[
                pddl.Predicate(name="hcsystem-is-free-current", vars=[new_obj, self.true], negated=True),
                pddl.Predicate(name="hcsystem-is-free-current", vars=[next_free, self.true]),
                pddl.Predicate(name="hcsystem-is-free", vars=[new_obj, self.true], negated=True)
            ]
        )
        self.instantiations.add(new_obj._self_class)
        new_obj._self_instantiated = True   # TODO: HCProxy / HCShadowProxy??
    
    def op_getattr(self, hcp_place: "hc.HCProxy", name: str, hcp_value: "hc.HCProxy", negated=False):
        if negated: log.debug(">>>>>>>>>>>>>>>>>> Negated getattr!!")
        log.debug("Rendered getattr: %s" % pddl.Predicate(name=f'{name}', vars=[hcp_place, hcp_value], negated=negated))
        self.append_all(
            preconditions=[pddl.Predicate(name=f'{name}', vars=[hcp_place, hcp_value], negated=negated)],
            effects=[]
        )
    
    def op_setattr(self, hcp_place: "hc.HCProxy", name: str, hcp_value: "hc.HCProxy", prev: "hc.HCProxy"):
        if prev:
            log.debug("OP SETATT EXEC {0}".format(prev._self_id()))
        # if hcp_place._self_wrapped and prev:
        #     log.debug("A")
        #     # This only happens for global objects...
        #     # FIXME Just because there is not current way to delete a value in global.
        #     # This optimization will not work if we support del keyword on globals
        #     self.append_all(
        #         preconditions=[pddl.Predicate(f"{hcp_place._self_class_id()}-{name}", [hcp_place, prev])],
        #         effects=[
        #             Predicate(f"{hcp_place._self_class_id()}-{name}", [hcp_place, prev], negated=True),
        #             Predicate(f"{hcp_place._self_class_id()}-{name}", [hcp_place, hcp_value])
        #         ]
        #     )
        if hcp_place._self_wrapped is not None and not prev:
            log.debug(f"B for {hcp_place._self_name}")
            # This only happens for special case of a "GOAL" object that is injected for PDDL
            self.append_all(
                preconditions=[],
                effects=[
                    pddl.Predicate(name=f'{name}', vars=[hcp_place, hcp_value])
                ]
            )
        elif (prev and 
              not hcp_place._self_instantiated_se and 
              (hcp_place._self_class not in self.attrs_init or name not in self.attrs_init[hcp_place._self_class])):
            log.debug("C")
            # TODO : there is another option: we KNOW there is a value becase we had an EQ before
            # TODO : we know there is NO value because we selected same object before with NO value (or at least same)
            self.append_branch([
                    [
                        [
                            pddl.Predicate(name=f'{name}', vars=[hcp_place, prev])
                        ],
                        [
                            pddl.Predicate(name=f'{name}', vars=[hcp_place, prev], negated=True),
                            pddl.Predicate(name=f'{name}', vars=[hcp_place, hcp_value])
                        ]
                    ],
                    [
                        [
                            pddl.Predicate(name=f"{name}-novalue", vars=[hcp_place, self.true], is_novalue_fact=True)
                        ],
                        [
                            pddl.Predicate(
                                name=f"{name}-novalue", vars=[hcp_place, self.true],
                                negated=True, is_novalue_fact=True),  # todo is_value_fact=True
                            pddl.Predicate(name=f'{name}', vars=[hcp_place, hcp_value])
                        ]
                    ]
            ])
        elif (prev and 
                not hcp_place._self_instantiated_se and 
                     hcp_place._self_class in self.attrs_init and name in self.attrs_init[hcp_place._self_class]):
            # We know exactly that the attribute is NOT empty
            self.append_all(
                preconditions=[
                    pddl.Predicate(name=f'{name}', vars=[hcp_place, prev])
                ],
                effects=[
                    pddl.Predicate(name=f'{name}', vars=[hcp_place, prev], negated=True),
                    pddl.Predicate(name=f'{name}', vars=[hcp_place, hcp_value])
                ]
            )
        else:
            log.debug("D: __init__ section")
            # This branch is for __init__ only: we know exactly that the class is "empty"
            self.append_all(
                preconditions=[],
                effects=[
                    pddl.Predicate(name=f'{name}', vars=[hcp_place, hcp_value])
                ]
            )
    
    def op_eq(self, hcp_what: "hc.HCProxy", hcp_other: "hc.HCProxy"): # should be optimized-out where possible
        if hcp_what._self_id() == hcp_other._self_id():
            log.debug("WARNING! absurd eq Should never happen")
            return
        # write like this but hcp_other shoulf be argument with name "self"
        self.append_all(
            preconditions=[pddl.Predicate(fact="=", vars=[hcp_what, hcp_other])],
            effects=[]
        )

    def op_neq(self, hcp_what: "hc.HCProxy", hcp_other: "hc.HCProxy"): # should be optimized-out where possible
        if hcp_what._self_id() == hcp_other._self_id():
            log.debug("WARNING! absurd neq Should never happen")
            self.absurd = True
            return
        self.append_all(
            preconditions=[pddl.Predicate(fact="=", vars=[hcp_what, hcp_other], negated=True)],
            effects=[]
        )
    
    def op_set_add(self, hcp_place, hcp_value):
        self.append_all(
            preconditions=[],
            effects=[
                pddl.Predicate(name="elements", vars=[hcp_place, hcp_value], element=True)
            ]
        )

    def op_set_remove(self, hcp_place, hcp_value):
        self.append_all(
            preconditions=[pddl.Predicate(name="elements", vars=[hcp_place, hcp_value], element=True)],
            effects=[
                pddl.Predicate(name="elements", vars=[hcp_place, hcp_value], element=True, negated=True)
            ]
        )
    
    def op_ensure_neq(self, *args, **kwargs):
        pass

    def op_hasattr(self, me, args, pos):
        obj = args[0]
        name = args[1]
        assert isinstance(obj, hc.HCProxy) or isinstance(obj, hc.HCShadowProxy)
        assert isinstance(name, str)
        attr_class = obj._self_class.__annotations__[name]
        random_placeholder = hc.HCProxy(None, None, "__STATIC", class_=attr_class, name=name)
        self.append_all(
            preconditions=[
                pddl.Predicate(name=f'{name}', vars=[obj, random_placeholder])
            ],
            effects=[]
        )
        
    def op_not_hasattr(self, me, args, pos):
        obj = args[0]
        name = args[1]
        assert isinstance(obj, hc.HCProxy) or isinstance(obj, hc.HCShadowProxy)
        assert isinstance(name, str)
        self.append_all(
            preconditions=[
                pddl.Predicate(name=f"{name}-novalue", vars=[obj, self.true], 
                               is_novalue_fact=True, is_hasattr=True)
            ],
            effects=[ ]
        )

    def op_delattr(self, me, args, pos):
        obj = args[0]
        name = args[1]
        assert isinstance(obj, hc.HCProxy) or isinstance(obj, hc.HCShadowProxy)
        assert isinstance(name, str)
        attr_class = obj._self_class.__annotations__[name]
        random_placeholder = hc.HCProxy(None, None, "__STATIC", class_=attr_class, name=name)
        self.append_all(
            preconditions=[
                pddl.Predicate(name=f'{name}', vars=[obj, random_placeholder])
            ],
            effects=[ 
                pddl.Predicate(name=f"{name}", vars=[obj, random_placeholder], negated=True),
                pddl.Predicate(name=f"{name}-novalue", vars=[obj, self.true], is_novalue_fact=True)
            ]
        )

    def op_hint_exact(self, *args, **kwargs):
        # print("HINT EXACT", args)
        placeid = str(hyperc.util.stable_int_hash(args[2]))
        args = args[1]
        hint_objects = args[-1]()
        # print("HINT OBJECTS", hint_objects)
        if hint_objects is None or len(hint_objects) == 0:
            return
        args = args[:-1]
        eq_pairs = []
        # generate a predicate with signature
        # (hint-<actionname>-<obj1class-obj2class-...> ?obj1 ?obj2 ?obj3...)
        proxy_classes_string = "-".join([x._self_class_id() for x in args])
        hint_pred_name = f"hint-{self.f.__name__}-{proxy_classes_string}-{placeid}"
        hint_pred_vars = " ".join([f"?v{x} - {v._self_class_id()}" for x, v in enumerate(args)])
        hint_pred_sig = f"({hint_pred_name} {hint_pred_vars})"

        proxy_vars_string = " ".join([x._self_id() for x in args])
        precondition = pddl.CustomPredicate(
            full_text=f"({hint_pred_name} {proxy_vars_string})",
            signature=hint_pred_sig
        )
        self.append_all(
            preconditions=[precondition],
            effects=[]
        )

        for objects_set in hint_objects:
            objects_set_proxied = [hc.resolve_proxy(None, x) for x in objects_set]
            obj_classes_string = "-".join([x._self_class_id() for x in objects_set_proxied])
            assert obj_classes_string == proxy_classes_string, \
                f"Hints types of paramter-object mismatch: {proxy_classes_string} != {obj_classes_string}"
            obj_values_string = " ".join([x._self_id() for x in objects_set_proxied])
            self.globals_facts.add(pddl.CustomPredicate(
                full_text=f"({hint_pred_name} {obj_values_string})",
                signature=hint_pred_sig
            ))
    
    def op_none(self, *args, **kwargs):
        log.debug("Dropped op %s" % repr(args))
        for v in args:
            if isinstance(v, hc.HCProxy):
                self.lost_objects.append(v)


