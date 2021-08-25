from typing import Iterable
import ipywidgets as widgets
import ipyevents
import ipycanvas


def recursively_remove_from_dom(
    container_widget: widgets.Box,
    to_remove: Iterable[widgets.Widget] = (ipyevents.Event, ipycanvas.Canvas),
):
    assert hasattr(container_widget, "children")

    new_children = []

    for child in container_widget.children:
        if isinstance(child, to_remove):
            continue
        if isinstance(child, widgets.Box):
            child = recursively_remove_from_dom(child)
        new_children.append(child)
    container_widget.children = new_children
    return container_widget
