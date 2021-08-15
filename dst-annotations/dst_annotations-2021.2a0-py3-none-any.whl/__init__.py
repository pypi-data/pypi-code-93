import pkg_resources

from ._annotations import (
    AnnotatedAlias,
    DataClassProto,
    Empty,
    ForwardRefProto,
    GenericAliasProto,
    NamedClassProto,
    NamedTupleProto,
    TypedDictProto,
    ValidDataClassProto,
    as_forward_ref,
    empty,
    register_named_class,
)
from ._inspect_annotations import get_runtime_types
from ._jsoncompatible import (
    JSONArray,
    JSONCompatible,
    JSONObject,
    JSONSchema,
    JSONSingle,
)

__version__ = pkg_resources.require(__name__)[0].version
