"""
Functions for serializing Python functions.

The only known areas where we will fail to serialize something usable are:

user imports like import foo.bar.baz instead of from foo.bar import baz
are not detected properly by the underlying library we use for looking up
dependencies. import json or other top-level modeuls still works just fine,
its just when you include multiple path components that we don't detect the
dependency properly

references to instantiated non-builtin types with a repr that can't be exec'd

users referring to a renamed version of an imported module has some wonky
behavior, for example `import json` then `foo=json` then referring to
`foo` in the func to be serialized.
"""
import inspect
from collections import defaultdict
from types import FunctionType
from types import ModuleType

from dill.detect import freevars
from dill.detect import globalvars
from pyspark.sql import types as spark_types

from tecton_proto.args.user_defined_function_pb2 import UserDefinedFunction
from tecton_spark.logger import get_logger
from tecton_spark.materialization_common import MaterializationContext
from tecton_spark.materialization_context import UnboundMaterializationContext
from tecton_spark.time_utils import WINDOW_UNBOUNDED_PRECEDING
from tecton_spark.udfs import tecton_sliding_window_udf

logger = get_logger("function_serialization")


def to_proto(transform, return_type=str):
    code = transform._code if hasattr(transform, "_code") else _getsource(transform)
    _validate_code(code)

    proto = UserDefinedFunction()
    proto.name = transform.__name__
    proto.body = code
    proto.return_type = return_type.__name__

    return proto


BANNED_INDIRECT_IMPORTS = ["materialization_context", "tecton_sliding_window_udf", "WINDOW_UNBOUNDED_PRECEDING"]


def _validate_code(code):
    for banned_import in BANNED_INDIRECT_IMPORTS:
        if f"tecton.{banned_import}" in code:
            raise Exception(
                f"Cannot serialize `tecton.{banned_import}`. Please use an import like `from tecton import {banned_import}`"
            )


def _getsource(func):
    imports = defaultdict(set)
    modules = set()
    code_lines = []
    seen_args = {}

    def process_functiontype(name, obj, imports, modules, code_lines, seen_args):
        # if this is user-defined or otherwise unavailable to import at deserialization time
        # including anything without a module, with module of __main__, defined as @inlined method,
        # or anything with a qualified name containing characters invalid for an import path, like foo.<locals>.bar
        if obj.__module__ in ("__main__", None) or getattr(obj, "_inlined", False) or "<" in obj.__qualname__:
            objs = globalvars(obj, recurse=False)
            objs.update(freevars(obj))
            default_objs = {}
            for param in inspect.signature(obj).parameters.values():
                if param.default != inspect.Parameter.empty:
                    default_objs[param.name] = param.default
                    # these defaults shadow over obj
                    objs.pop(param.name, None)
            # need to sort the keys since globalvars ordering is non-deterministic
            for dependency, dep_obj in sorted(objs.items()):
                recurse(dependency, dep_obj, imports, modules, code_lines, seen_args, write_codelines=True)
            for dependency, dep_obj in sorted(default_objs.items()):
                # we dont re-write defaults at top-level since the `def` lines should have the declarations
                recurse(dependency, dep_obj, imports, modules, code_lines, seen_args, write_codelines=False)
            fdef = inspect.getsource(obj)
            fdef = fdef[fdef.find("def ") :]
            code_lines.append(fdef)
        else:
            imports[obj.__module__].add(obj.__name__)

    def recurse(name, obj, imports, modules, code_lines, seen_args, write_codelines):
        def _add_codeline(line):
            if write_codelines:
                code_lines.append(line)

        # prevent processing same dependency object multiple times, even if
        # multiple dependent objects exist in the tree from the original
        # func
        seen_key = str(name) + str(obj)
        if seen_args.get(seen_key) is True:
            return
        seen_args[seen_key] = True

        # Confusingly classes are subtypes of 'type'; non-classes are not
        if isinstance(obj, type):
            if obj.__module__ == "__main__":
                raise Exception(f"Cannot serialize class {obj.__name__} from module __main__")
            imports[obj.__module__].add(obj.__name__)

        elif isinstance(obj, FunctionType):
            process_functiontype(name, obj, imports, modules, code_lines, seen_args)
        elif isinstance(obj, ModuleType):
            if f"{obj.__package__}.{name}" == obj.__name__:
                imports[obj.__package__].add(name)
            else:
                modules.add(obj.__name__)
        elif isinstance(obj, spark_types.StructType):
            _add_codeline(f"{name} = StructType.fromJson(json.loads('{obj.json()}'))")
            modules.add("json")
            imports["pyspark.sql.types"].add("StructType")
        elif isinstance(obj, UnboundMaterializationContext):
            imports["tecton_spark.materialization_context"].add("materialization_context")
        elif obj is tecton_sliding_window_udf:
            imports["tecton_spark.udfs"].add("tecton_sliding_window_udf")
        elif obj == WINDOW_UNBOUNDED_PRECEDING:
            imports["tecton_spark.time_utils"].add("WINDOW_UNBOUNDED_PRECEDING")
        elif isinstance(obj, MaterializationContext):
            raise Exception(
                "tecton.MaterializationContext() is not a valid value here. Did you mean "
                "tecton.materialization_context()?"
            )
        else:
            try:
                repr_str = f"{name}={repr(obj)}"
                exec(repr_str)
                _add_codeline(repr_str)
            except Exception:
                raise Exception(f"Cannot evaluate object {obj} of type '{type(obj)}' for serialization")

    recurse(func.__name__, func, imports, modules, code_lines, seen_args, write_codelines=True)

    for module in sorted(imports):
        import_line = f"from {module} import "
        import_line += ", ".join(sorted(imports[module]))
        code_lines.insert(0, import_line)

    for module in sorted(modules):
        code_lines.insert(0, f"import {module}")

    return "\n".join(code_lines)


