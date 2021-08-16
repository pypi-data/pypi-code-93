import logging
import warnings
from collections.abc import Iterable
from functools import reduce

from pentaquark.constants import SEPARATOR, RELATIONSHIP_OBJECT_KEY
from pentaquark.exceptions import PentaQuarkConfigurationError, PentaQuarkObjectDoesNotExistError
from pentaquark.models.base import PropertyModelBase, RESERVED_KEYWORDS, MetaModelOptions
from pentaquark.patterns import N
from pentaquark.properties import CypherProperty, ComputedProperty
from pentaquark.relationships.enums import RelationshipCardinality
from pentaquark.utils import unflatten_list
from pentaquark.registry import node_registry

logger = logging.getLogger(__name__)


def cypher(return_type):
    """Property computed from a Cypher operation"""
    def decorated(meth):
        """Just attach an attribute to the decorated method"""
        meth._is_cypher_property = True
        meth._return_type = return_type
        return meth
    return decorated


def graphql_property(graphql_type, name=None, requires=None, many=False):
    """Expose an extra property in the GraphQL schema (read-only)"""
    def decorated(meth):
        meth._is_graphql_property = True
        meth._graphql_type = graphql_type
        meth._graphql_name = name
        meth._requires = requires
        meth._many = many
        return meth
    return decorated


class NodeMeta(PropertyModelBase):
    def __new__(mcs, name, bases, attrs):
        from pentaquark.properties.relationships import RelationshipProperty
        from pentaquark.properties import CypherProperty
        relationships = {}
        graphql_properties = {}
        for attr_name, attr in attrs.items():
            if isinstance(attr, RelationshipProperty):
                if SEPARATOR in attr_name:
                    raise PentaQuarkConfigurationError(f"'{attr_name}' contains {SEPARATOR}")
                if attr_name in RESERVED_KEYWORDS:
                    raise PentaQuarkConfigurationError(f"'{attr_name}' is a reserved keyword")
                relationships[attr_name] = attr
                if hasattr(attr, "bind_to_model"):
                    attr.bind_to_model(attr_name)
                continue
            if getattr(attr, "_is_cypher_property", None):
                func = getattr(mcs, attr_name)
                setattr(mcs,
                        attr_name,
                        CypherProperty(cypher=func(), return_type=func._return_type)
                        )
            if getattr(attr, "_is_graphql_property", None):
                prop_name = attr._graphql_name or attr_name
                graphql_properties[prop_name] = attr
        # manage inheritance
        for b in bases:
            if hasattr(b, "_relationships"):
                for rn, rel in b._relationships.items():
                    # prevent changing the RelationshipProperty (rel) reference
                    # when base (b) has same metaclass
                    if rn in relationships:
                        continue
                    relationships[rn] = rel
            if hasattr(b, "_graphql_properties"):
                for pn, p in b._graphql_properties.items():
                    if pn in graphql_properties:
                        continue
                    graphql_properties[pn] = p
        attrs["_relationships"] = relationships
        attrs["_graphql_properties"] = graphql_properties

        kls = PropertyModelBase.__new__(mcs, name, bases, attrs)
        meta = attrs["_meta"]
        logger.info("Creating model %s (meta = %s)", mcs, meta)
        if not meta.is_abstract:
            label = meta.label
            logger.info("Registering model %s", label)
            node_registry.add(
                label, kls,
            )
        return kls


