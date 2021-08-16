from .exporter import Exporter, ExportResult
from .exporter_pool import ExporterPool
from ..exceptions import MissingModuleError

__all__ = ["ExportResult", "Exporter", "ExporterPool"]
_addons = ["FileExporter", "MongoDBExporter", "ElasticSearchExporter",
           "PostgreSQLExporter"]

for a in _addons:
    try:
        filename = f"exporters.exporter_{a.replace('Exporter', '').lower()}"
        mod = __import__(filename, globals(), fromlist=[a], level=2)
        globals()[a] = getattr(mod, a)
    except MissingModuleError:
        continue
    else:
        __all__.append(a)
