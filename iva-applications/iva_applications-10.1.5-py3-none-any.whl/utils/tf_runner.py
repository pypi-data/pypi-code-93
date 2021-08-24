"""Tensorflow Runner ulils."""
from typing import List, Dict, Any
import warnings

import numpy as np
import tensorflow as tf

from .runner import Runner
from .graph_utils import load_graph, wrap_frozen_graph


class TFRunner(Runner):
    """Runner for Tensorflow graph."""

    def __init__(self, graph_path: str, input_nodes: List[str], output_nodes: List[str]):
        """
        Initialize Tensorflow Runner with protobuf graph.

        Parameters
        ----------
        graph_path: path to protobuf file
        input_nodes: input nodes' names
        output_nodes: output nodes' names
        """
        super().__init__(graph_path, input_nodes, output_nodes)
        with tf.io.gfile.GFile(graph_path, "rb") as file:
            graph_def = tf.compat.v1.GraphDef()
            _ = graph_def.ParseFromString(file.read())

        self.frozen_graph_wrapper = wrap_frozen_graph(graph_def=graph_def,
                                                      inputs=input_nodes,
                                                      outputs=output_nodes)

    def __call__(self, tensor: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Run inference using TensorFlow.

        Parameters
        ----------
        tensor: Dict of input node names and np.ndarrays

        Returns
        -------
        outputs_dict: Dict of output node names and np.ndarrays
        """
        inputs_dict = {}
        outputs_dict = {}
        for key, value in tensor.items():
            node_dict = {
                key: tf.constant(value, dtype=value.dtype)
            }
            inputs_dict.update(node_dict)
        keys = list(tensor.keys())
        tensor_list = [inputs_dict[key] for key in keys]
        outputs = self.frozen_graph_wrapper(*tensor_list)
        for index, _ in enumerate(outputs):
            node_dict = {self.output_nodes[index]: outputs[index].numpy()}
            outputs_dict.update(node_dict)
        return outputs_dict


class TFRunnerOld(Runner):
    """Runner for Tensorflow graph."""

    def __init__(self, graph_path: str, input_nodes: List[str], output_nodes: List[str]):
        """
        Initialize Tensorflow Runner with protobuf graph.

        Parameters
        ----------
        graph_path: path to protobuf file
        input_nodes: input nodes' names
        output_nodes: output nodes' names
        """
        super().__init__(graph_path, input_nodes, output_nodes)
        loaded_graph = load_graph(graph_path)
        self.sess = tf.compat.v1.Session(graph=loaded_graph)
        warnings.warn("TFRunnerOld is deprecated, use TFRunner instead", DeprecationWarning)

    def __call__(self, tensor: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Run inference using TensorFlow.

        Parameters
        ----------
        tensor: input matrices

        Returns
        -------
        outputs_dict: output matrices
        """
        outputs_dict = {}
        inputs_dict = {}
        graph_output_tensors = []
        for index, node_name in enumerate(self.output_nodes):
            graph_output_tensors.append(self.sess.graph.get_tensor_by_name(node_name))
        for key, value in tensor.items():
            node_dict = {
                self.sess.graph.get_tensor_by_name(key): value
            }
            inputs_dict.update(node_dict)
        outputs = self.sess.run(
            graph_output_tensors,
            feed_dict=inputs_dict)
        for index, _ in enumerate(outputs):
            node_dict = {self.output_nodes[index]: outputs[index]}
            outputs_dict.update(node_dict)
        return outputs_dict


def get_original_node_names_from_cfg(conf_tpu_json_dict: Dict[str, Any]) -> Dict[str, str]:
    """
    Make a dict with input and output quant nodes names as keys and corresponding original nodes names as values.

    This function uses a dict from to_compile/conf.tpu.json which is obtained after quantization.

    Parameters
    ----------
    conf_tpu_json_dict
        dict from conf.tpu.json file

    Returns
    -------
    The dict which matches nodes of quantized graph and original nodes
    """
    match_dict = {}
    in_out_nodes = []
    comp_dict = conf_tpu_json_dict['model']
    all_nodes = list(comp_dict.keys())
    in_out_raw_nodes = [node for node in all_nodes if 'input_node' in node or 'output_node' in node]
    for node in in_out_raw_nodes:
        if 'input_node' in node:
            node = node + '/Placeholder:0'
        if 'output_node' in node:
            node = node + '/output:0'
        in_out_nodes.append(node)
    for node in in_out_nodes:
        match_dict[node] = comp_dict[node.split('/')[0]]['tpu_anchor']
    return match_dict
