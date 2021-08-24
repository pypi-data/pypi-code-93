"""Useful instruments for work with graphs."""
import os
from typing import List
import tensorflow as tf
import tensorflow.compat.v1 as tf_v1
from tensorflow.python.framework import dtypes
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2
from tensorflow.python.tools import optimize_for_inference_lib
from tensorflow.python.platform import gfile


def pb_to_tensorboard_event(model_filename: str, save_dir: str) -> tf.compat.v1.Event:
    """Save TF event from pb-file."""
    with tf_v1.Session() as sess:
        with gfile.FastGFile(model_filename, 'rb') as read_file:
            graph_def = tf_v1.GraphDef()
            graph_def.ParseFromString(read_file.read())
            tf.import_graph_def(graph_def)
        train_writer = tf_v1.summary.FileWriter(save_dir)
        train_writer.add_graph(sess.graph)


def freeze_session(
        session: tf_v1.Session,
        keep_var_names=None,
        output_names=None):
    """
    Freezes the state of a session into a pruned computation graph.

    Creates a new computation graph where variable nodes are replaced by
    constants taking their current value in the session. The new graph will be
    pruned so subgraphs that are not necessary to compute the requested
    outputs are removed.

    Parameters
    ----------
    session
        The TensorFlow session to be frozen.
    keep_var_names
        A list of variable names that should not be frozen, or None to freeze all the variables in the graph.
    output_names
        Names of the relevant graph outputs.

    Returns
    -------
        The frozen graph definition.
    """
    graph = session.graph
    with graph.as_default():
        freeze_var_names = list(
            set(v.op.name for v in tf_v1.global_variables()).difference(
                keep_var_names or []))
        output_names = output_names or []
        output_names += [v.op.name for v in tf_v1.global_variables()]
        input_graph_def = graph.as_graph_def()
        for node in input_graph_def.node:
            node.device = ""
        frozen_graph = tf_v1.graph_util.convert_variables_to_constants(
            session, input_graph_def, output_names, freeze_var_names)
        return frozen_graph


def load_graph(graph_path: str) -> tf.Graph:
    """Load tensorflow graph from a .pb file.

    Parameters
    ----------
    graph_path : str
        Path to .pb file to load

    Returns
    -------
    tf.Graph
        Loaded graph

    Raises
    ------
    FileNotFoundError
        If graph_path doesn't exist
    """
    if not os.path.exists(graph_path):
        raise FileNotFoundError("File {} not found".format(graph_path))

    graph = tf.Graph()
    with graph.as_default():
        graph_def = tf_v1.GraphDef()
        with tf.io.gfile.GFile(graph_path, 'rb') as fid:
            graph_def.ParseFromString(fid.read())
            tf.import_graph_def(graph_def, name='')
    return graph


def freeze_graph_from_ckpt(
        ckpt_dir: str,
        output_node_names: str,
        to_dump: bool = False,
        tensorboard_event: bool = False) -> tf.Graph:
    """
    Extract the checkpoint files defined by the output nodes and convert all its variables into constant.

    Parameters
    ----------
    ckpt_dir
        the root folder containing the checkpoint state file
    output_node_names
        a string, containing all the output node's names, comma separated
    to_dump
        boolean flag indicates save graph to the filesystem or not
    tensorboard_event
        Set it true in case of lack of information about node's names to get tensorboard event
    Returns
    -------
        Frozen TensorFlow graph
    """
    if not tf_v1.gfile.Exists(ckpt_dir):
        raise AssertionError(
            "Export directory doesn't exists. Please specify an export "
            "directory: %s" % ckpt_dir)

    if not output_node_names:
        print("You need to supply the name of a node to --output_node_names.")
        return -1

    # We retrieve our checkpoint full path
    checkpoint = tf_v1.train.get_checkpoint_state(ckpt_dir)
    input_checkpoint = checkpoint.model_checkpoint_path

    # We clear devices to allow TensorFlow to control on which device it will load operations
    clear_devices = True

    # We start a session using a temporary fresh Graph
    with tf_v1.Session(graph=tf_v1.Graph()) as sess:
        # We import the meta graph in the current default Graph
        saver = tf_v1.train.import_meta_graph(input_checkpoint + '.meta', clear_devices=clear_devices)
        if tensorboard_event:
            tf_v1.summary.FileWriter(ckpt_dir, sess.graph)  # view the nodes of a meta graph

        # We restore the weights
        saver.restore(sess, input_checkpoint)

        # We use a built-in TF helper to export variables to constants
        frozen_graph = tf_v1.graph_util.convert_variables_to_constants(
            sess,  # The session is used to retrieve the weights
            tf_v1.get_default_graph().as_graph_def(),  # The graph_def is used to retrieve the nodes
            output_node_names.split(",")  # The output node names are used to select the useful nodes
        )
        if to_dump:
            # We precise the file fullname of our frozen graph
            absolute_model_dir = "/".join(input_checkpoint.split('/')[:-1])
            output_graph = absolute_model_dir + "/frozen_graph.pb"
            # Finally we serialize and dump the output graph to the filesystem
            with tf_v1.gfile.GFile(output_graph, "wb") as graph_file:
                graph_file.write(frozen_graph.SerializeToString())
            print("%d ops in the final graph." % len(frozen_graph.node))

    return frozen_graph


