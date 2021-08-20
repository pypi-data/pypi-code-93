from jelastic_client.env_status import EnvStatus
from jelastic_client.node import Node, Nodes


def get_nodes_from_env_info(env_info: dict) -> Nodes:
    nodes = []
    raw_nodes = env_info["nodes"] if hasattr(
        env_info, "nodes") and env_info["nodes"] is not None else []
    for raw_node in raw_nodes:
        node = Node(
            int_ip=raw_node["intIP"], node_type=raw_node["nodeType"], node_group=raw_node["nodeGroup"])
        nodes.append(node)
    return nodes


class EnvInfo:

    def __init__(self, env_info: dict):
        self._info = env_info
        self._nodes = get_nodes_from_env_info(env_info)

    def status(self) -> EnvStatus:
        return EnvStatus(self._info["env"]["status"])

    def env_name(self) -> str:
        return self._info["env"]["envName"]

    def nodes(self) -> Nodes:
        return self._nodes

    def is_running(self) -> bool:
        return self.status() is EnvStatus.Running

    def exists(self) -> bool:
        return self.status() is not EnvStatus.NotExists and self.status() is not EnvStatus.Unknown

    # TODO: test this:
    #   1. feed the class with some test dictionary corresponding to real-world
    #   2. confront get_node_ips with the previously fed env info
    # - given a nodeGroup, fetch the related IPs
    # - given a nodeType, fetch the related IPs
    # - give a nodeType AND a nodeGroup, fetch the related IPs
    def get_node_ips(self, node_group: str = None, node_type: str = None) -> list[str]:
        env_nodes = self._nodes

        node_ips_with_node_group = []
        if node_group is not None:
            node_ips_with_node_group = [env_node.int_ip for env_node in env_nodes if
                                        env_node.node_group == node_group]
            if node_type is None:
                return node_ips_with_node_group

        node_ips_with_node_type = []
        if node_type is not None:
            node_ips_with_node_type = [
                env_node.int_ip for env_node in env_nodes if env_node.node_type == node_type]
            if node_group is None:
                return node_ips_with_node_type

        return list(set(node_ips_with_node_type).intersection(node_ips_with_node_group))
