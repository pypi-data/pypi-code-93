"""Classes related to yaml processing"""
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

_YAML_LINE_WIDTH = 120


class _MyYAML(YAML):
    """Use the ruamel yaml thing to render strings, which is what they don't like.
    See https://yaml.readthedocs.io/en/latest/example.html#output-of-dump-as-a-string"""
    def dump(self, data, stream=None, **kw):  # pylint: disable=W0221,R1710
        """Dump into a string"""
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


def get_yaml() -> _MyYAML:
    """Return an instance of the Yaml dumper.
    Usage get_yaml().dump({'a': 'b'})
    """
    yaml = _MyYAML()
    yaml.width = _YAML_LINE_WIDTH  # pylint: disable=C0201,W0201
    return yaml
