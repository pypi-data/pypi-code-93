from typing import Any, Text, List, Dict


def adding_items_to_lookup_tables(
    title: Text, item: Text, existing_lookup_tables: List[Dict[Text, List[Text]]]
) -> None:
    """Takes a list of lookup table dictionaries.  Finds the one associated
    with the current lookup, then adds the item to the list.

    Args:
        title: Name of the lookup item.
        item: The lookup item.
        existing_lookup_tables: Existing lookup items that will be extended.
    """
    lookup_matches = [table for table in existing_lookup_tables if table["name"] == title]
    if not lookup_matches:
        existing_lookup_tables.append({"name": title, "elements": [item]})
    else:
        lookup_elements = lookup_matches[0]["elements"]
        lookup_elements.append(item)
