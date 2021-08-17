# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Concrete classes for model wrappers."""

from torch import nn

from azureml.automl.dnn.vision.classification.common.constants import ModelNames, \
    ModelLiterals, ModelParameters
from azureml.automl.dnn.vision.classification.models.base_model_wrapper import BaseModelWrapper
from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.base_model_factory import BaseModelFactory
from azureml.automl.dnn.vision.common.constants import PretrainedModelNames, TrainingLiterals
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.pretrained_model_utilities import PretrainedModelFactory

logger = get_logger(__name__)


class Resnet18Wrapper(BaseModelWrapper):
    """Model wrapper for Resnet18."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, pretrained: bool = True) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type validcrop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param pretrained: flag to indicate if the pretrained weights should be loaded
        :type pretrained: bool
        """
        model = PretrainedModelFactory.resnet18(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNET18,
                         featurizer=featurizer)


class Resnet34Wrapper(BaseModelWrapper):
    """Model wrapper for Resnet34."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, pretrained: bool = True) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type validcrop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param pretrained: flag to indicate if the pretrained weights should be loaded
        :type pretrained: bool
        """
        model = PretrainedModelFactory.resnet34(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNET34,
                         featurizer=featurizer)


class Resnet50Wrapper(BaseModelWrapper):
    """Model wrapper for Resnet50."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, pretrained: bool = True) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type validcrop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param pretrained: flag to indicate if the pretrained weights should be loaded
        :type pretrained: bool
        """
        model = PretrainedModelFactory.resnet50(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNET50,
                         featurizer=featurizer)


class Resnet101Wrapper(BaseModelWrapper):
    """Model wrapper for Resnet101."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, pretrained: bool = True) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type validcrop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param pretrained: flag to indicate if the pretrained weights should be loaded
        :type pretrained: bool
        """
        model = PretrainedModelFactory.resnet101(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNET101,
                         featurizer=featurizer)


class Resnet152Wrapper(BaseModelWrapper):
    """Model wrapper for Resnet152."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, pretrained: bool = True) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type validcrop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param pretrained: flag to indicate if the pretrained weights should be loaded
        :type pretrained: bool
        """
        model = PretrainedModelFactory.resnet152(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNET152,
                         featurizer=featurizer)


class Mobilenetv2Wrapper(BaseModelWrapper):
    """Model wrapper for mobilenetv2."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, pretrained: bool = True) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type validcrop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param pretrained: flag to indicate if the pretrained weights should be loaded
        :type pretrained: bool
        """
        model = PretrainedModelFactory.mobilenet_v2(pretrained=pretrained)
        num_feats = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.MOBILENETV2,
                         featurizer=featurizer)


class SeresnextWrapper(BaseModelWrapper):
    """Model wrapper for seresnext."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, pretrained: bool = True) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type valid_crop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param pretrained: flag to indicate if the pretrained weights should be loaded
        :type pretrained: bool
        """
        model = PretrainedModelFactory.se_resnext50_32x4d(num_classes=1000, pretrained=pretrained,
                                                          pretrained_on='imagenet')
        num_feats = model.last_linear.in_features
        model.last_linear = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])

        # seresnext50 can't take arbitrary image size
        default_valid_resize_size = ModelParameters.DEFAULT_VALID_RESIZE_SIZE
        default_valid_crop_size = ModelParameters.DEFAULT_VALID_CROP_SIZE
        default_train_crop_size = ModelParameters.DEFAULT_TRAIN_CROP_SIZE
        if valid_resize_size != default_valid_resize_size or valid_crop_size != default_valid_crop_size or \
                train_crop_size != default_train_crop_size:
            logger.warning("[{} only takes a fixed input size ({}: {}, {}: {} and {}: {}) "
                           "thus using defaults instead of the provided values]"
                           .format(ModelNames.SERESNEXT,
                                   ModelLiterals.VALID_RESIZE_SIZE, default_valid_resize_size,
                                   ModelLiterals.VALID_CROP_SIZE, default_valid_crop_size,
                                   ModelLiterals.TRAIN_CROP_SIZE, default_train_crop_size))
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=default_valid_resize_size, valid_crop_size=default_valid_crop_size,
                         train_crop_size=default_train_crop_size, multilabel=multilabel,
                         model_name=ModelNames.SERESNEXT, featurizer=featurizer)


class ResNest50Wrapper(BaseModelWrapper):
    """ Model wrapper for ResNest-50."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, pretrained: bool = True) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type validcrop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param pretrained: flag to indicate if the pretrained weights should be loaded
        :type pretrained: bool
        """
        model = PretrainedModelFactory.resnest50(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNEST50,
                         featurizer=featurizer)


