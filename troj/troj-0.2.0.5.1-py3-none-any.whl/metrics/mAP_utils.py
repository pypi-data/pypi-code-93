import pandas as pd
import numpy as np
import torch
from numpy import trapz

"""
TODO: run tests for each of these functions to increase coverage
"""

def MakePredAnnotBoxDataframes(df, adversarial=False):
    """
    Takes a troj OD dataframe and creates two new dataframes from it. The first dataframe contains the ground truth objects
    where each row is an instance of an object in an image. The second dataframe is the predicted objects, where each row is
    a single object in an image as well.
    :param df: Troj OD dataframe
    :param adversarial: If we are using the adversarial values or not.
    :return: dataframe containing ground truth objects and one containing predictions.
    """
    # makes two dataframes, where each row is a specific instance of a bounding box. Does this for both gt and preds
    gt_dicts_list = []
    pred_dicts_list = []
    ind_str = "{}_{}"
    if adversarial:
        prefix = "adversarial"
    else:
        prefix = "pred"
    for index, row in df.iterrows():
        im_name = row["file_name"]
        gt_labels = row["labels"]
        pred_labels = row[ind_str.format(prefix, "labels")]
        for idx in range(len(gt_labels)):
            label = row["labels"][idx]
            box = row["boxes"][idx]
            gt_dict = {"file_name": im_name, "label_id": label, "box": box}
            gt_dicts_list.append(gt_dict)
        for idx in range(len(pred_labels)):
            label = row[ind_str.format(prefix, "labels")][idx]
            box = row[ind_str.format(prefix, "boxes")][idx]
            score = row[ind_str.format(prefix, "scores")][idx]
            pred_dict = {
                "file_name": im_name,
                "pred_label_id": label,
                "pred_box": box,
                "pred_score": score,
            }
            pred_dicts_list.append(pred_dict)
    gt_box_df = pd.DataFrame(gt_dicts_list)
    pred_box_df = pd.DataFrame(pred_dicts_list)
    return gt_box_df, pred_box_df


def box_ious(gt_df, pred_df):
    """

    :param gt_df: ground truth dataframe from function MakePredAnnotBoxDataframes
    :param pred_df: Prediction dataframe from function MakePredAnnotBoxDataframes
    :return: returns both dataframes, where the pred_df has been modified to contain a column where each row in that column
    contains a number which is either -1 if the predicted object does not have a corresponding ground truth, or contains the
    index of the ground truth object in the ground truth dataframe. It also adds the maximum IOU value.
    """
    # get class ids
    class_ids = gt_df["label_id"].unique()
    # iterate over class ids
    for cls_id in class_ids:
        sub_pred_df = pred_df[pred_df["pred_label_id"] == cls_id]
        imgs = sub_pred_df["file_name"].unique()
        # iterate over images
        for img in imgs:
            # get image, get instances of classes in image.
            im_gt = gt_df[gt_df["file_name"] == img]
            im_gt = im_gt[im_gt["label_id"] == cls_id]
            im_gt_cls_boxes = np.asarray(im_gt["box"].tolist())
            pred_cls_boxes = np.asarray(
                sub_pred_df[sub_pred_df["file_name"] == img]["pred_box"].tolist()
            )
            # check for ground truth objects
            if im_gt_cls_boxes.shape[0] == 0:
                ious = torch.zeros(pred_cls_boxes.shape[0], 1)
                no_gt = True
            # if there are ground truth objects, compute the IOU between the objects and the predictions
            else:
                ious = torchvision.ops.box_iou(
                    torch.from_numpy(pred_cls_boxes), torch.from_numpy(im_gt_cls_boxes)
                )
                no_gt = False
            # get maximum ious for each object
            iou_max, indices = torch.max(ious, dim=1)
            indices = indices.numpy()
            iou_max = iou_max.numpy()
            inds = sub_pred_df[sub_pred_df["file_name"] == img].index
            pred_df.loc[inds, "max_iou"] = iou_max
            if no_gt == False:
                # save corresponding indices of most salient ground truth object
                ground_truth_inds = im_gt.iloc[indices].index
                pred_df.loc[inds, "gt_instance_idx"] = ground_truth_inds
                # go through gt indices in preds, for each gt_index keep only the maximum iou instance, set other index to -1
                for idx in ground_truth_inds:
                    comp_df = pred_df[pred_df["gt_instance_idx"] == idx]
                    comp_df = comp_df.sort_values("max_iou", ascending=False)
                    sorted_inds = comp_df.index
                    if len(sorted_inds) > 1:
                        pred_df.loc[sorted_inds[1:], "gt_instance_idx"] = (
                            -1 * torch.ones(len(sorted_inds[1:]), 1).numpy()
                        )
            else:
                # if no GT objects exist, set the indices to -1
                fp_markers = -1 * torch.ones(pred_cls_boxes.shape[0], 1).numpy()
                pred_df.loc[inds, "gt_instance_idx"] = fp_markers
            # pred_df = pred_df.loc[inds]['max_iou'] = iou_max
    return gt_df, pred_df


