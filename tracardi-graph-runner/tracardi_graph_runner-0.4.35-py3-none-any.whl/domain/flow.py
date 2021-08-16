from typing import Optional
from tracardi_graph_runner.domain.flow_graph_data import FlowGraphData
from tracardi_graph_runner.domain.named_entity import NamedEntity


class Flow(NamedEntity):
    description: Optional[str] = None
    flowGraph: Optional[FlowGraphData] = None
    enabled: Optional[bool] = True
