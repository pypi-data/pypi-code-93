from bs4 import Tag

__all__ = ["CustomHtmlTag", "Attrs", "PartialAttrs"]
        
######## General utility classes for tags and attrs

class CustomHtmlTag(Tag):
    "Base class defining as_str for a bs4.Tag (may be overridden)"
    def as_str(self):
        return str(self)#.prettify()

class Attrs(dict):
    "For passing into bs4.Tag constructor"
    def __init__(self, attr_dict):
        self.update({"attrs": attr_dict})

class PartialAttrs(Attrs):
    "Store a dict as an object property and pass a dict to create an attrs dict"
    def __init__(self, custom_attrs):
        super().__init__({**self.default_attrs, **custom_attrs})

    @property
    def default_attrs(self):
        return self._default_attrs if hasattr(self, "_default_attrs") else dict()
    
    @default_attrs.setter
    def default_attrs(self, default_dict):
        self._default_attrs = default_dict
