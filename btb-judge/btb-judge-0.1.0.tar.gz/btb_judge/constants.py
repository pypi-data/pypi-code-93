MAX_MOVES = 200
SIZE = 7
MAX_HEIGHT = 5
REASONS = {
    'INVALID_FORMAT_OR_TIMEOUT': 'Invalid move format or Request timed out',
    'INVALID_POINTS': 'Invalid points',
    'INVALID_CELL': 'Invalid move - moved to an occupied cell',
    'UNREACHABLE_CELL': 'Invalid move - moved to a cell with unreachable height',
    'INVALID_CURRENT_MB': 'current in M&B was incorrect',
    'INVALID_BUILD_MB': 'build in M&B was incorrect',
    'INVALID_CURRENT_PB': 'current in P&B was incorrect',
    'INVALID_BUILD_PB': 'build in P&B was incorrect',
}
