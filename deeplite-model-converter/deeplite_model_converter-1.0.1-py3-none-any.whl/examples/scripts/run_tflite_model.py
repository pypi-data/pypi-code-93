import os 
# Hide GPU from visible devices to run on CPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import tensorflow as tf
import numpy as np

from deeplite_torch_zoo.wrappers.wrapper import get_data_splits_by_name, get_model_by_name
from deeplite.torch_profiler.torch_profiler import TorchProfiler

# Step 1: Define native pytorch dataloaders
batch_size = 1
data_splits = get_data_splits_by_name(dataset_name='cifar100',
                                        data_root='',
                                        batch_size=batch_size,
                                        num_workers=4)
test_loader = data_splits['test']
data_loader = TorchProfiler.enable_forward_pass_data_splits(data_splits)
inputs_tuple = data_loader['train'].forward_pass.create_random_model_inputs(batch_size)

# Step 2: Initialize the TFLite Interpreter
model_path = "model.tflite"
interpreter = tf.lite.Interpreter(model_path=model_path)

interpreter.resize_tensor_input(0, inputs_tuple[0].shape)
interpreter.allocate_tensors()

# Step 3: Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Step 4: Measure the accuracy
num_correct = 0
total = 0
for x, y in test_loader: # y of the size (batch_size * 1)
    total += 1
    x = x.detach().cpu().numpy()

    interpreter.set_tensor(input_details[0]['index'], x)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    if np.argmax(output_data) == y.detach().cpu().numpy():
        num_correct += 1

print("Accuracy: ", total, num_correct, (num_correct/total))