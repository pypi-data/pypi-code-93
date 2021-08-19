__author__ = ['yuquanfeng', 'zhiyaozhang']

import matplotlib.pyplot as plt
import os

import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.utils.multiclass import unique_labels


def plot_confusion_matrix(y_true,
                          y_pred,
                          save_name='',
                          postfix='jpg',
                          save_path='./',
                          normalize=None,
                          display_labels=None,
                          include_values=True,
                          title=None,
                          cmap=plt.cm.Blues,
                          xticks_rotation='horizontal',
                          figsize=(9, 7),
                          dpi=300,
                          values_format=None,
                          colorbar=True
                          ):
    """
    :param y_true:
    :param y_pred:
    :param normalize: {'true'， 'pred'， 'all'}， default=None
    :param save_name: 保存的文件名，默认值=’‘，为空字符串时，不保存文件
    :param postfix: 文件后缀名，('jpg', 'png')二选一，不符合要求时，默认jpg
    :param save_path: 文件保存的路径
    :param display_labels: 用于显示的label，默认值=None，不传入时，会自动计算出0~n的数字显示
    :param include_values: bool，默认值=True, 在混淆矩阵中包含值
    :param title: 标题, 默认值=None
    :param cmap: matplotlib识别的Colormap, 默认值=Blues
    :param xticks_rotation: {'vertical'，'horizontal'}或float, 默认值='horizontal', xtick标签的旋转。
    :param figsize: 默认值=(9, 7)
    :param dpi: 300
    :param values_format: str，默认值=None, 混淆矩阵中值的格式规范。如果“None”，格式规范为“d”或“.2g”，以较短者为准。
    :param colorbar: bool，默认值=True, 是否向绘图中添加颜色栏。
    :return: 混淆矩阵的值
    """
    cm = confusion_matrix(y_true, y_pred, normalize=normalize)
    _, ax = plt.subplots(figsize=figsize, dpi=dpi)

    if normalize:
        if not title:
            title = "Normalized confusion matrix"
    else:
        if not title:
            title = 'Confusion matrix, without normalization'

    if display_labels is None:
        display_labels = unique_labels(y_true, y_pred)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                  display_labels=display_labels)
    disp.plot(include_values=include_values,
              cmap=cmap, ax=ax, xticks_rotation=xticks_rotation,
              values_format=values_format, colorbar=colorbar)

    plt.title(title)
    if postfix not in ('jpg', 'png'):
        postfix = 'jpg'

    if save_name and isinstance(save_name, str):
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        plt.savefig(os.path.join(save_path, f'{save_name}.{postfix}'))
    plt.show()
    return cm


def visualize_train(train_loss, train_acc, valid_loss, valid_acc, save_name,
                    postfix='jpg', figsize=(10, 8), dpi=300, show_checkpoint=True):
    # visualize the loss and acc as the network trained
    fig = plt.figure(figsize=figsize, dpi=dpi)
    plt.plot(range(1, len(train_loss) + 1), train_loss, label='Training Loss')
    plt.plot(range(1, len(valid_loss) + 1), valid_loss, label='Validation Loss')
    plt.plot(range(1, len(train_acc) + 1), train_acc, label='Training Acc')
    plt.plot(range(1, len(valid_acc) + 1), valid_acc, label='Validation Acc')

    # find position of lowest validation loss
    if show_checkpoint:
        minposs = valid_loss.index(min(valid_loss)) + 1
        plt.axvline(minposs, linestyle='--', color='r', label='Early Stopping Checkpoint')

    plt.xlabel('epochs')
    plt.ylabel('loss & acc')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{save_name}.{postfix}', bbox_inches='tight')
    plt.show()


# if __name__ == '__main__':
#     df = pd.read_csv('../test/resnet50_2021-8-19-4_41_log.csv')
#     train_acc, train_loss, = df['train_acc'].values.tolist(), df['train_loss'].values.tolist()
#     val_acc, val_loss = df['val_acc'].values.tolist(), df['val_loss'].values.tolist()
#
#     visualize_train(train_loss, train_acc, val_loss, val_acc, save_name='../output/test_vis_train')
#     y_pred = [0, 0, 2, 2, 0, 2]
#     y_true = [2, 0, 2, 2, 0, 1]
#     # array([[2, 0, 0],
#     #        [0, 0, 1],
#     #        [1, 0, 2]])
#     cm = plot_confusion_matrix(y_true, y_pred,
#                                normalize='all',
#                                # display_labels=['a', 'b', 'c'],
#                                # values_format='.3g',
#                                # colorbar=False
#                                save_name='test',
#                                save_path='../output'
#                                )
#     print(cm)
