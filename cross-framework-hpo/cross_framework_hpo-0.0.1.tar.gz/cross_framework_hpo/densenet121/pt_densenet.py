from cross_framework_hpo.base_pytorch_model import base_pytorch_function
import torchvision.models as models


def densenet_pt_objective(config):
    model = models.densenet121(pretrained=False, num_classes=10)
    return base_pytorch_function(config, supplied_model=model)


if __name__ == "__main__":
    test_config = {'batch_size': 64, 'learning_rate': .001, 'epochs': 1, 'adam_epsilon': 1e-7}
    res = densenet_pt_objective(test_config)
    print("Accuracy is {}".format(res[0]))
