from cross_framework_hpo.base_pytorch_model import base_pytorch_function
# import torchvision.models as models
from cross_framework_hpo.vgg16.updated_torchvision_vgg import vgg16
import torch

def vgg_pt_objective(config):
    model = vgg16(pretrained=False, num_classes=10)
    return base_pytorch_function(config, supplied_model=model)


if __name__ == "__main__":
    test_config = {'batch_size': 532, 'learning_rate': 0.074552791, 'epochs': 26, 'adam_epsilon': 0.536216016}
    pt_test_acc, pt_model, pt_average_training_history, pt_latest_training_history = vgg_pt_objective(test_config)
    torch.save(pt_model.state_dict(), '../cifar10/vgg_lambda/dual_train_d24f6410' + '.pt_model.pt')
    print("Accuracy is {}".format(pt_test_acc))


