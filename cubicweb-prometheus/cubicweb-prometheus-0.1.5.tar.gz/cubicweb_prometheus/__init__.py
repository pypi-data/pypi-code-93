"""cubicweb-prometheus application package

Exporting prometheus metrics
"""


def includeme(config):
    config.include(".views")
