from .server import GenTableMappingFromSourceTables, GenSparkSqlFromLocalMappingTables
from .config import init

init()

__all__ = [
    'GenTableMappingFromSourceTables',
    'GenSparkSqlFromLocalMappingTables'
]
