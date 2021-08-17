from sensiml.client import SensiML

try:
    from sensiml.widgets import DashBoard

    __all__ = ["SensiML", "DashBoard"]
except ImportError:
    # dev version fails here so lets import a dummy
    __all__ = ["SensiML"]


try:
    from IPython.core.display import HTML

    display(HTML("<style>.container { width:90% !important; }</style>"))
except:
    pass

name = "sensiml"
__version__ = "2021.2.0"
