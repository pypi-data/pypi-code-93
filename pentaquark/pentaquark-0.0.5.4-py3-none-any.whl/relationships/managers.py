# import warnings
import logging
import collections.abc
import warnings
from functools import reduce

from pentaquark.constants import START_NODE_ALIAS, SEPARATOR, RELATIONSHIP_OBJECT_KEY
from pentaquark.db import connection
from pentaquark.exceptions import PentaQuarkObjectDoesNotExistError, PentaQuarkCardinalityError
from .enums import RelationshipCardinality
from ..mixins import IteratorMixin
from ..query_builders.param_store import ParameterStore

logger = logging.getLogger(__name__)


class RelationshipSet:
    """A wrapper around a list of relationships"""

    # FIXME: make sure RelationshipSet only contains Relationships!

    def __init__(self, relationships=None):
        self.relationships = relationships or []

    def __eq__(self, other):
        return self.relationships == other.relationships

    def __bool__(self):
        return len(self.relationships) > 0

    def __str__(self):
        return f"<RelationshipSet {str(self.relationships)}>"

    def __repr__(self):
        return f"<RelationshipSet {str(self.relationships)}>"

    def add(self, rel):
        """Add a relationship to the relationship set.
        Does not perform any db operation.

        :param rel: Relationship
        :return:
        """
        if isinstance(rel, collections.abc.Iterable):
            self.relationships.extend(rel)
        else:
            self.relationships.append(rel)

    def remove(self, other):
        """Remove the relationship rel from the relationship set.
        Does not perform any db operation.

        :param rel: Node
        :return:
        """
        for r in self.relationships:
            if r.end_node == other:
                self.relationships.remove(r)

    def items(self):
        for r in self.relationships:
            yield r.end_node, r

    def nodes(self):
        if self.relationships:
            return [r.end_node for r in self.relationships]
        return []

    def get(self, other):
        for n in self:
            if other == n.end_node:
                return n

    # TODO: is this method needed
    def __iter__(self):
        return iter(self.relationships)

    def __next__(self):
        yield from self.relationships

    def __len__(self):
        return len(self.relationships)

    def __getitem__(self, item):
        try:
            return self.relationships[item]
        except IndexError as e:
            raise PentaQuarkObjectDoesNotExistError(e)


