import logging

from pentaquark.models import PropertyModelBase, Node

logger = logging.getLogger(__name__)


class RelationshipMeta(PropertyModelBase):
    pass


class Relationship(metaclass=RelationshipMeta):
    def __init__(self, start_node, end_node, **kwargs):
        if not isinstance(start_node, Node):
            raise ValueError(f"start_node must be a Node, got {start_node.__class__}")
        self.start_node = start_node
        self.end_node = end_node
        self.initial_data = kwargs

        # TODO: duplicated code with Node.__init__, can this be factorized in some way?
        self.cached_properties = {}
        self._is_in_neo = False
        self.is_sync = False

        properties_iter = self._properties
        for fn, prop in properties_iter.items():
            prop.bind_to_instance(self)
            val = kwargs.pop(fn, None)
            if val is None:
                # if prop.required:
                #     raise ValueError(f"Field {fn} is mandatory but no value provided")
                if hasattr(prop, "source"):
                    val = getattr(self, prop.source, None) or kwargs.get(prop.source, None)
                elif prop.default:
                    try:
                        val = prop.default()
                    except TypeError:  # not callable
                        val = prop.default
            setattr(self, fn, val)

    def __repr__(self):
        return f"<Relationship from={self.start_node} -> to={self.end_node} ({self.cached_properties})>"
