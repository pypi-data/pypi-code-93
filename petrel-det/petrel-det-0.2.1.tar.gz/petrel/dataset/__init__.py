import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2

from .petrel import PetrelDataset
from .train_data import TrainDataset
from .val_data import ValDataset

BBOX = A.BboxParams(
    format='pascal_voc',
    min_area=0,
    min_visibility=0,
    label_fields=['labels'])


def get_default_transform(img_size):
    """Returns a function to perform the default transform if the training
       transform fails.
    """
    return A.Compose([A.Resize(height=img_size[0],
                               width=img_size[1], p=1.0),
                      ToTensorV2(p=1.0)],
                     bbox_params=BBOX,
                     p=1.0)
