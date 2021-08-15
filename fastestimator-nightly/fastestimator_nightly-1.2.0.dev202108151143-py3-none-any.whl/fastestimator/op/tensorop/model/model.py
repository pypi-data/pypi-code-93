# Copyright 2019 The FastEstimator Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import inspect
from functools import partial
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, TypeVar, Union

import tensorflow as tf
import torch

from fastestimator.backend.feed_forward import feed_forward
from fastestimator.op.tensorop.tensorop import TensorOp
from fastestimator.util.traceability_util import FeInputSpec, traceable
from fastestimator.util.util import to_list, get_num_devices

Tensor = TypeVar('Tensor', tf.Tensor, torch.Tensor)
Model = TypeVar('Model', tf.keras.Model, torch.nn.Module)


@traceable()
class ModelOp(TensorOp):
    """This class performs forward passes of a neural network over batch data to generate predictions.

    Args:
        model: A model compiled by fe.build.
        inputs: String key of input training data.
        outputs: String key under which to store predictions.
        mode: What mode(s) to execute this Op in. For example, "train", "eval", "test", or "infer". To execute
            regardless of mode, pass None. To execute in all modes except for a particular one, you can pass an argument
            like "!infer" or "!train".
        trainable: Indicates whether the model should have its weights tracked for update.
        intermediate_layers: One or more layers inside of the model from which you would also like to extract output.
            This can be useful, for example, for visualizing feature extractor embeddings in conjunction with the
            TensorBoard trace. Layers can be selected by name (str) or index (int). If you are using pytorch, you can
            look up this information for your model by calling `list(model.named_modules())`. For TensorFlow you can use
            `model.submodules`. Tensorflow users should note that if you do not manually assign a name to a model layer,
            a name will be autogenerated for you (ex. conv2d_2). This autogenerated name will change if you build a new
            model within the same python session (for example, if you re-run a Jupyter notebook cell, the name could now
            be conv2d_5). Any `intermediate_layers` you request will be appended in order to the end of the Op output,
            so you must provide output key names for them within the `outputs` argument. Note that layer names may be
            different between single-gpu and multi-gpu environments, though we attempt to prevent this.
    """
    def __init__(self,
                 model: Union[tf.keras.Model, torch.nn.Module],
                 inputs: Union[None, str, Iterable[str]] = None,
                 outputs: Union[None, str, Iterable[str]] = None,
                 mode: Union[None, str, Iterable[str]] = None,
                 trainable: bool = True,
                 intermediate_layers: Union[None, str, int, List[Union[str, int]]] = None):
        super().__init__(inputs=inputs, outputs=outputs, mode=mode)
        assert hasattr(model, "fe_compiled"), "must use fe.build to compile the model before use"
        self.intermediate_outputs = []  # [{device: Tensor}]
        intermediate_layers = to_list(intermediate_layers)
        if intermediate_layers and get_num_devices() > 1:
            print("\033[93m {}\033[00m".format(
                "FastEstimator-Warn: Layer names / ids may be different between single-gpu and multi-gpu environments"))
        for intermediate_layer in intermediate_layers:
            storage = {}
            if isinstance(model, tf.keras.Model):
                layers = model.submodules
                if isinstance(intermediate_layer, int):
                    intermediate_layer = layers[intermediate_layer]
                else:
                    layers = {layer.name: layer for layer in layers}
                    intermediate_layer = layers[intermediate_layer]
                if not hasattr(intermediate_layer, 'fe_original_call'):
                    intermediate_layer.fe_original_call = intermediate_layer.call
                    intermediate_layer.call = partial(_capture_call_tf, fe_storage=storage, fe_layer=intermediate_layer)
            elif isinstance(model, torch.nn.Module):
                layers = model.named_modules()
                if get_num_devices() > 1:
                    # Try to automatically adjust parameters for multi-gpu so that user doesn't need to change code
                    layers2 = list(model.named_modules())  # It's a generator, so don't corrupt the other copy
                    if isinstance(layers2[0][1], torch.nn.parallel.DataParallel):
                        parallel_prefix = "module."
                        if isinstance(intermediate_layer, str) and not intermediate_layer.startswith(parallel_prefix):
                            intermediate_layer = parallel_prefix + intermediate_layer
                        elif isinstance(intermediate_layer, int):
                            layers = layers2[1:]
                if isinstance(intermediate_layer, int):
                    intermediate_layer = list(layers)[intermediate_layer][1]
                else:
                    intermediate_layer = dict(layers)[intermediate_layer]
                intermediate_layer.register_forward_hook(partial(_capture_call_torch, fe_storage=storage))
            self.intermediate_outputs.append(storage)
        self.model = model
        self.trainable = trainable
        self.epoch_spec = None
        self.multi_inputs = False
        self.device = ''

    def build(self, framework: str, device: Optional[torch.device] = None) -> None:
        self.device = device or ''  # TF will just use empty string for device
        if framework == "torch" and len(self.inputs) > 1:
            if hasattr(self.model, "module"):
                # multi-gpu models have module attribute
                self.multi_inputs = len(inspect.signature(self.model.module.forward).parameters.keys()) > 1
            else:
                self.multi_inputs = len(inspect.signature(self.model.forward).parameters.keys()) > 1

    def get_fe_models(self) -> Set[Model]:
        return {self.model}

    def forward(self, data: Union[Tensor, List[Tensor]], state: Dict[str, Any]) -> Union[Tensor, List[Tensor]]:
        training = state['mode'] == "train" and self.trainable
        if isinstance(self.model, torch.nn.Module) and self.epoch_spec != state['epoch']:
            # Gather model input specs for the sake of TensorBoard and Traceability
            self.model.fe_input_spec = FeInputSpec(data, self.model)
            self.epoch_spec = state['epoch']
        if self.multi_inputs:
            data = feed_forward(self.model, *data, training=training)
        else:
            data = feed_forward(self.model, data, training=training)
        intermediate_outputs = []
        for output in self.intermediate_outputs:
            intermediate_outputs.append(_unpack_output(output, self.device))
            output.clear()  # This will only help with pytorch memory, tf tensors will remain until next forward
        if intermediate_outputs:
            data = to_list(data) + intermediate_outputs
        return data


