"""Sphinx configuration file for TSSW package"""

from documenteer.conf.pipelinespkg import *  # noqa
import lsst.ts.idl  # noqa

project = "ts_idl"
html_theme_options["logotext"] = project  # noqa
html_title = project
html_short_title = project
doxylink = {}  # Avoid warning: Could not find tag file _doxygen/doxygen.tag

intersphinx_mapping["ts_xml"] = ("https://ts-xml.lsst.io", None)  # noqa
