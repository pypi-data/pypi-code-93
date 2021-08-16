import collections
import datetime
import inspect
import logging
import typing

import attr
import coloring
from koalak.consts import PACKAGE_NAME
from koalak.decorators import optionalargs

logger = logging.getLogger("koala")
logger.setLevel(logging.DEBUG)

try:
    typping_ForwardRef = typing.ForwardRef
except AttributeError:
    typping_ForwardRef = typing._ForwardRef  # noqa


"""
RelationalDB is a wrapper for sqlalchemy and attr to have
a relational database with a better API and abstraction
- no ID
- specify relations with annoation (List["Animal"], Animal, ...)
- use attr to create __init__, __repr__, ...
See examples in test_relationaldb.py



"""


@attr.s
class BuildingRelationalAttribute:
    """Helper cls to build relational attribute"""

    name: str = attr.ib()
    many: bool = attr.ib(default=None)
    atomic_type_name: str = attr.ib(
        default=None
    )  # type of the referenced table (without the List)
    referenced_by: "BuildingRelationalAttribute" = attr.ib(default=None)
    attr_attribute = attr.ib(default=None)

    # this attribute is set to True by the class that contain this
    #  attribute, sins it is possible for an other class to create
    #  an attribute with ref (having exist=True we are sure that
    #  the attribute exist and it's not just a reference)
    exist = attr.ib(default=None)

    def __attrs_post_init__(self):
        if self.name == "age":
            coloring.print_bred("AGE IS BUILT")
            print(self)

    def update(
        self,
        *,
        many=None,
        atomic_type_name=None,
        referenced_by=None,
        attr_attribute=None,
        exist=None,
    ):
        for varname in [
            "exist",
            "many",
            "atomic_type_name",
            "referenced_by",
            "attr_attribute",
        ]:
            var = locals()[varname]
            if var is not None:
                attr = getattr(self, varname)
                if attr is not None:
                    # attr not None and var not None! they must be the same
                    if var is not attr:
                        raise ValueError(
                            f"Trying to update {varname} but it's already set to {attr} "
                        )
                else:
                    setattr(self, varname, var)


@attr.s
class BuildingClass:
    """Helper class to postpone building the ORM classes"""

    name: str = attr.ib()
    cls = attr.ib(default=None, init=False)
    table_name: str = attr.ib(default=None, init=False)
    attributes: typing.Dict[str, BuildingRelationalAttribute] = attr.ib(
        factory=dict, init=False
    )
    orm_cls = attr.ib(default=None, init=False)
    # this attribute is set to True by the class that contain this
    #  attribute, sins it is possible for an other class to create
    #  an attribute with ref (having exist=True we are sure that
    #  the attribute exist and it's not just a reference)
    exist = attr.ib(default=None)

    def update(self, *, cls=None, table_name=None, orm_cls=None, exist=None):
        for varname in ["cls", "table_name", "orm_cls", "exist"]:
            var = locals()[varname]
            if var is not None:
                attr = getattr(self, varname)
                if attr is not None:
                    # attr not None and var not None! they must be the same
                    if var is not attr:
                        raise ValueError(
                            f"Trying to update {varname} but it's already set to {attr} "
                        )
                else:
                    setattr(self, varname, var)

    def get_or_create_attribute(
        self, attribute_name: str
    ) -> BuildingRelationalAttribute:
        if attribute_name in self.attributes:
            return self.attributes[attribute_name]
        else:
            attribute = BuildingRelationalAttribute(attribute_name)
            self.attributes[attribute_name] = attribute
            return attribute


@attr.s
class AttributeMetadata:
    """Additional metadata to attr (use sqlalchemy attributes and RelatinalDB attributes)"""

    unique: bool = attr.ib(default=None, kw_only=True)


