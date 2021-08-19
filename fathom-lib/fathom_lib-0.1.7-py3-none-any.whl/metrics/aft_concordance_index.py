import numpy as np


class AftConcordanceIndex:
    def calc_metrics(self, context):
        result = {
            "train_concordance_index": self.concordance_index(
                context["y_train"], context["y_train_pred"]
            ),
            "test_concordance_index": self.concordance_index(
                context["y_test"], context["y_test_pred"]
            ),
        }
        return result

    @staticmethod
    def concordance_index(y, y_pred):
        y_np = np.array(y)
        y_pred_np = np.array(y_pred)
        correct_pairs = 0
        admissable_pairs = 0
        for i in range(len(y_pred_np)):
            pair = y_np[i]
            subset = y_np[:i]
            larger_pairs_indices = np.where(
                (pair[1] <= subset[:, 0]) & (pair[0] != subset[:, 1])
            )[0]
            smaller_pairs_indices = np.where(
                (pair[0] >= subset[:, 1]) & (pair[1] != subset[:, 0])
            )[0]
            admissable_pairs += len(larger_pairs_indices) + len(smaller_pairs_indices)

            y_pred_right = y_pred_np[larger_pairs_indices]
            correct_pairs += len(np.where(y_pred_np[i] < y_pred_right)[0]) + 0.5 * len(
                np.where(y_pred_np[i] == y_pred_right)[0]
            )
            y_pred_left = y_pred_np[smaller_pairs_indices]
            correct_pairs += len(np.where(y_pred_np[i] > y_pred_left)[0]) + 0.5 * len(
                np.where(y_pred_np[i] == y_pred_left)[0]
            )
        if admissable_pairs == 0:
            return -1
        else:
            return correct_pairs / admissable_pairs
