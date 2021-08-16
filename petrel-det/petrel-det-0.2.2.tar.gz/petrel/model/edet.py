import torch
from effdet import get_efficientdet_config, create_model_from_config
from .bench import DetBenchTrainVal


def load_edet(config_name,
              image_size,
              checkpoint_path=None,
              num_classes=1,
              max_det_per_image=1000,
              soft_nms=False,
              device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
              train=True,
              detection=False):
    """
    Loads the EfficientDet model with the given config name, input size, and output classes.
    Can load models with COCO pretrained weights or user-defined model weights.


    :param config_name: Name of the mdoel to load.
    :param image_size: Size the input images.
    :param checkpoint_path: Option path for loading model weights.
    :param num_classes: Number of prediction classes.
    :param max_det_per_image: Maximum number of detection regions to predict.
    :param soft_nms: Use soft non-max suppression. Defaults to False as soft nms is very slow.
    :param device: Device to load the model on. CPU or CUDA. Defaults using CUDA if available, otherwise CPU
    :param train: Is the model being trained. Defaults to True
    :param detection: Return detections during training. This slows down the validation step. Defaults to False.
    :return: EfficientDet model.
    """
    config = get_efficientdet_config(config_name)
    if type(image_size) == int:
        config.image_size = [image_size, image_size]
    else:
        config.image_size = image_size
    config.max_det_per_image = max_det_per_image
    config.soft_nms = soft_nms
    pretrained = False if checkpoint_path else True
    model = create_model_from_config(config, pretrained=pretrained,
                                     bench_task="train" if train else "predict",
                                     max_det_per_image=max_det_per_image,
                                     num_classes=num_classes,
                                     soft_nms=soft_nms,
                                     checkpoint_path=checkpoint_path if checkpoint_path else "",
                                     bench_labeler=True)

    if train:
        if not detection:
            model = DetBenchTrainVal(model.model, model.config)
        model.train()
    else:
        model.eval()
    if device:
        model = model.to(device)

    return model
