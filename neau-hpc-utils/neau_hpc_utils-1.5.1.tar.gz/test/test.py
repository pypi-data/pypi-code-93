from neau_hpc_utils.graph import plot_confusion_matrix
import timm
import torch
from torch import nn


class MyViT(nn.Module):
    """
    修改分类模型的分类数
    """
    def __init__(self, target_size, device, device_ids, pretrained=True):
        super(MyViT, self).__init__()
        self.model = timm.create_model('vit_base_patch16_224',
                                       pretrained=pretrained)
        n_features = self.model.head.in_features
        # 改成自己任务的图像类别数
        self.model.head = nn.Linear(n_features, target_size)
        self.model = torch.nn.DataParallel(self.model, device_ids=device_ids)
        self.model = self.model.to(device)

    def forward(self, x):
        x = self.model(x)
        return x


if __name__ == '__main__':
    y_pred = [0, 0, 2, 2, 0, 2]
    y_true = [2, 0, 2, 2, 0, 1]
    # array([[2, 0, 0],
    #        [0, 0, 1],
    #        [1, 0, 2]])
    cm = plot_confusion_matrix(y_true, y_pred,
                               normalize='all',
                               # display_labels=['a', 'b', 'c'],
                               # values_format='.3g',
                               # colorbar=False
                               # save_name='test3',
                               # save_path='../output'
                               )
    print(cm)