def _capture_call_tf(input: tf.Tensor, fe_storage: Dict[Union[str, torch.device], Tensor],
                     fe_layer: tf.keras.layers.Layer, **kwargs) -> tf.Tensor:
    """A function to capture the output of a TF model layer.

    Args:
        input: The input tensor to the layer. Note that this must be the first argument in the method signature.
        fe_storage: A place to store the output from the layer.
        fe_layer: A tf layer such that fe_layer(input) -> output.
        **kwargs: Any arguments to be passed along to the fe_layer call method.

    Returns:
        The output of the given layer for the specified input.
    """
    output = fe_layer.fe_original_call(input, **kwargs)
    fe_storage[''] = output  # TF multi-gpu doesn't need to store separately per device
    return output


def _capture_call_torch(module: torch.nn.Module, input: Tuple[torch.Tensor, ...], output: torch.Tensor,
                        fe_storage: Dict[Union[str, torch.device], Tensor]) -> None:
    """A callback function to capture the output of a torch model layer.

    Args:
        module: The pytorch model to which the layer belongs.
        input: The input to the given layer
        output: The output from the given layer.
        fe_storage: A place to store the output from the layer.
    """
    fe_storage[input[0].device] = output


def _unpack_output(output_dict: Dict[Union[str, torch.device], Tensor], device: Union[str, torch.device]) -> Tensor:
    """A function to convert a collection of layer outputs into a single output.

    This is necessary for pytorch multi-gpu support.

    Args:
        output_dict: A dictionary containing one or more tensors to be combined.
        device: The device onto which to compile the tensor(s).

    Returns:
        A stacked representation of the tensor(s) in the output_dict.
    """
    if isinstance(device, torch.device):
        response = torch.vstack(
            [t[1].to(device) for t in sorted(output_dict.items(), key=lambda x: x[0].index or 0)])
    else:  # tf
        response = output_dict[device]
    return response
