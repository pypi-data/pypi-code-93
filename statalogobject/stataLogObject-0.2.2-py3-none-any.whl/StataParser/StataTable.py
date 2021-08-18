from stataLogObject.Supports import ForestPlotInvalidAttributes, FOREST_DICT, methods_in_line
from stataLogObject.Configs import Table

from miscSupports import flip_list, write_markdown
from csvObject import write_csv


class StataTable:
    def __init__(self, raw_table, config):
        """
        A generic Stata Table

        :param raw_table: The raw table from StataRaw object
        :type raw_table: list[list]

        :param config: The attributes of the Table to configure with
        :type config: Table

        """

        # Raw table reference and the configuration for this table
        self._raw = raw_table
        self.config = config

        # Set the supporting table header values
        self.model_fit_names = self.config.mf.field_names()

        [setattr(self, f, self._set_mf(f)) for f in self.model_fit_names]
        self.model_fit = {f: getattr(self, f) for f in self.model_fit_names if getattr(self, f) is not None}

        # Extract phenotype, variable names, and the table body in row form
        self.table_col_names = self.config.body_iso.body_type.entry_names
        self.phenotype, self.body_values = self.config.body_iso.extract_body(self._raw)

        # Set the column data format
        [setattr(self, f"tb_{field}", [getattr(v, field) for v in self.body_values])for field in self.table_col_names]
        self.table_columns = {field: getattr(self, f"tb_{field}") for field in self.table_col_names}

    def __repr__(self):
        """Debug string"""
        return f"{self.phenotype}={len(self.table_columns['var_name'])}Var"

    def _set_mf(self, f):
        """Set a given model fit parameter if it has been set, else return None as this variable was optional"""
        if not getattr(self.config.mf, f):
            return None
        else:
            return getattr(self.config.mf, f).find_mf(self._raw, f)

    def body_to_csv(self, write_directory, write_name):
        """Write the body as a csv to the write directory called 'write_name'.csv"""
        write_csv(write_directory, write_name, list(self.table_columns.keys()), flip_list(self.table_columns.values()))

    def forest_format(self, exclusions=None):
        """Format the data as a forest plot would require, specifically designed for pyBlendFigures Forest"""
        if sum([1 if h in self.table_columns.keys() else 0 for h in FOREST_DICT.keys()]) != len(FOREST_DICT.keys()):
            raise ForestPlotInvalidAttributes(list(self.table_columns.keys()), FOREST_DICT.keys())

        rows_list = flip_list([self.table_columns[key] for key in FOREST_DICT.keys()])
        return [rows_list[i] for i in self._index_forest(exclusions)]

    def _index_forest(self, exclusions):
        """
        If we want to exclude variables, like _cons for example, then we want to remove these indexes from the isolate

        :param exclusions: An optional list of var names to exclude
        :type exclusions: list[str] | None

        :return: A list of indexes to isolate rows within
        :rtype: list[int]
        """
        if exclusions is None:
            return [i for i in range(len(self.table_columns['var_name']))]
        else:
            return [i for i, var in enumerate(self.table_columns['var_name']) if var not in exclusions]

    def in_line_methods_forest(self, rd=2, exclusions=None, md_path=None):
        """
        Create in lines methods equivalents for each variable in the style of forest

        :param rd: The amount of rounding to apply, defaults to 2
        :type rd: int

        :param exclusions: An optional list of var names to exclude
        :type exclusions: list[str] | None

        :param md_path: If set will create a file called 'methods' in this directory with this information
        :type md_path: str | Path

        :return: A list of strings of type 'VarName\t( RD=round(cf, rd), 95%CI: round(lb, rd); round(ub, rd) )\n'
        """

        rows = [methods_in_line(var_name, cf, lb, ub, rd) for var_name, cf, lb, ub in self.forest_format(exclusions)]
        if md_path is None:
            return rows
        else:
            write_markdown(md_path, "methods", rows)
            return rows