class ResNest101Wrapper(BaseModelWrapper):
    """ Model wrapper for ResNest-101."""

    def __init__(self, num_classes: int, valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                 multilabel: bool = False, pretrained: bool = True) -> None:
        """
        :param num_classes: number of classes
        :type num_classes: int
        :param valid_resize_size: length of side of the square that we have to resize to
        :type valid_resize_size: int
        :param valid_crop_size: length of side of the square that we have to crop for passing to model
        :type validcrop_size: int
        :param train_crop_size: length of side of the square that we have to crop for passing to model
            for train dataset
        :type train_crop_size: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param pretrained: flag to indicate if the pretrained weights should be loaded
        :type pretrained: bool
        """
        model = PretrainedModelFactory.resnest101(pretrained=pretrained)
        num_feats = model.fc.in_features
        model.fc = nn.Linear(num_feats, num_classes)
        # store featurizer
        featurizer = nn.Sequential(*list(model.children())[:-1])
        super().__init__(model=model, number_of_classes=num_classes,
                         valid_resize_size=valid_resize_size, valid_crop_size=valid_crop_size,
                         train_crop_size=train_crop_size, multilabel=multilabel, model_name=ModelNames.RESNEST101,
                         featurizer=featurizer)


class ModelFactory(BaseModelFactory):
    """Model factory class for obtaining model wrappers."""

    def __init__(self):
        """Init method."""
        super().__init__()

        self._models_dict = {
            ModelNames.RESNET18: Resnet18Wrapper,
            ModelNames.RESNET34: Resnet34Wrapper,
            ModelNames.RESNET50: Resnet50Wrapper,
            ModelNames.RESNET101: Resnet101Wrapper,
            ModelNames.RESNET152: Resnet152Wrapper,
            ModelNames.MOBILENETV2: Mobilenetv2Wrapper,
            ModelNames.SERESNEXT: SeresnextWrapper,
            ModelNames.RESNEST50: ResNest50Wrapper,
            ModelNames.RESNEST101: ResNest101Wrapper
        }

        self._pre_trained_model_names_dict = {
            ModelNames.RESNET18: PretrainedModelNames.RESNET18,
            ModelNames.RESNET34: PretrainedModelNames.RESNET34,
            ModelNames.RESNET50: PretrainedModelNames.RESNET50,
            ModelNames.RESNET101: PretrainedModelNames.RESNET101,
            ModelNames.RESNET152: PretrainedModelNames.RESNET152,
            ModelNames.MOBILENETV2: PretrainedModelNames.MOBILENET_V2,
            ModelNames.SERESNEXT: PretrainedModelNames.SE_RESNEXT50_32X4D,
            ModelNames.RESNEST50: PretrainedModelNames.RESNEST50,
            ModelNames.RESNEST101: PretrainedModelNames.RESNEST101
        }

        self._default_model = ModelNames.SERESNEXT

    def get_model_wrapper(self, model_name, num_classes, multilabel,
                          device, distributed, rank, settings={}, model_state=None):
        """
        :param model_name: string name of the model
        :type model_name: str
        :param num_classes: number of classes
        :type num_classes: int
        :param multilabel: flag indicating whether this is multilabel or not
        :type multilabel: bool
        :param device: device to place the model on
        :type device: torch.device
        :param distributed: if we are in distributed mode
        :type distributed: bool
        :param rank: rank of the process in distributed mode
        :type rank: int
        :param settings: Settings to initialize model settings from
        :type settings: dict
        :param model_state: model weights
        :type model_state: dict
        :return: model wrapper
        :rtype: azureml.automl.dnn.vision.classification.base_model_wrappers.BaseModelWrapper
        """
        if model_name is None:
            model_name = self._default_model

        if model_name not in self._models_dict:
            raise AutoMLVisionValidationException('The provided model_name is not supported.',
                                                  has_pii=False)
        if num_classes is None:
            raise AutoMLVisionValidationException('num_classes cannot be None', has_pii=False)

        # Extract relevant parameters from settings
        valid_resize_size = settings.get(ModelLiterals.VALID_RESIZE_SIZE, ModelParameters.DEFAULT_VALID_RESIZE_SIZE)
        valid_crop_size = settings.get(ModelLiterals.VALID_CROP_SIZE, ModelParameters.DEFAULT_VALID_CROP_SIZE)
        train_crop_size = settings.get(ModelLiterals.TRAIN_CROP_SIZE, ModelParameters.DEFAULT_TRAIN_CROP_SIZE)
        model_wrapper = self._models_dict[model_name](num_classes=num_classes,
                                                      multilabel=multilabel,
                                                      pretrained=model_state is None,
                                                      valid_resize_size=valid_resize_size,
                                                      valid_crop_size=valid_crop_size,
                                                      train_crop_size=train_crop_size)

        # Freeze layers
        # make sure to have this logic before setting up ddp
        layers_to_freeze = settings.get(TrainingLiterals.LAYERS_TO_FREEZE, None)
        if layers_to_freeze is not None:
            utils.freeze_model_layers(model_wrapper, layers_to_freeze=layers_to_freeze)

        if model_state is not None:
            model_wrapper.load_state_dict(model_state)

        model_wrapper.to_device(device)

        if distributed:
            model_wrapper.model = nn.parallel.DistributedDataParallel(model_wrapper.model,
                                                                      device_ids=[rank],
                                                                      output_device=rank)
        model_wrapper.distributed = distributed

        return model_wrapper