def compute_pr(tp, fp, gt_num):
    """
    Computes the precision and recall from the number of true positives, number of false positives, and the number of
    ground truth objects.
    :param tp: Number of true positves.
    :param fp: Number of false positives.
    :param gt_num: Number of ground truth objects.
    :return: precision, recall
    """
    # takes in # of true positives, # false positives, and total number of GT objects and returns the precision and recall
    recall = tp / gt_num
    precision = tp / (tp + fp)
    return precision, recall


def compute_interp_curve(precisions, recalls):
    """

    :param precisions: precisions array
    :param recalls: recalls array
    :return: interpolated PR curve.
    """
    curve_y = []
    for idx in range(recalls.shape[0]):
        p_interp = np.max(precisions[idx:])
        curve_y.append(p_interp)
    return curve_y


def ClassAP(gt_df, preds_df, iou_thresh=0.5):
    """
    Computes the average precision for each class according the PASCAL VOC criteria.
    :param gt_df: Ground truth dataframe.
    :param preds_df: predictions dataframe containing both the ground truth object column and the IOU column
    :param iou_thresh: the IOU threshold to compute the AP from.
    :return: A dictionary containing the class AP for each class at iou_thresh.
    """
    class_ap_dict = {}
    class_ids = gt_df["label_id"].unique()
    preds_copy = copy.deepcopy(preds_df)
    gt_copy = copy.deepcopy(gt_df)
    preds_copy.loc[(preds_copy["max_iou"] < iou_thresh), "gt_instance_idx"] = -1
    for cls_id in class_ids:
        tp_counter = 0
        fp_counter = 0
        precision = []
        recall = []
        sub_pred_df = preds_copy[preds_copy["pred_label_id"] == cls_id]
        sub_gt_df = gt_copy[gt_copy["label_id"] == cls_id]
        sub_pred_df = sub_pred_df.sort_values("pred_score", ascending=False)
        true_pos = sub_pred_df[sub_pred_df["gt_instance_idx"] != -1]
        num_gt = len(sub_gt_df)
        sub_preds_indices = sub_pred_df.index
        for idx in sub_preds_indices:
            if sub_pred_df.loc[idx]["gt_instance_idx"] == -1:
                fp_counter += 1
            else:
                tp_counter += 1
            prec, rec = compute_pr(tp_counter, fp_counter, num_gt)
            sub_pred_df.loc[idx, "accum_tp"] = tp_counter
            sub_pred_df.loc[idx, "accum_fp"] = fp_counter
            sub_pred_df.loc[idx, "precision"] = prec
            sub_pred_df.loc[idx, "recall"] = rec
        sorted_precisions = sub_pred_df["precision"].to_numpy()
        sorted_recalls = sub_pred_df["recall"].to_numpy()
        interp_curve = compute_interp_curve(sorted_precisions, sorted_recalls)
        ap = trapz(interp_curve, x=sorted_recalls)
        class_ap_dict[cls_id] = ap

    return class_ap_dict
