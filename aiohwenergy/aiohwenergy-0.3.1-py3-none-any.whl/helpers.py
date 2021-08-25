"""Helper functions."""


def generate_attribute_string(self, attributes):
    """Return a string of available attributes."""
    output = ""
    for attribute in attributes:
        output += f"{attribute}: {getattr(self, attribute)}\n"
    return output
