from tracardi_graph_runner.domain.debug_info import DebugInfo
from tracardi_graph_runner.domain.entity import Entity
from tracardi_graph_runner.domain.flow import Flow
from tracardi_graph_runner.domain.flow_history import FlowHistory
from tracardi_graph_runner.utils.dag_error import DagGraphError
from tracardi_graph_runner.utils.dag_processor import DagProcessor
from tracardi_graph_runner.utils.flow_graph_converter import FlowGraphConverter


class WorkFlow:

    def __init__(self, flow_history: FlowHistory, session, profile, event):
        self.flow_history = flow_history
        self.profile = profile
        self.session = session
        self.event = event

    async def invoke(self, flow: Flow, debug=False) -> DebugInfo:

        if self.event is None:
            raise DagGraphError(
                "Flow `{}` has no context event defined.".format(
                    flow.id))

        if not flow.flowGraph:
            raise DagGraphError("Flow {} is empty".format(flow.id))

        if self.flow_history.is_acyclic(flow.id):

            # Convert Editor graph to exec graph
            converter = FlowGraphConverter(flow.flowGraph.dict())
            dag_graph = converter.convert_to_dag_graph()
            dag = DagProcessor(dag_graph)

            try:
                exec_dag = dag.make_execution_dag(debug=debug)
            except DagGraphError as e:
                raise DagGraphError("Flow `{}` returned the following error: `{}`".format(flow.id, str(e)))

            # Init and run with event
            await exec_dag.init(flow, self.flow_history, self.event, self.session, self.profile)

            debug_info = await exec_dag.run(payload={},
                                            flow_id=flow.id,
                                            event_id=self.event.id
                                            )

            return debug_info