@attr.s
class AttrMetadata:
    """Metadata used in attr.ib(metadata=...) that hold extra information about DB"""

    name: str = attr.ib(default=None)
    unique: bool = attr.ib(default=None)
    many: bool = attr.ib(default=None)
    atomic_type_name: str = attr.ib(
        default=None
    )  # type of the referenced cls (without the List)
    atomic_type = attr.ib(default=None)
    ref: str = attr.ib(default=None)
    attr_attribute = attr.ib(default=None)
    exist = attr.ib(default=None)
    referenced_by: "AttrMetadata" = attr.ib(default=None)

    def __attrs_post_init__(self):
        if self.unique is None:
            self.unique = False

    def __getattr__(self, item):
        if item in ["type"]:
            return getattr(self.attr_attribute, item)
        return self.__getattribute__(item)

    def update(
        self,
        *,
        many: bool = None,
        atomic_type_name: str = None,
        atomic_type=None,
        referenced_by=None,
        attr_attribute=None,
        exist: bool = None,
        name: str = None,
        ref: str = None,
    ):
        for varname in [
            "exist",
            "many",
            "atomic_type_name",
            "atomic_type",
            "referenced_by",
            "attr_attribute",
            "name",
            "ref",
        ]:
            var = locals()[varname]
            if var is not None:
                attr = getattr(self, varname)
                if attr is not None:
                    # attr not None and var not None! they must be the same
                    if var is not attr:
                        raise ValueError(
                            f"Trying to update {varname} but it's already set to {attr} "
                        )
                else:
                    setattr(self, varname, var)


@attr.s
class ClsMetadata:
    """Helper class to postpone building the ORM classes"""

    name: str = attr.ib()
    cls = attr.ib(default=None, init=False)
    table_name: str = attr.ib(default=None, init=False)
    attributes: typing.Dict[str, AttrMetadata] = attr.ib(factory=dict, init=False)
    # this attribute is set to True by the class that contain this
    #  attribute, sins it is possible for an other class to create
    #  an attribute with ref (having exist=True we are sure that
    #  the attribute exist and it's not just a reference)
    exist = attr.ib(default=None)

    def __len__(self):
        return len(self.attributes)

    def __contains__(self, item):
        return self.attributes.__contains__(item)

    def __getitem__(self, item) -> AttrMetadata:
        return self.attributes.__getitem__(item)

    def update(self, *, cls=None, table_name=None, exist=None):
        for varname in ["cls", "table_name", "exist"]:
            var = locals()[varname]
            if var is not None:
                attr = getattr(self, varname)
                if attr is not None:
                    # attr not None and var not None! they must be the same
                    if var is not attr:
                        raise ValueError(
                            f"Trying to update {varname} but it's already set to {attr} "
                        )
                else:
                    setattr(self, varname, var)

    def get_or_create_attribute(self, attribute_name: str) -> AttrMetadata:
        if attribute_name in self.attributes:
            return self.attributes[attribute_name]
        else:
            attribute = AttrMetadata()
            attribute.update(name=attribute_name)
            self.attributes[attribute_name] = attribute
            return attribute


