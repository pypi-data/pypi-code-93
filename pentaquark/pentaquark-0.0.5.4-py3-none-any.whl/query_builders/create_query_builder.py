import logging
import collections.abc

from pentaquark.db import connection
from .query_builder import QueryBuilder
from ..exceptions import PentaQuarkObjectDoesNotExistError

logger = logging.getLogger(__name__)


class CreateQueryBuilder(QueryBuilder):
    def create(self, ins=None, extra_kwargs=None, **kwargs):
        """Create a db object
        You must provide either ins or kwargs.

        :param Node ins: Node instance to be created in db
        :param **kwargs: properties of object to be created
        """
        # are we creating from instance or kwargs?
        # we use this information to know from where to read relationship data
        # TODO: probably not required
        from_ins = True
        if ins is None:
            from_ins = False
            ins = self.model(**kwargs)
        ins.set_defaults()
        properties = ins.get_property_kwargs()
        ins.check_required_properties(properties)
        with connection.transaction():
            # create instance
            self._create(**properties)
            ins.is_sync = True
            ins._is_in_neo = True
            # if relationships, add relationships
            for rn, rel_property in ins._relationships.items():
                related_obj = None
                if from_ins:  # get relationship from instance cached_properties
                    try:
                        related_obj = getattr(ins, rn).get()
                    except PentaQuarkObjectDoesNotExistError:
                        pass
                elif rn in kwargs:  # try to get relationship object from kwargs
                    related_obj = kwargs[rn]
                elif key := self._related_obj_id_in_kwargs(kwargs, rn):  # get target node id
                    related_obj = self._get_related_object(rel_property, kwargs[key])
                if related_obj:
                    rel_manager = getattr(ins, rn)
                    if isinstance(related_obj, collections.abc.Iterable):
                        for ro in related_obj:
                            rel_manager.connect(ro)
                    else:
                        rel_manager.connect(related_obj)
            ins._is_in_neo = True
            ins._is_sync = True
            ins.post_save(extra_kwargs=extra_kwargs)
            ins.post_create(extra_kwargs=extra_kwargs)
        return ins

    @classmethod
    def _related_obj_id_in_kwargs(cls, kwargs, key):
        key_with_id = f"{key}_id"
        if key_with_id in kwargs:
            return key_with_id
        return None

    def _get_related_object(self, rel_property, target_id):
        target_model = rel_property.get_target_node_class()
        target_id_prop = target_model._properties[target_model.get_id_property_name()]
        target_instance = target_model.q.match(
            **{target_model.get_id_property_name(): target_id_prop.to_cypher(target_id)}
        ).one()
        return target_instance

    def _create(self, **kwargs):
        """Perform Cypher CREATE operation

        :param kwargs: cypher-ready parameters
        :return: None
        """
        label = self.model.get_label()
        cypher = f"CREATE (n:{label})\n"
        cypher += "SET " + ",".join(f'n.{k}=${k}' for k in kwargs)
        connection.cypher(cypher, kwargs)

    def merge(self, ins, extra_kwargs=None):
        self._merge(ins, extra_kwargs=extra_kwargs)

    def _merge(self, ins, extra_kwargs=None):
        # transaction already opened in merge method
        label = self.model.get_label()
        id_property_name = self.model.get_id_property_name()
        properties = ins.get_property_kwargs()
        ins.check_required_properties(properties)
        cypher = f"MATCH (n:{label} {{{id_property_name}: ${id_property_name} }})\n"
        cypher += "SET " + ",".join(f'n.{k}=${k}' for k in properties)
        params = ins.get_property_kwargs()
        connection.cypher(cypher, params)
        ins.post_save(extra_kwargs=extra_kwargs)

    def _build_query(self):
        pass
