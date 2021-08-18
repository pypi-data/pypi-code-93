from typing import List

from .schema_utils import handle_name, handle_major_name, MergeType


class SchemaException(Exception):
    ...


def check_source_schema(source_dict: dict) -> List[str]:
    """
    Check the names in the schema to see if we can use them in Databricks

    Parameters
    source_dict
    proposed_source : dict
        The schema loaded from the dbt folder structure for a particular source

    Raises
    ------
    SchemaException
        If there are any issues, raise an exception
    """
    errors = []

    if source_dict["schema"] != handle_major_name(source_dict["schema"]):
        errors.append(
            f"Source {source_dict['name']}: "
            f"Schema named '{source_dict['schema']}' is not possible in "
            f"Databricks. Suggested name: {handle_major_name(source_dict['schema'])}"
            )

    for _, table in source_dict.get("tables", {}).items():
        if table["name"] != handle_major_name(table["name"]):
            errors.append(
                f"Source {source_dict['name']}: "
                f"Table named '{table['name']}' is not possible in "
                f"Databricks. Suggested name: {handle_major_name(table['name'])}"
                )

        # Check that the join type is understood
        if table.get("join", {}).get("type") is not None:
            if not MergeType.check_type(table["join"]["type"]):
                errors.append(
                    f"Source {source_dict['name']}, "
                    f"table {table['name']}: "
                    f"Trying to join using the type {table['join']['type']}, "
                    f"but this isn't one of the possible options: "
                    f"{MergeType.all_types()}"
                )

        # Check that the columns we want to join on make sense
        column_names = [c["name"] for c in table["columns"]]
        if table.get("join", {}).get("column") is not None:
            join_columns = table["join"]["column"].split(",")
            for col in join_columns:
                if col not in column_names and f"`{col}`" not in column_names:
                    errors.append(
                        f"Source {source_dict['name']}, "
                        f"table {table['name']}: "
                        f"Trying to join on column {join_columns}, "
                        f"but {col} isn't one of the columns on the table: "
                        f"{column_names}"
                        )

        for column in table.get("columns", []):
            sub_errors = []
            has_backticks = \
                column["name"].startswith("`") and column["name"].endswith("`")
            no_backticks = column["name"].strip("`")

            # Produce one suggested name, regardless of the number of errors
            suggested_name, wrapped_name = \
                handle_name(no_backticks), handle_name(no_backticks)

            if no_backticks != suggested_name:
                sub_errors.append(
                    f"Source {source_dict['name']}, table {table['name']}: "
                    f"Column named '{column['name']}' is not possible in "
                    f"Databricks as it has illegal characters."
                    )

            # [ and ] causes dbt testing SQL to not render correctly
            if ("[" in column["name"] or "]" in column["name"]) \
                    and not has_backticks:
                sub_errors.append(
                    f"Source {source_dict['name']}, table {table['name']}: "
                    f"Column named '{column['name']}' has '[' and/or ']' "
                    f"characters, which causes issues with DBT testing. "
                    f"Remove those, or add quotes and backticks to the name "
                    f"in the schema yml file to resolve this."
                )
                suggested_name = \
                    suggested_name.replace("[", "").replace("]", "")

            # Columns starting with _ are reserved for engineering columns
            if column["name"].startswith("_") \
                    or column["name"].startswith("`_") \
                    or wrapped_name.startswith("_") \
                    or wrapped_name.startswith("`_"):
                sub_errors.append(
                    f"Source {source_dict['name']}, table {table['name']}: "
                    f"Column named '{column['name']}' starts with '_', "
                    f"which is reserved for Ingenii Engineering columns."
                )
                suggested_name = suggested_name.replace("_", "", 1)
                wrapped_name = wrapped_name.replace("_", "", 1)

            if sub_errors:
                errors.extend([
                    se +
                    f" Suggested name '`{wrapped_name}`' including the " +
                    f"quotes, or {suggested_name}"
                    for se in sub_errors
                ])

    if errors:
        raise SchemaException("\n".join(errors))