class RelationshipManager(IteratorMixin):
    base_iterator = dict

    def __init__(self, instance, rel_property):
        super().__init__()
        self.instance = instance
        self.rel_property = rel_property
        self.is_sync = False
        self._all_fetched = False

    def items(self):
        if not self.related_objects:
            return []
        for r in self.related_objects:
            yield r.end_node, r

    def __iter__(self):
        # TODO: manage cases where there are multiple relationships
        #  between the same two nodes
        for item in self.related_objects:
            yield item.end_node

    def __next__(self):
        for item in self:
            yield item

    def _get_cached_or_fetch(self, ret_params=None, filters=None, force_reload=False):
        """Fetch data or use cached value, unless force_reload is True.

        :param ret_params: return parameters for the relationship and target node
        :param filters: filter on relationship or target node properties
        :param force_reload: do not use cache and force refetching data. Useful when
            related set has been filtered
        :return:
        """
        ret_params = ret_params or []
        filters = filters or {}
        use_cached = True
        # the below code would force some return params, do not do that for now
        # if not ret_params:
        #     # make sure we return the relationship data and the target model
        #     ret_params = [self.rel_property.name]
        #     if self.rel_property.model is not None:
        #         ret_params.append(f"{self.rel_property.name}{SEPARATOR}{RELATIONSHIP_OBJECT_KEY}")
        logger.debug("REL_MANAGER: GET_CACHED_OR_FETCH: ret_params=%s, "
                     "related_objects=%s, instance=%s, kwargs=%s",
                     ret_params, self.related_objects, self.instance, filters)
        if filters and not self._all_fetched:  # force reloading if we are filtering a partial dataset
            force_reload = True
        if not filters:
            self._all_fetched = True
        if force_reload:
            self.related_objects = None
        if not isinstance(self.related_objects, RelationshipSet):
            use_cached = False
            if self.instance._is_in_neo:
                data = self._fetch_data(*ret_params, raw=True, filters=filters)
                for d in data:
                    self.hydrate(**d)
                if not data:
                    # set related object to empty RelationshipSet
                    # (different from its initial value, None, which is the sign
                    # data has not been requested yet, empty RS means data is empty)
                    self.related_objects = RelationshipSet()
            elif rel_id := getattr(self.instance, self.rel_property.name + "_id", None):
                target_class = self.rel_property.get_target_node_class()
                rel_obj = target_class.q.match(
                    **{
                        target_class.get_id_property_name(): rel_id
                    }
                ).one()
                self.add(rel_obj)
        return self.related_objects, use_cached

    def _fetch_data(self, *ret_params, filters=None, raw=False):
        """

        :param ret_params: return parameters
        :return:
        """
        returns = [
            *ret_params
            # f"{self.rel_property.name}{SEPARATOR}{p}" for p in ret_params
        ] if ret_params else [self.rel_property.name]
        params = {
            **self.instance.get_id_dict(),
            **{self._get_filter_key(k): v for k, v in filters.items()}
        }
        data = self.instance.__class__.q.match(**params).returns(*returns)
        if raw:
            try:
                data = data.raw().all()
            except PentaQuarkObjectDoesNotExistError:
                return RelationshipSet()
            related_data = reduce(
                lambda x, y: x + y[START_NODE_ALIAS][self.rel_property.name],
                data,
                []
            )
            return related_data
        data = data.all()
        # related_data = data[START_NODE_ALIAS][self.rel_property.name]
        return [getattr(d, self.rel_property.name) for d in data]

    def one(self, *ret_params):
        logger.debug("REL_MANAGER: ONE: ret_params=%s", ret_params)
        r, _ = self._get_cached_or_fetch(ret_params=ret_params)
        if r and len(r) > 0:
            return r[0].end_node
        return None

    def _get_filter_condition(self, key, value, obj):
        """

        :param key: parameter name  (+lookup if any)
        :param value: filter value
        :param obj: objects to be filtered
        :return:
        """
        if SEPARATOR in key:
            field, lookup = key.rsplit(SEPARATOR, 1)
        else:
            field = key
            lookup = "eq"
        if field not in obj._properties:
            raise ValueError(f"'{field}' is not a valid property for {obj.__class__.__name__}")
        if lookup != "eq":
            raise NotImplementedError(f"Lookup {lookup} is not (yet) implemented in the filter method. "
                                      f"You have to filter yourself.")
        return getattr(obj, field) == value

    def _get_filter_key(self, k):
        if k.startswith(self.rel_property.name):
            return k
        return f"{self.rel_property.name}{SEPARATOR}{k}"

    def filter(self, *ret_params, **kwargs):
        data, use_cached = self._get_cached_or_fetch(ret_params=ret_params, filters=kwargs)
        if use_cached:
            # we already have some data
            pruned_list = RelationshipSet([
                d for d in self.related_objects
                if all(
                    self._get_filter_condition(k, v, d.end_node) for k, v in kwargs.items()
                )
            ])
            return pruned_list
        return data

    def all(self, *ret_params, force_reload=False):
        c, _ = self._get_cached_or_fetch(ret_params=ret_params, force_reload=force_reload)
        if c:
            return c.nodes()
        return []

    def get(self,  *ret_params):
        logger.debug("REL_MANAGER: GET: ret_params=%s", ret_params)
        if self.rel_property.cardinality == RelationshipCardinality.UNIQUE_STRICT:
            return self.one(*ret_params)
        return self.all(*ret_params)

    @property
    def related_objects(self):
        cached_properties = self.instance.cached_properties
        if self.rel_property.name in cached_properties:
            return cached_properties[self.rel_property.name]
        return None

    @related_objects.setter
    def related_objects(self, value):
        # logger.debug("related_objects.setter %s", value)
        self.instance.cached_properties[self.rel_property.name] = value

    def _add_single(self, ins, **kwargs):
        """

        :param ins:
        :param kwargs:
        :return:
        """
        # logger.debug("REL_MANAGER: ADD_SINGLE: %s, %s", ins, kwargs)
        relationship = self._relationship(ins, **kwargs)
        # logger.debug("REL_MANAGER: ADD_SINGLE: new_relationship=%s", relationship)
        self._check_other_is_valid(ins)
        related_objects = self.related_objects
        # logger.debug("REL_MANAGER: ADD_SINGLE: related_objects=%s", related_objects)
        if related_objects is None:
            related_objects = RelationshipSet()
        elif not isinstance(related_objects, collections.abc.Iterable):
            related_objects = RelationshipSet([related_objects])
        related_objects.add(relationship)
        self.related_objects = related_objects
        return related_objects

    def _check_other_is_valid(self, other):
        """

        :param Node other:
        :return:
        """
        # check node label is consistent with relationship definition
        other_label = other.get_label()
        if other_label != self.rel_property.target_node_labels:
            raise Exception(f"{other_label} not a valid target for {self.rel_property.name} "
                            f"(accepting: {self.rel_property.target_node_labels})")
        # check the relationship cardinality
        if self.related_objects:
            existing = self.related_objects.get(other)
            if existing and existing._is_in_neo:
                raise PentaQuarkCardinalityError(
                    f"There is already a relationship of type {self.rel_property.rel_type} "
                    f"between {self.instance} and {other}"
                    f"({self.related_objects})"
                )
            # elif (
            #         self.cardinality == RelationshipCardinality.UNIQUE_LABEL
            #         and any(o.get_label() == other.get_label() for o in self._others)
            # ):
            #     raise AtomicUniquenessViolationError(
            #         f"There is already a relationship of type {self.rel_type} between {self.source} "
            #         f"and a node with label {other.get_label()}"
            #     )

    def add(self, node, **kwargs):
        """Add the relationship between self.instance and ins with properties kwargs
        No DB operation is performed.

        :param node:
        :param kwargs:
        :return:
        """
        # logger.debug("REL_MANAGER: ADD: %s, %s", node, kwargs)
        if kwargs and not self.rel_property.model:
            raise TypeError("Can not provide kwargs for relationships without model")
        if not node:
            raise ValueError("cannot add empty or None objects")
        return self._add_single(node, **kwargs)

    def remove(self, node):
        if node not in self.related_objects.nodes():
            raise ValueError(f"Can not remove {node}, not connected")
        self.related_objects.remove(node)

    def hydrate(self, **kwargs) -> None:
        """Create a relationship instance and add it to the current instance

        :param kwargs: relationship properties if any
        :return:
        """
        # logger.debug("REL_MANAGER: HYDRATE: %s", kwargs)
        target_node_class = self.get_target_model()
        target_instance = target_node_class.hydrate(**kwargs)
        rel_data = kwargs.get(RELATIONSHIP_OBJECT_KEY)
        rel_data = rel_data[0] if rel_data else {}
        self.add(
            target_instance,
            **rel_data
        )

    def _relationship(self, other, **kwargs):
        """Instantiate a Relationship from self.instance to other with
        properties kwargs if any

        :param other:
        :param kwargs:
        :return:
        """
        from .models import Relationship
        if self.rel_property.model is None and kwargs:
            warnings.warn("Provided relationship properties without relationship model, "
                          "these properties will be ignored")
        rel_model_class = self.rel_property.model or Relationship
        rel_ins = rel_model_class(
            start_node=self.instance,
            end_node=other,
            **kwargs
        )
        return rel_ins

    def connect(self, other, **kwargs) -> None:
        """Create the relationship between self.instance and other.
        If the relationship is parametrized (ie comes with a model with properties),
        kwargs can be supplied to fill the relationship properties.

        :param Node other:
        """
        if not self.instance._is_in_neo:
            raise ValueError(f"You must first save the source object before connecting to another node ({self})")
        if not other._is_in_neo:
            raise ValueError(f"You must first save the target object before connecting to another node ({other})")
        self.add(other, **kwargs)
        self._save(other, **kwargs)

    def disconnect(self, other, **kwargs):
        self.remove(other)
        self._query(other, cypher_mode="DELETE", **kwargs)

    def update(self, other=None, **kwargs):
        self._query(other, cypher_mode="UPDATE", **kwargs)

    def get_target_model(self):
        return self.rel_property.get_target_node_class()

    def _query(self, other=None, cypher_mode="CREATE", **kwargs):
        if other is None and cypher_mode != "UPDATE":
            raise Exception("Must provide target node")
        ps = ParameterStore()
        source = self.instance
        source_data = source.kwargs_to_cypher(**source.get_id_dict())
        source_node_cypher = source.to_cypher_match(alias=START_NODE_ALIAS, param_store=ps, data=source_data)
        if other:
            target_data = other.kwargs_to_cypher(**other.get_id_dict())
            target = self.get_target_model()
            target_node_cypher = target.to_cypher_match(alias="target", param_store=ps, data=target_data)
        rel_pattern = self.rel_property.rel_pattern(alias="rel", param_store=ps, data=kwargs)
        if cypher_mode == "CREATE":
            query = f"""MATCH {source_node_cypher.repr()}
            MATCH {target_node_cypher.repr()}
            CREATE ({source_node_cypher.alias}) {rel_pattern.repr()} ({target_node_cypher.alias})
            """
        elif cypher_mode == "UPDATE":
            # rel pattern without kwargs, otherwise we would always create
            # a new relationship between source and target nodes
            rel_pattern = self.rel_property.rel_pattern(alias="rel", param_store=ps)
            new_data = ", ".join(
                f"{rel_pattern.alias}.{k} = {v}"
                for k, v in kwargs.items()
            )
            if other:
                query = f"""MATCH {source_node_cypher.repr()} {rel_pattern.repr()} {target_node_cypher.repr()}
                SET {new_data}
                """
            else:  # target all connected nodes
                query = f"""MATCH {source_node_cypher.repr()} {rel_pattern.repr()} ()
                SET {new_data}
                """
        elif cypher_mode == "DELETE":
            query = f"""MATCH {source_node_cypher.repr()} {rel_pattern.repr()} {target_node_cypher.repr()}
            DELETE {rel_pattern.alias}
            """
        else:
            raise ValueError(f"{cypher_mode} not valid for this method")
        connection.cypher(query, ps.params)

    def _save(self, other, **kwargs):
        self._query(other, cypher_mode="CREATE", **kwargs)
        other._is_in_neo = True
        other.is_sync = True

    def clear_all(self):
        """Delete all relationships"""
        ros = self.related_objects
        if ros is None:
            return
        for ro in ros.nodes():
            self.disconnect(ro)
        return ros

    def move_to(self, other):
        """Move relationship from one node to another
        In practice, delete all existing relationships and create a new one
        """
        with connection.transaction():
            old = self.clear_all()
            self.connect(other)
        return old
