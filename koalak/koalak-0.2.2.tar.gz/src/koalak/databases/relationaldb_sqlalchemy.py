import collections
import datetime
import inspect
import logging
import typing

import attr
import coloring
import sqlalchemy
from koalak.consts import PACKAGE_NAME
from koalak.decorators import add_post_init, optionalargs
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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


class RelationalDB:
    # TODO: add a new engine which is dict in contrast to SQLalchemy
    # it will have the same API, but it will store the classes
    # in memory with list and dicts and don't use SQL
    # TODO: add bijection argument (for friends, to add the same line twice)
    # TODO: add List of strings List[str] => and add a table with a foreign key
    # TODO: use only annotation without db.attribute(): Ex: name: str  (like dataclass)
    # TODO: add the possibility ti use @db.table  and take the name cls.__name__
    # TODO: implement  lazy import
    _map_cls_to_sqlalchemy_types = {str: String, int: Integer, bool: Boolean}
    List = typing.List

    def __init__(self, uri: str = None, echo=None, autocommit=None):
        if uri is None:
            uri = ":memory:"

        if echo is None:
            echo = False

        if autocommit is None:
            autocommit = True

        self.uri = uri
        self.autocommit = autocommit

        # internal attributes
        self._map_cls_tablename = {}
        self._map_tablename_cls = {}
        self._map_clsname_tablename = {}

        # sqlalchemy attributes
        self.engine = create_engine(f"sqlite:///{uri}", echo=echo)
        self.Session = sessionmaker(bind=self.engine)
        self.Base = declarative_base()

        # dictionary to hold classes to build at init()
        self._building_class: typing.Dict[str, BuildingClass] = {}

    @property
    def query(self):
        return self.session.query

    @property
    def commit(self):
        return self.session.commit

    datetime_now = datetime.datetime.utcnow

    def metadata(self, unique=True, nullable=False, target=None, ref=None):
        return {
            "koala": {
                "unique": unique,
                "nullable": nullable,
                "target": target,
                "ref": ref,
            }
        }

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
        nullable=None,
        target=None,
        ref=None,
    ):

        # check integrity of arguments
        if not nullable and default is None:
            assert TypeError(
                f"An attribute can't be 'not nullable' and default is None in the same time"
            )
        # if default is None activate nullable to True by default
        if default is None and nullable is None:
            nullable = True

        if metadata is None:
            metadata = {}
        if nullable is None:
            nullable = False
        metadata.update(
            self.metadata(unique=unique, target=target, nullable=nullable, ref=ref)
        )
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

    def table(self, table_name):
        """Create new table
        How it works:
        - Decorate the cls with attr to create the used methods (__init__, __repr__, ...)
        - Hook the __init__ for autoadd
        - collect all needed information for relations (to add in init())
        - Create the sqlalchemy ORM cls that inherit from the original cls and the Base cls
         without the relations (relations will be added in init())
        - Return the ORM cls
        """

        def decorator(cls):
            """Register this class to build it when init() is called"""
            # check if cls name is unique
            cls_name = cls.__name__
            if cls_name in self._building_class:
                assert KeyError(f"Class {cls_name} already exist in the database")

            # ======================================= #
            # decorate cls with attr (if not already) #
            # ======================================= #
            if not hasattr(cls, "__attrs_attrs__"):
                cls = attr.s(cls)

            # ========================================== #
            # hook __init__ to add autocommit if enabled #
            # ========================================== #
            def postinit_autocommit(self_instance):
                if self.autocommit:
                    self.session.add(self_instance)
                    # self.session.commit()

            # add postinit_autocommit to the cls
            cls = add_post_init(postinit_autocommit)(cls)

            # register cls and it's attributes
            orm_cls = self._create_orm_cls_without_relations(cls, table_name)
            # building_cls = self._register_cls(cls, table_name)

            return orm_cls

        return decorator

    def _get_or_create_building_cls(self, cls_name: str) -> BuildingClass:
        if cls_name in self._building_class:
            return self._building_class[cls_name]
        else:
            building_cls = BuildingClass(cls_name)
            self._building_class[cls_name] = building_cls
            return building_cls

    def _create_orm_cls_without_relations(self, cls, table_name):
        """Create the ORM cls without relations. Relations will be added at init()"""

        cls_name = cls.__name__

        # get the building_class for this class
        building_cls = self._get_or_create_building_cls(cls_name)
        building_cls.update(cls=cls, table_name=table_name, exist=True)

        building_attributes = building_cls.attributes
        attr_attributes = getattr(cls, "__attrs_attrs__")
        sqlalchemy_attributes = {
            "__tablename__": table_name,
            # Automatically add id
            "id": Column(Integer, primary_key=True),
        }

        for attr_attribute in attr_attributes:

            # arguments for sqlalchemy.Column
            logger.debug("attr_attribute %s", attr_attribute)
            logger.debug("map tablename cls %s", self._map_tablename_cls)
            logger.debug("map cls tablename %s", self._map_cls_tablename)

            attribute_name = attr_attribute.name
            coloring.print_bgreen("Attribute", cls.__name__, attribute_name)
            sqlalchemy_type = None
            args = []
            kwargs = {}
            metadata = attr_attribute.metadata["koala"]
            # Get sqlalchemy column type
            attr_type = attr_attribute.type
            if attribute_name == "age":
                coloring.print_bred("Age here")

            if isinstance(attr_type, sqlalchemy.sql.visitors.VisitableType):
                # sqlalchemy type (Integer, String, ...)
                sqlalchemy_type = attr_type
                print("in if")
            elif attr_type in self._map_cls_to_sqlalchemy_types:
                print("in elif")
                # convert builtin types  (int, str, bool, ...)
                sqlalchemy_type = self._map_cls_to_sqlalchemy_types[attr_attribute.type]
            else:
                print("in else")
                self._register_building_attribute(building_cls, attr_attribute)
                # The type is a an other table, we don't build it now we juste
                # collect information about it, to built it at init()
                if isinstance(attr_type, str):
                    # name of the cls
                    clsname_type = attr_type
                else:  # attr_type is ORM cls
                    # cls_type = attr_type
                    clsname_type = attr_type.__name__

                del attr_type  # to avoid errors

                # check it cls type is the same as this cls
                # if so, nullable must be True! (otherwise it's impossible to instantiate the object)
                # TODO: move the check in _register_building_attribute?
                if clsname_type == cls.__name__:
                    if not metadata["nullable"]:
                        # TODO: test this case (tell Yassmine?)
                        raise ValueError(
                            f"Attribute {attr_attribute.name!r} must be nullable when "
                            f"it's type is referencing to the same class ({cls.__name__!r})"
                        )

                # Don't build anything, init() will build all the relations
                continue

            # Build kwargs

            kwargs["unique"] = metadata["unique"]
            kwargs["nullable"] = metadata["nullable"]
            coloring.print_bmagenta("building column for", cls_name)
            print("name", attribute_name)
            print("type", sqlalchemy_type)
            print("args", args)
            print("kwargs", kwargs)
            print()
            # Create the Column
            sqlalchemy_attributes[attribute_name] = Column(
                sqlalchemy_type, *args, **kwargs
            )
            if attribute_name == "age":
                coloring.print_bred("finish building age collumn")
        # sqlalchemy_attributes.update(sqlalchemy_attributes_later)
        coloring.bblue("sqlalchemy attributes")
        print(sqlalchemy_attributes)
        # ORM cls inherit from the decorated cls and self.Base
        OrmCls = type(cls.__name__, (cls, self.Base), sqlalchemy_attributes)
        # ============================================================= #
        # Create a new cls that inherit from Base and the decorated cls #
        # ============================================================= #
        self._map_tablename_cls[table_name] = OrmCls
        self._map_cls_tablename[OrmCls] = table_name

        building_cls.update(orm_cls=OrmCls)
        return OrmCls

    def _register_building_attribute(
        self, cls_building: BuildingClass, attr_attribute
    ) -> BuildingRelationalAttribute:
        """Register an attribute"""

        attr_name = attr_attribute.name
        attr_type = attr_attribute.type
        metadata = attr_attribute.metadata["koala"]
        cls = cls_building.cls
        cls_name = cls.__name__
        building_attributes = cls_building.attributes
        building_attribute = cls_building.get_or_create_attribute(attr_name)
        building_attribute.update(attr_attribute=attr_attribute)
        building_attribute.update(exist=True)
        # check if the attribute is typing.List to use a "many" relationship
        many = False
        if isinstance(attr_type, typing.GenericMeta):
            if attr_type.__name__ == "List":
                many = True
                # check if List is empty (ex: List instead of List[Animal])
                if not attr_type.__args__:  # noqa
                    raise ValueError(
                        f"List annotation for {cls_name}.{attr_name} can not be empty"
                    )
                attr_type = attr_type.__args__[0]  # noqa

                # Check if the argument of List is a string
                if isinstance(attr_type, typping_ForwardRef):
                    attr_type = attr_type.__forward_arg__
            else:
                raise ValueError(
                    f"Support only List annotation, don't support {attr_type}"
                )
        if not isinstance(attr_type, str):
            attr_type = attr_type.__name__
        atomic_type = attr_type

        building_attribute.update(many=many, atomic_type_name=atomic_type)

        # build the ref_type if it doesn't exist
        ref_cls_name = atomic_type
        ref_building_cls = self._get_or_create_building_cls(atomic_type)

        # check if the attribute have a reference to an other one
        ref_attribute_name = metadata["ref"]
        if ref_attribute_name:
            # check: if the ref_class is already parsed check if ref attribute exist
            if ref_building_cls.exist:
                # if ref_attribute_name not in
                if (
                    ref_attribute_name not in ref_building_cls.attributes
                    or not ref_building_cls.attributes[ref_attribute_name].exist
                ):
                    raise ValueError(
                        f"{cls_building.name}.{attr_name} reference non existing attribute {ref_attribute_name}"
                    )

            # get the building_attribute
            ref_building_attributes = ref_building_cls.attributes
            building_attribute_ref = ref_building_cls.get_or_create_attribute(
                ref_attribute_name
            )

            building_attribute_ref.update(atomic_type_name=cls_name)
            building_attribute_ref.update(referenced_by=building_attribute)

            coloring.print_balice_blue("attribuuuuutes :'(")
            # Check if reference are consistent
            if building_attribute_ref.referenced_by:
                coloring.print_balice_blue("attribuuuuutes")
                print("this attribute", building_attribute)
                print("ref attribute", building_attribute_ref)
                # check that class is consistent
                #  ex: If Person have an attributes List[Animal] animals, ref=owner
                #  owner must be of type Person!
                ref_attomic_type = building_attribute_ref.atomic_type_name
                print("ref_attomic_type", ref_attomic_type)
                if ref_attomic_type and ref_attomic_type != cls_name:
                    raise ValueError(
                        f"{cls_name}.{attr_name} reference {ref_cls_name}.{ref_attribute_name}, but "
                        f" {ref_cls_name}.{ref_attribute_name} reference {ref_attomic_type} class"
                    )
                ref_referenced_by_name = building_attribute_ref.referenced_by.name

                if ref_referenced_by_name != attr_name:
                    raise ValueError(
                        f"The {cls_name}.{attr_name} reference {ref_cls_name}.{ref_attribute_name}"
                        f" but {ref_cls_name}.{ref_attribute_name} "
                        f"reference {cls_name}.{ref_referenced_by_name}"
                    )

        return building_attribute

    def init(self):
        # construict classes
        for cls_name in self._building_class:
            self._build_orm_relations(cls_name)

        self.Base.metadata.create_all(self.engine)
        self.session = self.Session()

    def _build_orm_relations(self, cls_name: str):
        buildingn_cls = self._building_class[cls_name]
        cls = buildingn_cls.cls
        orm_cls = buildingn_cls.orm_cls
        print("ORM relations", buildingn_cls)
        print()
        for building_attribute in buildingn_cls.attributes.values():
            # Check if the attribute exist or if it's referenced but don't exist
            if not building_attribute.exist:
                referenced_by = building_attribute.referenced_by
                assert ValueError(
                    f"Attribute {building_attribute.name} is referenced by {referenced_by.name} but don't exist"
                )
            print("Buildin attribute", building_attribute)
            attr_attribute = building_attribute.attr_attribute
            print("metadataaaaaaaa                ", repr(attr_attribute))
            print("METADATA", building_attribute.name, cls_name)
            metadata = attr_attribute.metadata["koala"]
            ref = metadata["ref"]
            many = building_attribute.many
            if not ref:
                ref_many = True
            else:
                ref_many = True

            if not isinstance(building_attribute.atomic_type_name, str):
                ref_type = building_attribute.atomic_type_name.__name__
            else:
                ref_type = building_attribute.atomic_type_name
            ref_building_cls = self._building_class[ref_type]
            if not many and ref_many:
                # one to many relations
                self._build_one_to_many_relation(
                    buildingn_cls, ref_building_cls, building_attribute.name
                )

    def _build_one_to_many_relation(
        self,
        one_cls: BuildingClass,
        many_cls: BuildingClass,
        one_attribute_name,
        one_relation=True,
    ):
        # add the foreign_key in the one_cls side
        coloring.print_bgreen("Adding one_to_many_relation")
        print(
            "Adding one_to_many_relation for",
            one_cls.name,
            "to",
            many_cls.name,
            "with attribute",
            repr(one_attribute_name),
        )
        print("Foreing key column")
        many_cls_id = f"{many_cls.table_name}.id"

        foreign_key = Column(Integer, ForeignKey(many_cls_id))
        foreign_key_name = f"{one_attribute_name}_id"
        print("foreingkey", foreign_key)
        setattr(one_cls.orm_cls, foreign_key_name, foreign_key)

        if one_relation:
            coloring.print_bcyan("add forein key for ", many_cls.name)
            print("cls", many_cls.name)
            print("foreign_keys", f"{one_cls.name}.{foreign_key_name}")
            print("attribute", one_attribute_name)
            print("remote_side", many_cls.orm_cls.id)

            relation = sqlalchemy.orm.relationship(
                many_cls.name,
                remote_side=many_cls.orm_cls.id,
                foreign_keys=f"{one_cls.name}.{foreign_key_name}",
            )
            setattr(one_cls.orm_cls, one_attribute_name, relation)
            # print(coloring.bred("relation"), one_cls.orm_cls, one_attribute_name, relation)

        print("\n")

    def first(self, table, **kwargs):
        if isinstance(table, str):
            table = self._map_tablename_cls[table]
        return self.session.query(table).filter_by(**kwargs).first()

    def close(self):
        self.commit()

    # aliases
    ib = attribute

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()


def relationaldb(
    uri: str = None, *, echo: bool = None, autocommit: bool = None
) -> RelationalDB:
    return RelationalDB(uri, echo=echo, autocommit=autocommit)
