from .poc_symex import solve, HCProxy, HCShadowProxy
from .exceptions import SchedulingError, SchedulingTimeout
from .util import side_effect_decorator


def side_effect(lmbda):
    lmbda()

def ensure_ne(a, b):
    "ensure that a never eaquals b"
    pass

def hint_exact(*args):
    """hint about some variables possible states
    Usage: hint_exact(v1, v2, ..., [list of tuples for variable-bindings])
    """
    pass


def hasattr(obj, attrname):
    if isinstance(obj, HCProxy) or isinstance(obj, HCShadowProxy):
        placeid = obj._self_root._self_mcdc_vals.get_place_id()
        if "assert not hasattr(" in placeid:
            obj._self_add_action('op_not_hasattr', ((obj, attrname), placeid))
            return False
        else:
            obj._self_add_action('op_hasattr', ((obj, attrname), placeid))
            return True


def not_hasattr(obj, attrname):
    # Will be called directly, not with globals
    return True  # Ignored when executed in symbolic execution phase


def delattr(obj, attrname):
    if isinstance(obj, HCProxy) or isinstance(obj, HCShadowProxy):
        obj._self_add_action('op_delattr', ((obj, attrname), obj._self_root._self_mcdc_vals.get_place_id()))