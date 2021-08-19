import os
import torch, torch.nn as nn
import onnx
from copy import deepcopy
from deeplite.profiler import Device

from deeplite.converter.converter import ModelConverter 
from deeplite.converter.formatter import getLogger
from deeplite.converter.formatter import ModelFormat
logger = getLogger()

class PyTorch2ONNX(ModelConverter):
    def __init__(self, model):
        super().__init__(model)
        self.source_format = ModelFormat.PYTORCH
        self.target_format = ModelFormat.ONNX

    def convert(self, dataloader, batch_size=1, path='output.onnx', dynamic_input='b'):
        
        if dynamic_input and self.CAN_DYN_INPUT is False:
            logger.warning("Cannot convert to dynamic input as torch version < 1.2, disabling it")
            self.dynamic_input = None    

        inputs_tuple = dataloader.forward_pass.create_random_model_inputs(batch_size)

        if not dataloader.forward_pass.expecting_common_inputs:
            logger.info("Forcing CPU device and disabling fp16 as inputs are non standard")
            self.precision = 'fp32'
            self.device = Device.CPU
        else:  
            inputs_tuple = dataloader.forward_pass._tensor_sampler.to_device(
                inputs_tuple, self.device, standardize=False)
            
        model = deepcopy(self.model)
        model.eval()
        model = self.model_to_device(model, self.device)
        if self.precision.lower() == "fp16":
            logger.info("Change to fp16 mode.")
            model = model.half()
            path = path.replace('.onnx', '_fp16.onnx')
            # yeah this is a hack
            inputs_tuple = dataloader.forward_pass._tensor_sampler._loop_over_tensors_tuple(
                inputs_tuple, lambda x: x.half())

        dynamic_input_kwargs = {}
        if dynamic_input:
            # this is ready to be extended for output shape, but is it needed?
            inputs_shape = dataloader.forward_pass.get_model_input_shapes()
            # output = model(*inputs_tuple)

            input_names = []
            # output_names = []
            dynamic_input_kwargs['dynamic_axes'] = {}

            def add_single_info(position, shape, info_string, info_list):
                info_list.append(info_string + '_%d' % position)
                dynamic_input_kwargs['dynamic_axes'][input_names[-1]] = {}
                dyn_map = dynamic_input_kwargs['dynamic_axes'][input_names[-1]]

                if 'b' in dynamic_input:
                    dyn_map[0] = 'b'
                if 'c' in dynamic_input:
                    dyn_map[1] = 'c'
                if 'h' in dynamic_input and len(shape) > 1:
                    dyn_map[2] = 'h'
                if 'w' in dynamic_input and len(shape) > 1:
                    dyn_map[3] = 'w'

            def loop_over_info(shapes, name, list_names):
                i = 0
                # remember that this has the same structure as inputs_tuple as it was standardized
                for shp in shapes:
                    # VERY IMPORTANT: do not replace with an isinstance check! this really needs to be type
                    if type(shp) in (tuple, list,):
                        for sub_shp in shp:
                            add_single_info(i, sub_shp, name, list_names)
                            i += 1
                    elif isinstance(shp, dict):
                        raise NotImplementedError("Dynamic ONNX graph shapes unsupported with 'dict'")
                    else:
                        add_single_info(i, shp, name, list_names)
                        i += 1

            loop_over_info(inputs_shape, 'input', input_names)
            # loop_over_info(outputs_shape, 'output', output_names)

            dynamic_input_kwargs['input_names'] = input_names
            # dynamic_input_kwargs['output_names'] = output_names

        # export pytorch model to onnx
        try:
            torch.onnx.export(model, inputs_tuple, path, opset_version=self.ONNX_OPSET_VERSION,
                              export_params=True, **dynamic_input_kwargs)
            logger.info("Model has been exported to onnx format: {0}".format(os.path.abspath(path)))
            rval = 0
        except Exception as e:
            logger.error("Model could not be exported in onnx")
            logger.warning(
                "Model could not be exported in onnx, it contains an unsupported operation '{}'".format(e))
            rval = 1

        return rval

    def load_model(self, path=None):
        pass

    def save(self):
        pass

    def set_config(self, precision='fp32', device=Device.CPU, opset_version=None, can_dyn_input=False,):
        try:
            from torch.onnx import symbolic_helper
            self.ONNX_OPSET_VERSION = symbolic_helper._onnx_stable_opsets[-1]
        except:
            logger.debug("Unable to find the latest onnx stable opset release, defaulting to 9")
            self.ONNX_OPSET_VERSION = 9 if not opset_version else opset_version

        self.CAN_DYN_INPUT = float(torch.__version__[:3]) >= 1.2 if not can_dyn_input else can_dyn_input
        self.device = Device.GPU if precision.lower() == "fp16" else device
        self.precision = precision

    @staticmethod
    def model_to_device(m, device):
        m = m.cpu() if device == Device.CPU else m.cuda()
        return m