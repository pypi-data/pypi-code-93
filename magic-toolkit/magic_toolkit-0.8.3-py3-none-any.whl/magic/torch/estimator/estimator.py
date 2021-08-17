from magic import log
import torch
from torch import nn
from torchsummary import summary
import os

class Estimator:
    def __init__(self, model: nn.Module, pre_trained, inputs_size):
        """
        :param model:
        :param pre_trained:
        :param inputs_size: list of size, [[C, H, W], [C, H, W], ...]
        """
        # pre-defined member data
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        # member data passed in
        self.model = model.to(self.device)
        self.pre_trained = pre_trained
        self.inputs_size = inputs_size
        self.resume_last_training = True
        self.checkpoint = {"model": {}, "epoch": 0, "optimizer": {}, "logdir": "", "epoch_loss_mean": 0}

    def __call__(self, *inputs):
        return self.model.forward(*inputs)

    def set_train_mode(self):
        if not self.model.training:
            self.model.train()

    def set_eval_mode(self):
        if self.model.training:
            self.model.eval()

    def summary(self):
        """
        support multiple inputs to the network
        :param inputs_size, list of size, don't contain batch size: [[C, H, W], [C, H, W], ...]
        """
        inputs_size = [tuple(size) for size in self.inputs_size]  # need tuple type

        torch_model = self.model.module if hasattr(self.model, "module") else self.model

        log.info("model summary .. ")
        summary(torch_model, inputs_size, batch_size=1, device=self.device.type)

    def load(self, strict=False, resume=True):
        """
        Partially loading a model or loading a partial model are log scenarios
        when transfer learning or training a new complex model. Leveraging trained parameters,
        even if only a few are usable, will help to warmstart the training process and
        hopefully help your model converge much faster than training from scratch.
        you can set the strict argument to False in the load_state_dict() function to ignore non-matching keys
        """
        if not os.path.exists(self.pre_trained):
            log.warning("pre_trained model does not exists")
            self.resume_last_training = False
            return

        log.info("loading pre_trained:", self.pre_trained)

        self.checkpoint = torch.load(self.pre_trained, map_location=self.device)
        self.resume_last_training = resume

        if hasattr(self.model, "module"):
            self.model.module.load_state_dict(self.checkpoint['model'], strict=strict)
        else:
            self.model.load_state_dict(self.checkpoint['model'], strict=strict)

    def save(self, model_path=None):
        """ save checkpoint """
        if model_path is None:
            model_path = self.pre_trained

        """
        torch.nn.DataParallel is a model wrapper that enables parallel GPU utilization.
        To save a DataParallel model generically, save the model.module.state_dict(). 
        This way, you have the flexibility to load the model any way you want to any device you want.
        """

        if hasattr(self.model, "module"):
            if len(self.model.module.state_dict()) == 0:
                raise RuntimeError("model is empty")
            self.checkpoint["model"] = self.model.module.state_dict()
        else:
            if len(self.model.state_dict()) == 0:
                raise RuntimeError("model is empty")
            self.checkpoint["model"] = self.model.state_dict()

        torch.save(self.checkpoint, model_path)
        log.info("saved to {}".format(model_path))

    def export_onnx(self, onnx_path, batch=1, opset_version=None, verbose=False, output_names=None):
        """
        Exporting a model in PyTorch works via tracing or scripting.
        To export a model, we call the torch.onnx.export() function.
        This will execute the model, recording a trace of what operators are used to compute the outputs.
        Because export runs the model, we need to provide an input tensor x.
        The values in this can be random as long as it is the right type and size.
        :param onnx_path
        :param opset_version: onnx version
        :param batch: for onnx batch
        :param output_names: list, can be ignored
        """

        import onnx
        from onnxsim import simplify

        # Export the model
        self.set_eval_mode()

        dummy_inputs = tuple([torch.randn(batch, *size).to(self.device) for size in self.inputs_size])

        torch_model = self.model.module if hasattr(self.model, "module") else self.model

        torch.onnx.export(torch_model,  # model being run
                          dummy_inputs,  # model input (or a tuple for multiple inputs)
                          onnx_path,  # where to save the model (can be a file or file-like object)
                          export_params=True,  # store the trained parameter weights inside the model file
                          opset_version=opset_version,  # the ONNX version to export the model to
                          do_constant_folding=True,  # whether to execute constant folding for optimization
                          input_names=[],  # the model's input names
                          output_names=output_names,  # the model's output names
                          verbose=verbose
                          )

        # load your predefined ONNX model
        onnx_model = onnx.load(onnx_path)
        onnx_model, check = simplify(onnx_model)
        assert check, "Simplified ONNX model could not be validated"
        onnx.save(onnx_model, onnx_path)
        log.info("onnx saved to: {}".format(onnx_path))
