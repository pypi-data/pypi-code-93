# MIT License
# Copyright (c) 2021  Zhi Liu(cowliucn@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pandas as pd
import numpy as np

class ConfusionMatrixParser:

    def __init__(self, cm):
        self.cm = cm
        self.cm_parsed = None
        pass

    def parse_confusion_matrix(self):
        '''
        Parse confusion matrix, get following metrics:
        1) each class' TP, TN, FN, FP, TPR, TNR, FPR, FN
        2) each class' actual true count(atc), actual false count(afc), predicted true count(ptc), predicted false count(pfc)
        3) each class' accurcy, precision, recall, f1
        Args:
            None

        Returns:
            df(Dataframe): metric dataframe, each row is one class's 12 metrics.
            Sample outopt:
        tp  fp  tn  fn       tpr       fpr       tnr       fnr  atc  afc  ptc  pfc  accuracy  precision    recall        f1
class0   1  28  11   5  0.166667  0.717949  0.282051  0.833333    6   39   12   33  0.644444   0.083333  0.166667  0.111111
class1   5  20  10  10  0.333333  0.666667  0.333333  0.666667   15   30   15   30  0.555556   0.333333  0.333333  0.333333
class2   9  12   9  15  0.375000  0.571429  0.428571  0.625000   24   21   18   27  0.466667   0.500000  0.375000  0.428571
        '''

        cm = self.cm
        assert (cm.shape[0] == cm.shape[1])

        class_names = cm.index.values
        num_metrics = 16

        # metrics
        column_names = ["tp", "fp", "tn", "fn", "tpr", "fpr", "tnr", "fnr", "atc", "afc", "ptc", "pfc",
                        "accuracy", "precision", "recall", "f1"]
        assert (len(column_names) == num_metrics)

        class_num = cm.shape[0]

        # df stores all classes' metrics
        df = pd.DataFrame(np.zeros(shape=(class_num, num_metrics)),
                          index=class_names, columns=column_names)

        for i in range(class_num):
            tp = self.get_tp(i)
            fn = self.get_fn(i)
            fp = self.get_fp(i)
            tn = self.get_tn(tp, fn, fp)

            tpr = tp / (tp + fn)
            fpr = fp / (fp + tn)
            fnr = fn / (fn + tp)
            tnr = tn / (tn + fp)

            # atc, afc, ptc, pfc
            actual_true_count = tp + fn
            actual_false_count = tn + fp
            pred_true_count = tp + fp
            pred_false_count = tn + fn

            accuracy = (tp + tn) / (tp + tn + fp + fn)
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            f1 = (2 * precision * recall) / (precision + recall)

            d = dict()
            d["tp"] = tp
            d["tn"] = tn
            d["fp"] = fp
            d["fn"] = fn
            d["tpr"] = tpr
            d["tnr"] = tnr
            d["fpr"] = fpr
            d["fnr"] = fnr
            d["atc"] = actual_true_count
            d["afc"] = actual_false_count
            d["ptc"] = pred_true_count
            d["pfc"] = pred_false_count
            d["accuracy"] = accuracy
            d["precision"] = precision
            d["recall"] = recall
            d["f1"] = f1

            results = pd.Series(data=d, index=d.keys())
            df.iloc[i] = results

        int_column = ["tp", "fp", "tn", "fn", "atc", "afc", "ptc", "pfc"]
        df[int_column] = df[int_column].applymap(np.int64)

        self.cm_parsed = df.copy()

        return df

    def get_tp(self, i):
        '''
        Get a class' true positive
        Args:
            i(int): class index

        Returns:
            the class' true positive

        '''

        return self.cm.iloc[i, i]

    def get_fn(self, i):
        '''
        Get a class' false negative
        Args:
            i(int): class index

        Returns:
            the class's false  negative

        '''

        row = self.cm.iloc[i, :]
        fn = np.sum(row) - self.cm.iloc[i, i]

        return fn

    def get_fp(self,i):
        '''
        Get a class' false positive
        Args:
            i(int): class index

        Returns:
            the class's false positive
        '''
        col = self.cm.iloc[:, i]
        fp = np.sum(col) - self.cm.iloc[i, i]

        return fp

    def get_tn(self, tp, fn, fp):
        '''
         Get a class' true negative
         Args:
             i(int): class index

         Returns:
             the class's true positive

         '''

        all = 0
        for i in range(self.cm.shape[0]):
            for j in range(self.cm.shape[1]):
                all += self.cm.iloc[i, j]

        tn = all - tp - fn - fp

        return tn

    def print_summary(self, **kwargs):
        '''
        Print metrics summary.
        If "class_name" or "class_index" is specified, print the specified class summary,
        else print summary for every class.
        Args:
            **kwargs: class_name = "class name"
                      class_index = class index(integer)

        Returns:
            None
        '''

        df = self.cm_parsed
        if "class_name" in kwargs:
            class_name = kwargs["class_name"]
            df = df.loc[[class_name],:]
        if "class_index" in kwargs:
            class_index = kwargs["class_index"]
            df = df.iloc[[class_index], :]
            df= pd.DataFrame(df)

        for i in df.index:

            row = df.loc[i,:]
            print("Summary for %s\n"
                  "TP: %d\n"
                  "TN: %d\n"
                  "FP: %d\n"
                   "FN: %d\n"
                  "TPR: %.3f\n"
                  "TNR: %.3f\n"
                  "FPR: %.3f\n"
                  "FNR: %.3f\n"
                  "Actual true count: %d\n"
                  "Actual false count: %d\n"
                  "Predict true count: %d\n"
                  "Predict false count: %d\n"
                  "Accuracy: %.3f\n"
                  "Precision: %.3f\n"
                  "Recall: %.3f\n"
                  "F1: %.3f" %
                  (i, row["tp"],row["tn"],row["fp"],row["fn"],
                   row["tpr"],row["tnr"],row["fpr"],row["fnr"],
                   row["atc"],row["afc"],row["ptc"],row["pfc"],
                   row["accuracy"],row["precision"],row["recall"],row["f1"]))