def freeze_graph_from_saved_model(model_dir: str, save_dir: str = ".", graph_name: str = 'frozen_graph.pb',
                                  as_text: bool = False, concrete_func: tf.function = None):
    """
    Freeze the graph from TensorFlow saved_model and variables.

    Parameters
    ----------
    model_dir
        Path to the model directory containing saved_model and variables
    save_dir
        Path to the save dir for the frozen graph
    graph_name
        Result name of the frozen_graph
    as_text
        Bool variable if to save as text or not
    concrete_func
        Concrete function might be explicitly given to freeze constants
    Returns
    -------

    """
    model = tf.saved_model.load(model_dir, tags=[['serve']])
    if not concrete_func:
        try:
            concrete_func = model.signatures['serving_default']
        except KeyError:
            raise KeyError('Need to provide an explicit ConcreteFunction to freeze coefficients.')
    frozen_func = convert_variables_to_constants_v2(concrete_func)

    tf.io.write_graph(graph_or_graph_def=frozen_func.graph,
                      logdir=save_dir,
                      name=graph_name,
                      as_text=as_text)


def wrap_frozen_graph(graph_def: tf_v1.GraphDef, inputs: List[str], outputs: List[str]):
    """
    Return a function used to run the graph.

    Parameters
    ----------
    graph_def
        GraphDef object loaded from a frozen graph.
    inputs
        list of input nodes
    outputs
        list of output nodes
    Returns
    -------

    """
    def imports_graph_def():
        tf_v1.import_graph_def(graph_def, name="")

    wrapped_import = tf_v1.wrap_function(imports_graph_def, [])
    import_graph = wrapped_import.graph

    return wrapped_import.prune(
        tf.nest.map_structure(import_graph.as_graph_element, inputs),
        tf.nest.map_structure(import_graph.as_graph_element, outputs))


def optimize_frozen_graph_def(frozen_graph_def, input_node_names: List[str], output_node_names: List[str]):
    """Remove trainable parameters from graph_def."""
    output_graph_def = optimize_for_inference_lib.optimize_for_inference(
        frozen_graph_def,
        input_node_names=input_node_names,
        output_node_names=output_node_names,
        placeholder_type_enum=dtypes.float32.as_datatype_enum)
    # Remove Const nodes.
    for i in reversed(range(len(output_graph_def.node))):
        if output_graph_def.node[i].op == 'Const':
            del output_graph_def.node[i]
        for attr in ['T', 'Tshape', 'N', 'Tidx', 'Tdim',
                     'use_cudnn_on_gpu', 'Index', 'Tperm', 'is_training',
                     'Tpaddings']:
            if attr in output_graph_def.node[i].attr:
                del output_graph_def.node[i].attr[attr]
    return output_graph_def


def freeze_keras_model(model, save_dir: str, concrete_func: tf.function = None) -> None:
    """Freeze keras model and export it to protobuf file."""
    full_model = tf.function(lambda x: model(x))
    inputs: list = []
    if not concrete_func:
        for model_input in model.inputs:
            inputs.append(tf.TensorSpec(model_input.shape, model_input.dtype, name=model_input.name))
        concrete_function = full_model.get_concrete_function(tuple(inputs))
        frozen_func = convert_variables_to_constants_v2(concrete_function)
    else:
        frozen_func = convert_variables_to_constants_v2(concrete_func)
    graph_def = frozen_func.graph.as_graph_def()
    tf.io.write_graph(graph_or_graph_def=graph_def,
                      logdir=save_dir,
                      name=f"{model.name}.pb",
                      as_text=False)