class DBMetadata:
    def __init__(self):
        self.classes = {}

    def register(self, cls):
        self.decorate_with_attr(cls)
        cls_metadata = self.get_or_create_cls_metadata(cls.__name__)
        cls_metadata.update(exist=True, cls=cls)

        attr_attributes = cls.__attrs_attrs__
        for attr_attribute in attr_attributes:
            self.register_attribute(cls_metadata, attr_attribute)

    def register_attribute(self, cls_metadata: ClsMetadata, attr_attribute):
        coloring.print_bgreen("Register attribute", attr_attribute.name)
        attribute_name = attr_attribute.name
        # Create the attribute if not exist
        attribute = cls_metadata.get_or_create_attribute(attribute_name)
        attribute.update(attr_attribute=attr_attribute)

        atomic_type = self.get_atomic_type(attr_attribute.type)
        if isinstance(atomic_type, str):
            atomic_type_name = atomic_type
        else:
            atomic_type_name = atomic_type.__name__

        metadata = attr_attribute.metadata[PACKAGE_NAME]
        attribute.update(
            exist=True,
            atomic_type_name=atomic_type_name,
            atomic_type=atomic_type,
            ref=metadata.ref,
        )

        # If the type of this attribute is an other class (string referencing it)
        #  register the class
        if isinstance(atomic_type, str):
            self.get_or_create_cls_metadata(atomic_type_name)

        # Handle ref - the attribute reference an other attribute
        if attribute.ref:
            # Check that type is not built-in
            #  it's not possible to reference builtin types like str
            if self.is_builtin(attribute.atomic_type):
                # TODO: test
                raise ValueError(
                    f"ref cannot reference built-in type {attribute.atomic_type!r}"
                )

            # Create the attribute if not exit
            ref_cls_metadata = self.get_or_create_cls_metadata(atomic_type_name)
            ref_attribute = ref_cls_metadata.get_or_create_attribute(attribute.ref)

            # Check if the attribute already exist
            if ref_cls_metadata.exist and not ref_attribute.exist:
                # if the class exist (already registered) the attribute must exist
                raise ValueError(
                    f"{cls_metadata.name}.{attribute.name} reference non existing attribute {attribute.name} in {attribute.atomic_type_name}"
                )

            # update attribute
            ref_attribute.update(
                referenced_by=attribute,
                atomic_type=cls_metadata.cls,
                atomic_type_name=cls_metadata.name,
            )

    def get_atomic_type(self, type):
        return type

    def handle_type(self, attribute: AttrMetadata, cls_metadata: ClsMetadata):
        """Get the atomic_type and 'many'"""
        type = attribute.type
        many = False
        if isinstance(type, str):
            atomic_type_name = type
            atomic_type = type
        elif isinstance(type, typing.GenericMeta):
            if type.__name__ == "List":
                many = True
                # check if List is empty (ex: List instead of List[Animal])
                if not attr_type.__args__:  # noqa
                    raise ValueError(
                        f"List annotation for {cls_metadata.name}.{attribute.name} can not be empty"
                    )
                attr_type = attr_type.__args__[0]  # noqa

                # Check if the argument of List is a string
                if isinstance(attr_type, typping_ForwardRef):
                    attr_type = attr_type.__forward_arg__
            else:
                raise ValueError(
                    f"Support only List annotation, don't support {attr_type}"
                )
        else:
            atomic_type_name = atomic_type.__name__

        # TODO: test when type is given as string

    def is_builtin(self, type):
        # FIXME: probably some bugs in this function (not exaustive?)
        return type in [str, int, float, bool]

    def decorate_with_attr(self, cls):
        if not hasattr(cls, "__attrs_attrs__"):
            attr.s(cls)

    def get_or_create_cls_metadata(self, cls_name: str) -> ClsMetadata:
        if cls_name in self.classes:
            return self.classes[cls_name]
        else:
            cls_metadata = ClsMetadata(cls_name)
            self.classes[cls_name] = cls_metadata
            return cls_metadata

    def __len__(self):
        return self.classes.__len__()

    def __contains__(self, item):
        return self.classes.__contains__(item)

    def __getitem__(self, item) -> ClsMetadata:
        return self.classes.__getitem__(item)


class BaseRelationalDB:
    def __init__(self):
        self.db_metadata = DBMetadata()

    @optionalargs
    def register(self, cls):
        self.db_metadata.register(cls)
        return cls

    def close(self):
        pass

    def sync(self):
        pass

    def attribute(
        self,
        # attrs attribute
        type=None,
        *,
        default=attr.NOTHING,
        validator=None,
        repr=True,
        cmp=None,
        hash=None,
        init=True,
        metadata=None,
        converter=None,
        factory=None,
        kw_only=False,
        eq=None,
        order=None,
        on_setattr=None,
        # sqlalchemy attribute
        unique=None,
        ref=None,
    ):

        metadata = self.metadata(unique=unique, ref=ref)
        return attr.ib(  # noqa
            default=default,
            validator=validator,
            repr=repr,
            cmp=cmp,
            hash=hash,
            init=init,
            metadata=metadata,
            type=type,
            converter=converter,
            factory=factory,
            kw_only=kw_only,
            eq=eq,
            order=order,
            on_setattr=on_setattr,
        )

    ib = attribute

    def metadata(self, unique=None, ref=None):
        metadata = AttrMetadata(unique=unique, ref=ref)
        return {PACKAGE_NAME: metadata}


class TestRelationalDB:
    def __init__(self, db_factory):
        self.db_factory = db_factory

    def test_api(self):
        db = self.db_factory()


class RelationalListMany(collections.UserList):
    def __init__(self, ref_attribute_name: str):
        # FIXME
        self.ref_attribute_name = ref_attribute_name

    def append(self, item: typing.T) -> None:
        self.data.append(item)
        ref_attribute = getattr(item, self.ref_attribute_name)
        ref_attribute.data.append(self)
