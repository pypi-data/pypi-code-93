from sensiml.datamanager.pipeline import PipelineStep


class QueryCall(PipelineStep):
    """The base class for a query call."""

    def __init__(self, name):
        super(QueryCall, self).__init__(name=name, step_type="QueryCall")
        self._query = None
        self._use_session_preprocessor = True
        self._outputs = None

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, query):
        self._query = query

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        self._outputs = outputs

    @property
    def use_session_preprocessor(self):
        return self._use_session_preprocessor

    @use_session_preprocessor.setter
    def use_session_preprocessor(self, value):
        self._use_session_preprocessor = value

    def _to_dict(self):
        query_dict = {}
        query_dict["name"] = self.query.name
        query_dict["type"] = "query"
        query_dict["outputs"] = self.outputs
        query_dict["use_session_preprocessor"] = self.use_session_preprocessor

        return query_dict
