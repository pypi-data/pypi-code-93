from sensiml.datamanager.pipeline import PipelineStep


class CaptureFileCall(PipelineStep):
    """The base class for a featurefile call"""

    def __init__(self, name):
        super(CaptureFileCall, self).__init__(name=name, step_type="CaptureFileCall")
        self.name = name
        self._data_columns = None
        self._group_columns = ["Subject"]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, list):
            name = [name]
        self._name = name

    @property
    def data_columns(self):
        return self._data_columns

    @data_columns.setter
    def data_columns(self, value):
        self._data_columns = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        self._outputs = outputs

    @property
    def group_columns(self):
        return self._group_columns

    @group_columns.setter
    def group_columns(self, value):
        print("Capture files default to Subject.")

    def _to_dict(self):
        capturefile_dict = {}
        capturefile_dict["name"] = self.name
        capturefile_dict["type"] = "capturefile"
        capturefile_dict["data_columns"] = getattr(self, "_data_columns")
        capturefile_dict["group_columns"] = getattr(self, "_group_columns")
        capturefile_dict["outputs"] = getattr(self, "_outputs")
        return capturefile_dict
