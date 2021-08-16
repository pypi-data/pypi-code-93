from datetime import datetime

from pentaquark.models.nodes import NodeMeta, Node
from pentaquark.properties import RelationshipPropertyOut, StringProperty, DateTimeProperty, UUIDProperty


class StateMeta(NodeMeta):
    """Automatically adds `current_state` and `states` relationship property
    towards `cls.state_class` state node.
    """

    def __new__(mcs, name, bases, attrs):
        state_class_name = attrs.get("state_class").__name__
        attrs["current_state"] = RelationshipPropertyOut(
            "HAS_STATE_CURRENT", state_class_name
        )
        attrs["states"] = RelationshipPropertyOut(
            "HAS_STATE", state_class_name
        )
        return NodeMeta.__new__(mcs, name, bases, attrs)


class StateNode(Node):
    version = StringProperty()
    created_at = DateTimeProperty(default=datetime.now)

    id_property = "version"


class VersionedNode(Node, metaclass=StateMeta):
    """Override `save` method to create state nodes on create and update"""
    state_class = StateNode
    uid = UUIDProperty()

    id_property = "uid"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watched_properties = self.state_class._properties
        # getattr(self, "current_state").bind_rel(self, name="current_state")
        # getattr(self.__class__, "current_state").bind_rel(self, name="current_state")

    def create_new_state(self, version=None):
        """Create state node from saved instance"""
        if not self._is_in_neo:
            raise RuntimeError("You must first save your object before trying to create a state")
        if version is None:
            version = datetime.now().timestamp()
        params = {
            **{
                k: getattr(self, k, None)
                for k in self._watched_properties
            },
            **{
                "version": version
            },
        }
        current_state = self.state_class(**params)
        current_state.save()
        self.current_state.clear_all()  # remove connection to previous current_state
        self.current_state.connect(current_state)  # create connection to new current_state
        self.states.connect(current_state)  # create connection to state history

    def post_save(self, extra_kwargs=None) -> None:
        super().post_save(extra_kwargs)
        version = extra_kwargs.get("version") if extra_kwargs else None
        self.create_new_state(version=version)

    def state_at(self, version):
        """Get state for `version` or at `date`

        :param str version:
        """
        states = self.states.filter(
            version=version,
        )
        if states:
            return states[0]
        return None
