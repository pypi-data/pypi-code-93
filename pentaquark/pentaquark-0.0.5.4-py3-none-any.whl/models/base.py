"""
"""
from dataclasses import dataclass

from pentaquark.constants import SEPARATOR, RELATIONSHIP_OBJECT_KEY, MANAGER_ATTRIBUTE_NAME
from pentaquark.lookups import LOOKUPS
from pentaquark.models.managers import Manager
from pentaquark.properties import Property
from pentaquark.exceptions import PentaQuarkConfigurationError

RESERVED_KEYWORDS = LOOKUPS + [
    SEPARATOR,
    RELATIONSHIP_OBJECT_KEY,
    MANAGER_ATTRIBUTE_NAME,
]


@dataclass
class MetaModelOptions:
    label: str = None
    is_abstract: bool = False
    manager_class: object = Manager
    id_property: str = "id"
    help_text: str = ""
    unique_together: tuple = ()
    allow_undeclared_properties: bool = False


class PropertyModelBase(type):

    def __new__(mcs, name, bases, attrs):
        """Metaclass for Models

        - Create dict of properties
            - Check property name is not a reserved keyword
        - Parse Meta options

        :param args:
        :param kwargs:
        """
        from pentaquark.properties.relationships import RelationshipProperty
        # deal with properties and relationships
        properties = {}
        for attr_name, attr in attrs.items():
            if attr_name in RESERVED_KEYWORDS:
                raise PentaQuarkConfigurationError(f"'{attr_name}' is a reserved keyword")
            if isinstance(attr, Property) and not isinstance(attr, RelationshipProperty):
                if SEPARATOR in attr_name:
                    raise PentaQuarkConfigurationError(f"'{attr_name}' contains {SEPARATOR}")
                properties[attr_name] = attr
                if hasattr(attr, "bind_to_model"):
                    attr.bind_to_model(attr_name)
                continue
        # manage inheritance
        for b in bases:
            if hasattr(b, "_properties"):
                for pn, prop in b._properties.items():
                    # prevent changing the Property reference
                    # when base (b) has same metaclass
                    if pn in properties:
                        continue
                    properties[pn] = prop
        attrs["_properties"] = properties

        # meta class
        meta_options = MetaModelOptions()
        label = None
        if 'Meta' in attrs:
            meta = attrs.pop('Meta')
            if hasattr(meta, 'label'):
                label = meta.label
            if hasattr(meta, "is_abstract"):
                is_abstract = meta.is_abstract
                meta_options.is_abstract = is_abstract
            if hasattr(meta, "id_property"):
                meta_options.id_property = meta.id_property
            if hasattr(meta, "manager_class"):
                meta_options.manager_class = meta.manager_class
            if hasattr(meta, "allow_undeclared_properties"):
                meta_options.allow_undeclared_properties = meta.allow_undeclared_properties
            if hasattr(meta, "unique_together"):
                meta_options.unique_together = meta.unique_together
        meta_options.label = label or name
        attrs["_meta"] = meta_options

        return type.__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        cls.q = cls._meta.manager_class(cls)
        super().__init__(name, bases, attrs)
