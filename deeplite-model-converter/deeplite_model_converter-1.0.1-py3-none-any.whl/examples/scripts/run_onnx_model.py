import os 
# Hide GPU from visible devices to run on CPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import onnxruntime
import numpy as np

from deeplite_torch_zoo.wrappers.wrapper import get_data_splits_by_name, get_model_by_name

# Step 1: Define native pytorch dataloaders
batch_size = 1
data_splits = get_data_splits_by_name(dataset_name='cifar100',
                                        data_root='',
                                        batch_size=batch_size,
                                        num_workers=4)
test_loader = data_splits['test']

# Step 2: Load the ONNX model
model_path = "model.onnx"
sess_options = onnxruntime.SessionOptions()
session = onnxruntime.InferenceSession(model_path, sess_options)

# Step 3: Measure the accuracy
num_correct = 0
total = 0
for x, y in test_loader: # y of the size (batch_size * 1)
    x = x.detach().cpu().numpy()
    ort_inputs = {session.get_inputs()[0].name: x}
    ort_output = session.run(None, ort_inputs)
    ort_output = ort_output[0] # ort_shape is of the size (batch_size * num_classes)
    for idx in range(ort_output.shape[0]):
        total += 1
        if np.argmax(ort_output[idx]) == y[idx]:
            num_correct += 1

print("Accuracy: ", total, num_correct, (num_correct/total))