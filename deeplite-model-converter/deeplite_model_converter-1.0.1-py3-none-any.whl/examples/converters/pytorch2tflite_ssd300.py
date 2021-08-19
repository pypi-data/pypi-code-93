from deeplite_torch_zoo.wrappers.wrapper import get_data_splits_by_name, get_model_by_name
from deeplite.torch_profiler.torch_profiler import TorchProfiler
from deeplite.torch_profiler.torch_data_loader import TorchForwardPass
from deeplite.profiler import Device

# Step 1: Define native pytorch dataloaders and model
data_splits = get_data_splits_by_name(dataset_name='voc',
                                            model_name='ssd300_resnet18',
                                            data_root='/neutrino/datasets/',
                                            batch_size=16,
                                            num_workers=4)

# 1b. Load the native Pytorch model
native_teacher = get_model_by_name(model_name='ssd300_resnet18',
                                        dataset_name='voc_20',
                                        pretrained=True,
                                        progress=True)


# Step 2: Create Profiler class and register the profiling functions
fp = TorchForwardPass(model_input_pattern=(0, '_', '_', '_'))
data_loader = TorchProfiler.enable_forward_pass_data_splits(data_splits, fp)

from deeplite.pytorch_converter.pytorch2onnx import PyTorch2ONNX
from deeplite.onnx_converter.onnx2tf import ONNX2TF
from deeplite.tf_converter.tf2tflite import TF2TFLite

# Step 3: Convert Pytorch model to ONNX
pytorch2onnx = PyTorch2ONNX(model=native_teacher)
pytorch2onnx.set_config(precision='fp32', device=Device.GPU)
pytorch2onnx.convert(data_loader['train'], dynamic_input='bchw', path="model.onnx")

# Step 4: Convert ONNX model to TF signatures
onnx2tf = ONNX2TF(model="model.onnx")
tf_model, _ = onnx2tf.convert()

# Step 5: Convert TF signatures to TFLite model
tf2tflite = TF2TFLite(model=tf_model)
tflite_model, _ = tf2tflite.convert()
tf2tflite.save(tflite_model, "model.tflite")

