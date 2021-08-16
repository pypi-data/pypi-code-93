import numpy as np
import pandas as pd
from effdet.evaluation.detection_evaluator import PascalDetectionEvaluator


def model_eval(pred, categories, ious=np.round(np.arange(0.5, 1.0, 0.05), 2)):
    """
    Evaluates mAP scores at various IOU thresholds. Returns DataFrame of mAP scores for each threshold,
    label and the unweighted average of label mAPs.
    :param pred: Dataframe of predicted and ground truth labels and bounding boxes.
    :param categories: List of category names and labels. List elements must take the form {"id": id, "name": name}
    :param ious: IOU thresholds for computing mAPs. Defaults to .50:.05:.95.
    :return: Dataframe of mAP values.
    """
    evaluators = {iou: PascalDetectionEvaluator(categories=categories,
                                                matching_iou_threshold=iou) for iou in ious}
    for n, row in pred.iterrows():
        gt = {"cls": row["gt_labels"],
              "bbox": row["gt_boxes"]}
        det = {"cls": row["pred_labels"],
               "bbox": row["pred_boxes"],
               "score": row["pred_scores"]}
        for iou in evaluators:
            evaluators[iou].add_single_ground_truth_image_info(n, gt)
            evaluators[iou].add_single_detected_image_info(n, det)

    evaluators = {iou: evaluators[iou].evaluate() for iou in evaluators}
    for iou in evaluators:
        new_map = {}
        for k in evaluators[iou]:
            if "Precision" in k:
                new_map["Precision"] = evaluators[iou][k]
            else:
                new_k = k.split("/")[-1]
                new_map[new_k] = evaluators[iou][k]
        evaluators[iou] = new_map
    mAP = pd.DataFrame(evaluators).T
    return mAP
