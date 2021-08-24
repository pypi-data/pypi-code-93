from sdccli.printer import print_list as _print_list, print_item as _print_item


def formats():
    return {
        "panelList": print_panel_list,
        "panel": print_panel,
    }


_list_keys = ["id", "name", "type", "queryCount"]
_item_keys = ["id", "name", "type", "queryCount"]


def print_panel(panel):
    queries_parent = panel["advancedQueries"] if "advancedQueries" in panel else panel["basicQueries"]
    panel["queryCount"] = len(queries_parent)
    _print_item(panel, _item_keys)

    print("queries:")
    queries = [{"id": id, "query": query.get("query") or ", ".join([q["id"] for q in query.get('metrics')])} for
               id, query in enumerate(queries_parent)]
    _print_list(queries, ["", "id", "query"])


def print_panel_list(panel_list):
    for panel in panel_list:
        if "queryCount" in panel:
            panel["queryCount"] = len(panel["advancedQueries"]) if "advancedQueries" in panel else len(
                panel["basicQueries"])

    _print_list(panel_list, _list_keys)
