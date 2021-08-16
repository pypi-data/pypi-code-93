aliases = {
    # define aliases for control
    "orangecontrib.tomwer.widgets.control.DataListOW.DataListenerOW.DataListenerOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.control.DataListOW.DataListOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.control.DataListOW.DataSelectorOW.DataSelectorOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.control.DataListOW.DataValidatorOW.DataValidatorOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.control.DataListOW.DataWatcherOW.DataWatcherOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.control.DataListOW.FilterOW.FilterOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.control.NXTomomillOW.NXTomomillOW": "tomwer.core.process.control.nxtomomill.NxTomomillProcess",
    # define aliases for other
    "orangecontrib.tomwer.widgets.other.PythonScriptOW.OWPythonScript": "tomwer.core.process.script.python.PythonScript",
    # define aliases for reconstruction
    "orangecontrib.tomwer.widgets.reconstruction.AxisOW.AxisOW": "tomwer.core.process.reconstruction.axis.AxisProcess",
    "orangecontrib.tomwer.widgets.reconstruction.DarkRefAndCopyOW.DarkRefAndCopyOW": "tomwer.core.process.reconstruction.darkref.darkrefs.DarkRefs",
    "orangecontrib.tomwer.widgets.reconstruction.NabuOW.NabuOW": "tomwer.core.process.reconstruction.nabu.nabuslices.NabuSlices",
    "orangecontrib.tomwer.widgets.reconstruction.NabuVolumeOW.NabuVolumeOW": "tomwer.core.process.reconstruction.nabu.nabuvolume.NabuVolume",
    "orangecontrib.tomwer.widgets.reconstruction.FtseriesOW.FtseriesOW": "tomwer.core.process.reconstruction.ftseries.ftseries._Ftseries",
    "orangecontrib.tomwer.widgets.reconstruction.TofuOW.TofuOW": "tomwer.core.process.reconstruction.lamino.tofu.LaminoReconstruction",
    # define aliases for visualization
    "orangecontrib.tomwer.widgets.visualization.ImageStackviewerOW.ImageStackviewerOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.visualization.LivesliceOW.LivesliceOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.visualization.RadioStackOW.RadioStackOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.visualization.SampleMovedOW.SampleMovedOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.visualization.SinogramViewerOW.SinogramViewerOW": "tomwer.core.process.utils.IgnoreProcess",
    "orangecontrib.tomwer.widgets.visualization.SliceStackOW.SliceStackOW": "tomwer.core.process.utils.IgnoreProcess",
    # define aliases for edit
    "orange.widgets.tomwer.edit.DarkFlatPatchOW.DarkFlatPatchOW": "tomwer.core.process.edit.darkflatpatch.DarkFlatPatch",
    "orange.widgets.tomwer.edit.DarkFlatPatchOW.ImageKeyEditorOW": "tomwer.core.process.edit.imagekeyeditor.ImageKeyEditor",
}


# aliases used to avoid executing orange widgets directly (and avoid Qt stuff...)
# NOTES:
#
# - dark ref copy is not managed by the process application. For now we don't have any process consistancy and we have to create each time a new process.
#
# Tested:
#
# - NXTomomill
# - Darkref
# - Axis
# - Nabu
# - PythonScript
#
# For now Several processes are just 'ignore' by the pipeline:
#
