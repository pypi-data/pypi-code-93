__author__ = 'yuquanfeng'

import timm
import torch


def load_model_from_timm(model_name, device, device_ids, pretrained, num_classes):
    model = timm.create_model(model_name, pretrained=pretrained, num_classes=num_classes)
    model = model.to(device)
    model = torch.nn.DataParallel(model, device_ids=device_ids)
    return model