class Node(metaclass=NodeMeta):
    class Meta:
        is_abstract = True
        """Abstract classes are not queryable
        """
        id_property = "id"
        """Property to use as unique identifier by default
        """
        help_text = ""
        """Description that will be added to the GraphQL schema
        """
        unique_together = ()
        """Experimental: define properties that must be considered unique
        Does not work with relationships yet.
        """
        allow_undeclared_properties = False
        """By default, all properties MUST be declared in the model class.
        This parameter offers more freedom by letting the user set undeclared
        properties on the instance, that will be saved to Neo4j and can be used
        for querying.
        """

    _is_bound = True
    """Basically defines whether this class can be found in the node registry
    """

    def __init__(self, **kwargs):
        """
        Initialize node object:
            - Validate each Property value (type-check)
            - Set default values if necessary (property's value is None
                and a default has been declared)
            - Compute ComputedProperties
        :param kwargs: properties' values
        :return: None
        """
        self.cached_properties = {}
        self._is_in_neo = False
        self.is_sync = False
        # need to create a copy of kwargs to store initial unbound properties
        self.initial_data = dict(kwargs)

        deferred_properties = []

        for fn, prop in self._properties.items():
            prop.bind_to_instance(self)
            val = kwargs.pop(fn, None)
            if val is None:
                # requirement check is done before saving
                # rather than at object creation
                # if prop.required:
                #     raise ValueError(f"Field {fn} is mandatory but no value provided")
                if isinstance(prop, ComputedProperty):
                    deferred_properties.append(prop)
                    continue
                elif prop.default:
                    try:
                        val = prop.default()
                    except TypeError:  # not callable
                        val = prop.default
            setattr(self, fn, val)

        for rn, rel in self._relationships.items():
            self.cached_properties[rn] = None
            rel_manager = getattr(self, rn)
            rel_ins = kwargs.pop(rn, None)
            if rel_ins is None:
                rel_ins = []
            elif not isinstance(rel_ins, Iterable):
                rel_ins = [rel_ins, ]
            for ri in rel_ins:
                # add the related object to the related set
                # the RelationshipManager will take care of
                # updating the cached properties
                rel_manager.add(ri)

        for prop in deferred_properties:
            for d in prop.deps:
                if d not in self._properties:
                    logger.warning(
                        f"Dependent '{d}' is not in the list of class properties for '{self.__class__.__name__}'"
                    )
                    continue
                self._properties[d].bind_to_dependent_prop(prop)
            setattr(self, prop.name, None)

        # final loop through kwargs to deal with undeclared properties if any
        for k, v in kwargs.items():
            if (k not in self._properties) and (k not in self._relationships):
                # keep related object ID if provided
                if k in [r + "_id" for r in self._relationships]:
                    setattr(self, k, v)
                    continue
                if not self._meta.allow_undeclared_properties:
                    warnings.warn(
                        f"Property {k} of model {self} will be ignored",
                        UserWarning
                    )
                    continue
                # add a field in this instance property list
                setattr(self, k, v)
                # TODO: manage this through Property?
                #  Accessors do not work on instance-defined Property
                self.cached_properties[k] = v

    def __str__(self):
        return f"<{self.get_label()}: {self.get_id_property_name()}: {self.get_id()}>"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def is_bound(cls):
        return cls._is_bound

    # Node characteristics
    @classmethod
    def get_label(cls):
        return cls._meta.label

    @classmethod
    def get_id_property_name(cls):
        return cls._meta.id_property

    @classmethod
    def get_property_graphql_type(cls, prop_name=None):
        if not prop_name:
            prop_name = cls.get_id_property_name()
        return cls._properties[prop_name].graphql_type

    def get_id(self):
        return getattr(self, self.get_id_property_name(), None)

    def get_id_dict(self):
        id_prop_name = self.get_id_property_name()
        return {
            id_prop_name: self.get_id(),
        }

    @classmethod
    def get_id_property_graphql_type(cls):
        id_property_name = cls.get_id_property_name()
        id_property = cls._properties.get(id_property_name)
        return id_property.get_graphql_type()

    @classmethod
    def get_graphql_type(cls):
        return cls.get_label()

    def set_defaults(self):
        """Set default property values if not set on the instance"""
        for pn, prop in self._properties.items():
            if (
                getattr(self, pn, None) is None
                and prop.has_default
            ):
                setattr(self, pn, prop.default_value())

    def __setattr__(self, key, value):
        # let's update the "unbound" properties
        # NB: it is not possible to create unbound properties on the fly
        if key not in self._properties and key not in self._relationships:
            if idata := getattr(self, "initial_data", None):
                if key in idata:
                    self.cached_properties[key] = value
        super().__setattr__(key, value)

    def relationship_kwarg_names(self):
        """
        Return a list with relationship names
        and names suffixed with _id

        :return:
        """
        return reduce(lambda x, y: x+y, [
            [rn, f"{rn}_id"] for rn in self._relationships
        ], [])

    def get_property_kwargs(self):
        """Get kwargs for Cypher CREATE operations"""
        properties = {}
        for pn, prop in self._properties.items():
            properties[pn] = getattr(self, pn, None)
        kw = self.kwargs_to_cypher(**properties)
        if self._meta.allow_undeclared_properties:
            for k, v in self.cached_properties.items():
                if k not in kw and k not in self.relationship_kwarg_names():
                    kw[k] = v
        return kw

    @classmethod
    def _kwargs_to_cypher(cls, k, value):
        if k in cls._properties:
            prop = cls._properties[k]
            return prop.to_cypher(value)
        return value

    @classmethod
    def kwargs_to_cypher(cls, **kwargs):
        """Translate kwargs to Cypher using this class property list"""
        params = {
            pn: cls._kwargs_to_cypher(pn, value)
            for pn, value in kwargs.items()
            if pn in cls._properties
            or (cls._meta.allow_undeclared_properties and pn not in cls._relationships)
        }
        return params

    def check_required_properties(self, kwargs=None):
        """Check that all required properties are set
        (before save for instance)
        """
        for pn, prop in self._properties.items():
            if kwargs:
                v = kwargs.get(pn, None)
            else:
                v = getattr(self, pn, None)
            if prop.required and v is None:
                raise ValueError(f"Field {pn} is mandatory but no value provided")
        for rn, rel in self._relationships.items():
            rel_ins = getattr(self, rn, None)
            if rel.required and rel_ins is None:
                raise ValueError(f"Relationship {rn} is a required relationship for {self.__class__.__name__}")

    # Node uniqueness
    def __eq__(self, other):
        if self.is_sync:
            if self_id := getattr(self, self.get_id_property_name()):
                if other_id := getattr(other, other.get_id_property_name()):
                    return self_id == other_id
            return False
        else:
            return True
        # else, compare unique elements

    # Hydrate from DB
    @classmethod
    def hydrate(cls, **kwargs):
        """Create an instance from Neo4j returned results"""
        logger.debug("NODE: HYDRATE: %s", kwargs)
        kls = cls()
        hydrated = []
        kls.initial_data = kwargs
        # check property/relationship and only assign to
        # the object being hydrated the props that have been defined
        # in the model creation
        for pn, prop in kls._properties.items():
            v = prop.from_cypher(kwargs.get(pn))
            setattr(kls, pn, v)
            hydrated.append(pn)
        for rn, _ in kls._relationships.items():
            if kw := kwargs.get(rn):
                logger.debug("NODE: HYDRATE: relationship %s, %s", rn, kw)
                cls.hydrate_related_object(kls, rn, kw)
            hydrated.append(rn)
        if cls._meta.allow_undeclared_properties:
            # model allows for unbound properties, attach
            # remaining properties to the instance
            # TODO: manage undeclared relationships?
            for k, v in kwargs.items():
                if k not in hydrated:
                    # Neo4j driver will return specific DateTime type instead of python
                    # built-in datetime objects, so let's convert back to native types
                    # when this is possible
                    if hasattr(v, "to_native"):
                        v = v.to_native()
                    hydrated.append(k)
                    setattr(kls, k, v)
        kls.is_sync = True
        kls._is_in_neo = True
        return kls

    @classmethod
    def hydrate_related_object(cls, kls, rn, rn_kwargs):
        """Set related objects from Neo4j returned results"""
        if not rn_kwargs:
            return
        logger.debug("NODE: HYDRATE_RELATED: %s, %s", rn, rn_kwargs)
        rel_manager = getattr(kls, rn, None)
        # add rn=kls parameter for relationship with mandatory "parent"
        for kw in rn_kwargs:
            rel_manager.hydrate(rn=kls, **kw)

    # DB operations
    def _try_update(self, extra_kwargs=None):
        """Check whether an object with the same ID already exists in the DB,
        in which case the user has to make a choice on the wanted behaviour
        """
        try:
            self.q.match(**self.get_id_dict()).one()
        except PentaQuarkObjectDoesNotExistError:
            return False
        self.q.merge(ins=self, extra_kwargs=extra_kwargs)
        return True

    def save(self, **kwargs) -> None:
        """Save current instance

        :return: None
        """
        if self.get_id():  # if the ID is set, try to update existing object
            u = self._try_update(extra_kwargs=kwargs)
            if u:
                return
        # finally, try to create a new node
        self.q.create(ins=self, extra_kwargs=kwargs)

    def post_create(self, extra_kwargs=None) -> None:
        """Method called after object creation.
        Can be used to perform user-defined post creation operations on the model
        """
        pass

    def post_save(self, extra_kwargs=None) -> None:
        """Method called after each save (create or update) event"""
        pass

    def add_label(self, label):
        if not self._is_in_neo:
            raise Exception("not possible")
        self.q.add_label(self.get_id_dict(), label)

    def exists(self) -> bool:
        if q := self.get_existence_query():
            return q.exists()
        # unique fields
        # FIXME: filters here should never be empty?
        if filters := self.get_existence_filters():
            return self.__class__.q.match(
                **filters
            ).exists()
        return False

    def get_existence_query(self):
        if filters := self.get_existence_filters():
            return self.__class__.q.match(
                **filters
            )
        return None

    def get_existence_filters(self):
        filters = {}
        for u in self._meta.unique_together:
            if value := getattr(self, u):
                filters[u] = value
        return filters
        # for f in fields:
        #     try:
        #         selection = f.selection_set.selections
        #     except AttributeError:
        #         selection = None
        #     print(f)
        #     if selection:
        #         print(f.name.value, selection)
        #         if f.name.value in self._relationships:
        #             rel = self._relationships[f.name.value]
        #             related_instances = getattr(self, f.name.value)
        #             res = []
        #             for ri in related_instances:
        #                 res.append(ri.to_graphql_return(selection))
        #             if rel.cardinality == RelationshipCardinality.NONE:
        #                 result[f] = res
        #             else:
        #                 result[f] = res[0]
        #         else:
        #             raise TypeError("Unmanaged case")
        #     else:
        #         result[f.name.value] = getattr(self, f.name.value)
        # return result

    def detach_delete(self):
        """Detach delete a node"""
        return self.q.detach_delete(**self.get_id_dict())

    def delete(self):
        """Delete node"""
        return self.q.delete(**self.get_id_dict())

    @classmethod
    def to_cypher_match(cls, alias="", data=None,
                        param_store=None,
                        include_alias=True, include_label=True):
        """Returns the Cypher MATCH clause for this node

        :param str alias: node alias
        :param dict data: parameter to match the node against
        :param ParameterStore param_store: an existing ParameterStore
        :param bool include_alias: if True, the query will generate Cypher including
            entity aliases (MATCH (n:Node)...). If not the aliases will be omitted
            (MATCH (:Node)...)
        :param bool include_label: if True, the query will generate Cypher including
            labels, ie creating new variable (MATCH (n:Node)...). If not the aliases will be omitted
            (MATCH (n)...).
            NB: this could be replaced by a check "label is in variables", but that would not work
            for where clause in map projections (?). However, this feature is not used for now.
        """
        # logger.debug("NODE.to_cypher_match include_alias=%s, include_label=%s", include_alias, include_label)
        kwargs = data or {}
        if cls._is_bound and not cls._meta.allow_undeclared_properties:
            for k, v in kwargs.items():
                if k not in cls._properties or isinstance(k, CypherProperty):
                    raise AttributeError(f"'{k}' is not a valid property for model {cls.__name__}")
        label = cls.get_label()
        return N(
            label=label if include_label else None,
            alias=alias if include_alias else "",
            data=kwargs,
            param_store=param_store,
        )

    @classmethod
    def traverse_cypher(
            cls, relationship, alias, data=None,
            variables=None, param_store=None,
            include_alias=True, include_label=True) -> str:
        """Create the Cypher pattern to traverse a relationship

        :param str relationship: name of the relationship attribute in this model
        :param str alias: relationship alias
        :param dict data: relationship data
        :param list variables: variables already in scope (not used)
        :param ParameterStore param_store: an existing ParameterStore
        :param bool include_alias: if True, the query will generate Cypher including
            entity aliases (MATCH (n:Node)...). If not the aliases will be omitted
            (MATCH (:Node)...)
        """
        # logger.debug("NODE.TRAVERSE rel=%s, alias=%s, data=%s", relationship, alias, data)
        relationship_manager = getattr(cls, relationship, None)
        if relationship_manager is None:
            raise AttributeError(f"'{relationship}' is not a valid relationship for model {cls.__name__}")
        rel_data = data.pop(RELATIONSHIP_OBJECT_KEY, {})
        return relationship_manager.rel_property.to_cypher_match(
            alias, variables=variables,
            include_alias=include_alias, include_label=include_label,
            param_store=param_store, rel_data=rel_data, data=data)

    def _graphql_property_to_graphql_return(self, rel_key, rel_values, context):
        """Resolve GraphQL property using to_graphql_return if method exists (ie graphql_return_type is a Node)"""
        method = getattr(self, rel_key)
        method_result = method(context=context)
        if method._many:
            method_result = [
                m.to_graphql_return(rel_values, context=context) if hasattr(m, "to_graphql_return") else m
                for m in method_result
            ]
        else:
            method_result = (
                method_result.to_graphql_return(rel_values, context=context)
                if hasattr(method_result, "to_graphql_return") else method_result
            )
        return method_result

    # GraphQL related methods
    def to_graphql_return(self, ret_values: list[str], context: dict) -> dict:
        """Build dict to be returned by a GraphQL query

        :param list ret_values: the list of fields to be returned, including relationships
        :param dict context:
        """
        result = {}
        values = unflatten_list(*ret_values)
        for v in values:
            if isinstance(v, dict):  # relationship or graphql property
                rel_key, rel_values = next(iter(v.items()))
                if rel_key in self._relationships:
                    rel = self._relationships[rel_key]
                    related_instances = getattr(self, rel_key)
                    res = []
                    for ri in related_instances.all():
                        res.append(ri.to_graphql_return(rel_values, context={
                            "parent": self,
                        }))
                    if rel.cardinality == RelationshipCardinality.NONE:
                        result[rel_key] = res
                    else:
                        result[rel_key] = res[0]
                elif rel_key in self._graphql_properties:
                    result[rel_key] = self._graphql_property_to_graphql_return(
                        rel_key, rel_values, context=context,  # TODO: keep track of all parents in context?
                    )
                else:
                    raise ValueError(f"'{v}' unrecognized")
            elif v in self._properties:
                if x := getattr(self, v):
                    result[v] = self._properties[v].to_graphql(x)
            elif v in self._graphql_properties:
                result[v] = self._graphql_property_to_graphql_return(
                    v, None, context,
                )
            else:
                raise ValueError(f"'{v}' unrecognized")
        return result

    # @graphql_property("String", name="__typename")
    # def typename(self):
    #     """GraphQL Helper function"""
    #     return self.get_graphql_type()


"""
Experimental features
"""


class UNode(Node):
    _is_bound = False

    class Meta:
        allow_undeclared_properties = True


def UnboundNode(label):
    """Utility to access the query builders without explicitly declaring all properties
    """
    kls = type(
        label,
        (UNode, ),
        {
            "Meta": MetaModelOptions(allow_undeclared_properties=True, is_abstract=True)
        }
    )
    return kls
