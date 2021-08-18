def handle_name(raw_name: str) -> str:
    """
    Remove or replace Databricks forbidden characters: ' ,;{}()\n\t='

    Parameters
    ----------
    raw_name : str
        The raw name

    Returns
    -------
    str
        An acceptable version of the name
    """
    return raw_name.replace(" ", "_").replace(",", "").replace(";", "") \
                   .replace("{", "[").replace("}", "]") \
                   .replace("(", "[").replace(")", "]") \
                   .replace("\n", "").replace("\t", "_").replace("=", "-")


def handle_major_name(raw_name: str) -> str:
    """
    More restrictions for 'major' names, such as schema and table names.
    Column names are more permissive

    Parameters
    ----------
    raw_name : str
        The raw name containing potentially illegal characters

    Returns
    -------
    str
        The new name, cleaned of any problem containers
    """
    return handle_name(raw_name).replace("-", "_")


def schema_as_string(schema_list: list) -> str:
    """
    Takes a dictionary object of a schema, and turns it into string form to be
    used in SQL commands

    Parameters
    ----------
    schema_list : list
        The table schema, which requires both 'name' and 'data_type' keys

    Returns
    -------
    str
        The schema in SQL form
    """
    return ", ".join([
        f"{handle_name(s['name'])} {s['data_type']}"
        for s in schema_list
    ])


class MergeType:
    """
    Class to ensure that the correct merge types are used in functions. When
    we pass a merge type to a function such as merge_dataframe_into_table, we
    can use this class to ensure no unintended consequences
    """
    MERGE_DATE_ROWS = "merge_date_rows"
    MERGE_UPDATE = "merge_update"
    MERGE_INSERT = "merge_insert"
    INSERT = "insert"

    @classmethod
    def all_types(cls):
        return [
            cls.MERGE_DATE_ROWS, cls.MERGE_UPDATE,
            cls.MERGE_INSERT, cls.INSERT
        ]

    @classmethod
    def check_type(cls, type_to_check):
        return type_to_check in cls.all_types()
