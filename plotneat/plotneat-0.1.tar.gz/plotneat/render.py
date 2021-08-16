import plotly.graph_objects as go
import plotly.io as pio
from IPython.display import Image

from .plotly_addons import prepare_minimalistic_show


def render(fig, out="png", minimalistic=True, height=None, width=None):
    """
    Renders a figure in a chosen format.

    Inputs
    ----------
    fig : plotly.graph_objects.Figure
        Figure to render

    minimalistic : Boolean
        If True, makes a minimalistic rendering of the plot
        Default : True

    out : str
        Renderer to use.
        Options:
            - Filename
            - Format (Plotly: "png","jpeg","browser", ...)

    height, width : int
        Height and width of the rendered plot
        Default: None (uses the initial figure size)

    Outputs
    ----------
    None
    """

    if isinstance(fig, go.Figure):
        if height is None:
            height = fig["layout"]["height"]
        if width is None:
            witdth = fig["layout"]["width"]

        scale = 1
        if minimalistic is True:
            kwargs_show = prepare_minimalistic_show(fig)
        else:
            kwargs_show = dict()

        if out in ["png", "jpeg", "svg", "pdf"]:
            fig.to_image(
                format=out,
                engine="kaleido",
                width=witdth,
                height=height,
                scale=scale,
            )

        elif out.endswith(".json"):
            fig.write_json(out)

        elif (
            out.endswith(".png")
            or out.endswith(".jpeg")
            or out.endswith(".svg")
            or out.endswith(".pdf")
        ):
            fig.write_image(
                out,
                engine="kaleido",
                width=witdth,
                height=height,
                scale=scale,
            )

        elif out.endswith(".html"):
            fig.write_html(out)

        elif out == "Image":
            img_bytes = fig.to_image(
                format="png",
                width=witdth,
                height=height,
                scale=scale,
            )
            Image(img_bytes)

        else:
            fig.show(out, **kwargs_show)

    else:
        raise Exception("Unknown figure type")
