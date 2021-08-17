from pydoc import locate

from openfabric_pysdk.manifest import manifest


class Util:
    @staticmethod
    def get_concept_definition(selection):
        concept_id = manifest.get(selection).split('/')[1]
        schema = manifest.get(selection).split('/')[0]
        return f"{schema}/{concept_id}"

    @staticmethod
    def import_class(name):
        return locate(name.__module__ + "." + name.__name__)