def inlined(func):
    """Apply this decorator to a function to inline the serialization instead of importing it.
    :param func An function to be inlined instead of imported. The function should not have an external dependency that
                is not available in Spark driver and is not inlined (e.g. another non-inlined function in a test module)
    A common use case is during testing, in which case you can't import the test file in Spark driver.

    Example 1: How not using @inline decorator can break Spark driver
        test_foo.py:
            def double_func(a):
                return 2 * a

        main.py:
            import test_foo
            to_proto(test_foo.bar).body -> "from test_foo import bar"
                # this breaks because test_foo can't be imported in Spark driver

    Example 2: How using @inline decorator can fix Spark driver
        test_foo.py:
            @inline
            def double_func(a):
                return 2 * a

        main.py:
            import test_foo
            to_proto(test_foo.bar).body -> "def double_func(a):\n    return 2 * a"
                # this works because test_foo isn't being imported anymore and double_func is inlined

    Example 3: How mis-using @inline decorator can break Spark driver
        test_foo.py:
            def _internal_double_func(a):
                return 2 * a

            @inline
            def double_func(a):
                return _internal_double_func(a)

        main.py:
            import test_foo
            to_proto(test_foo.bar).body ->
                > from test_foo import _internal_double_func
                > def double_func(a):
                >     return _internal_double_func(a)
                # this breaks because test_foo can't be imported in Spark driver

    Example 4: How to fix example 3 (add @inline decorator to all dependencies)
        test_foo.py:
            @inline
            def _internal_double_func(a):
                return 2 * a

            @inline
            def double_func(a):
                return _internal_double_func(a)

        main.py:
            import test_foo
            to_proto(test_foo.bar).body ->
                > def _internal_double_func(a):
                >     return 2 * a
                >
                > def double_func(a):
                >     return _internal_double_func(a)
                # this works because test_foo isn't being imported anymore and both functions are inlined
    """
    setattr(func, "_inlined", True)
    return func


def from_proto(serialized_transform: UserDefinedFunction, scope=None):
    """
    deserialize into global scope by default. if a scope if provided, deserialize into provided scope
    """

    if scope is None:
        # PySpark has issues if the UDFs are not in global scope
        scope = __import__("__main__").__dict__

    assert serialized_transform.HasField("body") and serialized_transform.HasField(
        "name"
    ), "Invalid UserDefinedFunction."

    exec(serialized_transform.body, scope)

    # Return function pointer
    try:
        fn = eval(serialized_transform.name, scope)
        fn._code = serialized_transform.body
        return fn
    except Exception as e:
        raise ValueError("Invalid transform") from e
