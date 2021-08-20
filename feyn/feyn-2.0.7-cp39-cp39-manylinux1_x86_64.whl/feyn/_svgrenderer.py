from typing import Optional
from feyn import Model

from ._compatibility import detect_notebook


def show_model(model: Model, label: Optional[str] = None, update_display: bool = False):
    """Updates the display in a python notebook with the graph representation of a model

    Arguments:
        model {Model} -- The model to display.

    Keyword Arguments:
        label {Optional[str]} -- A label to add to the rendering of the model (default: {""})
    """

    if detect_notebook():
        from IPython.display import display, HTML, clear_output

        svg = _render_svg(model, label)
        display(HTML(svg))
        if update_display:
            clear_output(wait=True)
    else:
        status = f"{model.loss_value}"
        if label is not None:
            status = label
        print(status)


def _render_svg(model: Model, label: str = None):
    """Renders the graph representation of feyn models as SVG."""
    from feyn.plots._svg_toolkit import SVGGraphToolkit

    gtk = SVGGraphToolkit()
    gtk.add_graph(model, label=label)
    return gtk.render()


def layout_2d(graph):
    # This layout algo moves nodes to the latest layer possible (graphs are wide in the middle)
    lmap = {}
    layers = []
    out = graph[-1]
    layers.insert(0, [out])
    while True:
        layer = []
        for node in layers[0][
            :
        ]:  # iterate over a copy of the layer, it may be modified during iteration
            for ix in reversed(node.sources):
                if ix != -1:
                    pred = graph[ix]
                    if pred in lmap:
                        lmap[pred].remove(pred)

                    layer.append(pred)
                    lmap[pred] = layer

        if not layer:
            break
        layers.insert(0, layer)

    locs = [None] * len(graph)
    for layer, interactions in enumerate(layers):
        sz = len(interactions)
        center = (sz - 1) / 2
        for ix, interaction in enumerate(interactions):
            locs[interaction._index] = (layer, ix - center)

    return locs


def layout_2d_simple(graph):
    # This layout algo moves nodes to the earliest layer possible (graphs are wide towards the beginning)
    layers = [list() for _ in range(graph.depth + 2)]

    for node in graph:
        l = node.depth + 1
        layers[l].append(node)

    locs = [None] * len(graph)
    for layer, interactions in enumerate(layers):
        sz = len(interactions)
        center = (sz - 1) / 2
        for ix, interaction in enumerate(interactions):
            locs[interaction._index] = (layer, ix - center)

    return locs
