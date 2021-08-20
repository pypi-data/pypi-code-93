# coding: utf8

__all__ = ["Definition"]
from refinitiv.dataplatform.core.log_reporter import LogReporter
from refinitiv.dataplatform.legacy.tools import DefaultSession
from refinitiv.dataplatform.content.data_grid._fundamental_class import Fundamental


class Definition(LogReporter):
    def __init__(
        self,
        universe,
        fields,
        parameters=None,
        field_name=None,
        closure=None,
        session=None,
    ):
        self.session = session or DefaultSession.get_default_session()
        if self.session is None:
            raise AttributeError("A Session must be started")

        super().__init__(logger=self.session)
        self.universe = universe
        self.fields = fields
        self.parameters = parameters
        self.field_name = field_name
        self.closure = closure

    def get_data(self, session=None, on_response=None):
        fundamental_class = Fundamental(session=session, on_response=on_response)
        response = fundamental_class._get_data(
            universe=self.universe,
            fields=self.fields,
            parameters=self.parameters,
            field_name=self.field_name,
            closure=self.closure,
        )

        return response

    async def get_data_async(self, session=None, on_response=None):
        fundamental_class = Fundamental(session=session, on_response=on_response)
        response = await fundamental_class._get_data_async(
            universe=self.universe,
            fields=self.fields,
            parameters=self.parameters,
            field_name=self.field_name,
            closure=self.closure,
        )
        return response
