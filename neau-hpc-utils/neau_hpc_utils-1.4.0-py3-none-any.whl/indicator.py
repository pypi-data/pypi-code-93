__author__ = ['yuquanfeng', 'sihanzhou']

import os
import json
import numpy as np
from .graph import confusion_matrix


def get_indicator(y_true, y_pred, save_name='', save_path='./', values_format=3):
    cm = confusion_matrix(y_true, y_pred, normalize=None)

    # 在多分类下，TP、TN、FP、FN的计算
    FP = cm.sum(axis=0) - np.diag(cm)
    FN = cm.sum(axis=1) - np.diag(cm)
    TP = np.diag(cm)
    TN = cm.sum() - (FP + FN + TP)

    # 在多分类下，其他的指标的计算
    # TPR = TP / (TP + FN)  # Sensitivity, hit rate, recall, or true positive rate
    # TNR = TN / (TN + FP)  # Specificity or true negative rate
    # PPV = TP / (TP + FP)  # Precision or positive predictive value
    # NPV = TN / (TN + FN)  # Negative predictive value
    # FPR = FP / (FP + TN)  # Fall out or false positive rate
    # FNR = FN / (TP + FN)  # False negative rate
    # FDR = FP / (TP + FP)  # False discovery rate
    # ===============预处理分母，避免极端条件下，分母为0===============
    TP_and_FN = _ignore_zero((TP + FN))
    TN_and_FP = _ignore_zero((TN + FP))
    TP_and_FP = _ignore_zero((TP + FP))
    # 指标计算
    TPR = TP / TP_and_FN  # Sensitivity, hit rate, recall, or true positive rate
    TNR = TN / TN_and_FP  # Specificity or true negative rate
    PPV = TP / TP_and_FP  # Precision or positive predictive value

    # 得到平均的指标值
    Precision = np.mean(PPV)
    Specificity = np.mean(TNR)
    ReCall = np.mean(TPR)
    # F1_score = np.mean((2 * PPV * TPR) / (PPV + TPR))
    # Accuracy = np.mean((TP + TN) / (TP + FP + FN + TN))
    # ===============预处理分母，避免极端条件下，分母为0===============
    PPV_and_TPR = _ignore_zero((PPV + TPR))
    All = _ignore_zero((TP + FP + FN + TN))
    # 平均指标计算
    F1_score = np.mean((2 * PPV * TPR) / PPV_and_TPR)
    Accuracy = np.mean((TP + TN) / All)

    if not isinstance(values_format, int):
        values_format = 3

    data = {
        "TP": str(np.sum(TP)),
        "TN": str(np.sum(TN)),
        "FP": str(np.sum(FP)),
        "FN": str(np.sum(FN)),
        "Precision": str(round(Precision.item(), values_format)),
        "ReCall": str(round(ReCall.item(), values_format)),
        "F1 score": str(round(F1_score.item(), values_format)),
        "Specificity": str(round(Specificity.item(), values_format)),
        "Accuracy": str(round(Accuracy.item(), values_format)),
    }

    if save_name and isinstance(save_name, str):
        file_path = os.path.join(save_path, f'{save_name}.json')
        with open(file_path, 'w') as file_obj:
            json.dump(data, file_obj)

    return data


def _ignore_zero(array):
    return np.array(list(map(lambda x: x if x > 0 else 1, array)))


# if __name__ == '__main__':
#     y_true = [2, 0, 2, 2, 0, 1]
#     y_pred = [0, 0, 2, 2, 0, 2]
#     # array([[2, 0, 0],
#     #        [0, 0, 1],
#     #        [1, 0, 2]])
#     get_indicator(y_true, y_pred, save_name='test', save_path='../output', values_format=3)
