# -*- coding: utf-8 -*-
import logging
from typing import Dict, List, Union, Optional

try:
    from pandas import DataFrame
except ImportError:
    pass

logger = logging.getLogger(__name__)


class CsvOutput:
    """CsvOutput class enabling writing to csv files.

    Args:
        csv_paths (List[str]): Paths to csvs (one per tab)
        tabs (Dict[str, str]): Dictionary of mappings from internal name to spreadsheet tab name
        updatetabs (List[str]): Tabs to update
    """

    def __init__(self, csv_paths, tabs, updatetabs):
        # type: (List[str], Dict[str, str], List[str]) -> None
        self.csv_paths = csv_paths
        self.tabs = tabs
        self.updatetabs = updatetabs

    def update_tab(self, tabname, values, hxltags=None):
        # type: (str, Union[List, DataFrame], Optional[Dict]) -> None
        """Update tab with values

        Args:
            tabname (str): Tab to update
            values (Union[List, DataFrame]): Either values in a list of dicts or a DataFrame
            hxltags (Optional[Dict]): HXL tag mapping. Defaults to None.

        Returns:
            None
        """
        if tabname not in self.updatetabs:
            return
        sheetname = self.tabs[tabname]
        try:
            del self.workbook[sheetname]
        except KeyError:
            pass
        tab = self.workbook.create_sheet(sheetname)
        if isinstance(values, list):
            for i, row in enumerate(values):
                for j, value in enumerate(row):
                    tab.cell(row=i+1, column=j+1, value=value)
        else:
            headers = list(values.columns.values)
            tab.append(headers)
            if hxltags:
                tab.append([hxltags.get(header, '') for header in headers])
            for r in dataframe_to_rows(values, index=False, header=False):
                tab.append(r)
