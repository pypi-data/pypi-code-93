from sensiml.datamanager.pipeline import PipelineStep


class FeatureFileCall(PipelineStep):
    """The base class for a featurefile call"""

    def __init__(self, name):
        super(FeatureFileCall, self).__init__(name=name, step_type="FeatureFileCall")
        self._featurefile = None
        self._data_columns = None
        self._group_columns = None
        self._label_column = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def data_columns(self):
        return self._data_columns

    @data_columns.setter
    def data_columns(self, value):
        self._data_columns = value

    @property
    def group_columns(self):
        return self._group_columns

    @group_columns.setter
    def group_columns(self, value):
        if isinstance(value, list):
            self._group_columns = value
        else:
            print("Group columns must be a list of strings.")

    @property
    def label_column(self):
        return self._label_column

    @label_column.setter
    def label_column(self, value):
        if isinstance(value, str):
            self._label_column = value
        else:
            print("Label Column must be a string")

    @property
    def featurefile(self):
        return self._featurefile

    @featurefile.setter
    def featurefile(self, featurefile):
        self._featurefile = featurefile

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        self._outputs = outputs

    def _to_dict(self):
        featurefile_dict = {}
        featurefile_dict["name"] = self.name
        featurefile_dict["type"] = "featurefile"
        featurefile_dict["data_columns"] = getattr(self, "_data_columns")
        featurefile_dict["group_columns"] = getattr(self, "_group_columns")
        featurefile_dict["label_column"] = getattr(self, "_label_column")
        featurefile_dict["outputs"] = getattr(self, "_outputs")
        return featurefile_dict
