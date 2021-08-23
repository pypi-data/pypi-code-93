# -*- coding: utf-8 -*-

from pathlib import Path
import sys

# Make sure it's running in Python 3.6 as it's required by tksheet.
if sys.version_info[0] < 2 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    sys.exit('ERROR: This program require Python 3.6 or newer. You are running %s' %
             '.'.join(map(str, sys.version_info[0:3])))

PROGRAM_NAME = 'Process Memory Monitor'
VERSION = '0.0.2'
LABEL_WIDTH = 15
COMBO_WIDTH = 50
FIGURE_DPI = 100
DEFAULT_REFRESH_INTERVAL = 10

#sheet column numbers
SHEET_PID_COL = 0
SHEET_CPU_COL = 1
SHEET_RSS_COL = 2
SHEET_CMD_COL = 3
SHEET_LAST_UPDATED_COL = 4


__resource_path__ = Path(__file__).parent / 'resources'
__icon__ = __resource_path__ / 'proc-mem-monitor-icon.gif'

STATUS_CODES = {

}