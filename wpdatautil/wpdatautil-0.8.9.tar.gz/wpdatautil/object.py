"""object utilities."""


def fullname(obj: object) -> str:
    """Return the full name of the given object using its module and qualified class names."""
    # Ref: https://stackoverflow.com/a/66508248/
    module_name, class_name = obj.__class__.__module__, obj.__class__.__qualname__
    if module_name in (None, str.__class__.__module__):
        return class_name
    return module_name + "." + class_name
