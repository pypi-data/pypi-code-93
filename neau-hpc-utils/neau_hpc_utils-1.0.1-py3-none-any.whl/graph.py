import itertools
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.metrics import confusion_matrix, plot_confusion_matrix


def plot_confusion_matrix(y_true,
                          y_pred,
                          normalize=None,
                          decimals=2,
                          # cm,
                          # classes,
                          # title='Confusion matrix',
                          # cmap=plt.cm.Blues,
                          # name='Gaussnb',
                          ):
    """
    这个函数打印并绘制混淆矩阵。
    可以通过设置' normalize=True '来应用规范化。
    """
    con_mat = confusion_matrix(y_true, y_pred, normalize=normalize)

    if normalize:
        con_mat = np.around(con_mat, decimals=decimals)
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    # plt.figure(figsize=(9, 7), dpi=100)
    # plt.imshow(cm, interpolation='nearest', cmap=cmap)

    #     fig, ax = plt.subplots()
    #     im = ax.imshow(cm)
    #     ax.set_ylim(len(cm)-0.5, -0.5)

    # plt.title(title)
    # plt.colorbar()
    # tick_marks = np.arange(len(classes))
    # plt.xticks(tick_marks, classes)  # rotation=45
    # plt.yticks(tick_marks, classes)
    # plt.ylim(len(cm) - 0.5, -0.5)
    #
    # fmt = '.2f' if normalize else 'd'
    # thresh = cm.max() / 2.
    # for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
    #     plt.text(j, i, format(cm[i, j], fmt),
    #              horizontalalignment="center",
    #              color="white" if cm[i, j] > thresh else "black")
    #
    # plt.ylabel('True label')
    # plt.xlabel('Predicted label')
    # plt.tight_layout()
    # if not os.path.exists(f'./resulImgs/{name}cm.jpg'):
    #     plt.savefig(f'./resulImgs/Cm{name}.jpg')
    return con_mat


if __name__ == '__main__':
    y_pred = [0, 0, 2, 2, 0, 2]
    y_true = [2, 0, 2, 2, 0, 1]
    # array([[2, 0, 0],
    #        [0, 0, 1],
    #        [1, 0, 2]])
    cm = plot_confusion_matrix(y_true, y_pred, normalize='true')
    print(cm)

    # def CalculationResults(val_y, y_val_pred, simple=False, \
    #                        target_names=["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop",
    #                                      "reggae", "rock"], name='SGD'):
    #     # 计算检验
    #     F1_score = f1_score(val_y, y_val_pred, average='macro')
    #     if simple:
    #         return F1_score
    #     else:
    #         acc = accuracy_score(val_y, y_val_pred)
    #         recall_score_ = recall_score(val_y, y_val_pred, average='macro')
    #         class_report = classification_report(val_y, y_val_pred)
    #         ss1 = 'f1:%.2f%%' % (F1_score * 100) + '\n' + 'Accuarcy:%.2f%%' % (acc * 100) + '\n'
    #         f.write(ss1)
    #         print('f1:%.2f%%' % (F1_score * 100))
    #         print('Accuarcy:%.2f%%' % (acc * 100))
    #         print('f1_score:', F1_score, '\nACC_score:', acc, '\nrecall:', recall_score_)
    #         #         print('\n----class report ---:\n',class_report)
    #         #         print('----confusion matrix ---:\n',confusion_matrix_)
    #
    #         # 画混淆矩阵
    #         # 画混淆矩阵图
    #         plt.figure()
    #         plot_confusion_matrix(confusion_matrix_, classes=target_names,
    #                               title=f'Confusion matrix of {name}', name=name)
    #         #         plt.show()
    #         return F1_score, acc, recall_score_, confusion_matrix_, class_report
