"""
Utilities for attacks in the trojai package.

"""


import torchvision.ops
import torch


def nms_reduction(predictions, thresh=0.05):
    """
    Performs non-maximal suppression on output dictionary of network.

    :param predictions: A dictionary containing the keys [boxes, labels, scores] where boxes are the bounding boxes for
    predicted objects in the form [x,y, x+w, y+h] where w,h are the width and height of the bounding box. Labels are the
    predicted labels, and scores are the confidence of prediction.
    :param thresh: Threshold with which to perform the suppression.
    :return: Supressed predictions.
    """
    # returns predictions after NMS
    fixed_indices = torchvision.ops.nms(
        predictions["boxes"], predictions["scores"], thresh
    )
    reduced_predictions = {
        "boxes": predictions["boxes"][fixed_indices],
        "labels": predictions["labels"][fixed_indices],
        "scores": predictions["scores"][fixed_indices],
    }
    return reduced_predictions


def get_objects_of_type(predictions, object_class, inc_scores=True):
    """
    Gets predictions for objects only of a given type.

    :param predictions: Original predictions. Model typically outputs list, this expects only elements of that list.
    :param object_class: Object class id
    :param inc_scores: whether or not to include the scores in the output
    :return: The prediction dictionary containing only the desired class.
    """
    # extracts predictions for the class we wish to evaluate
    labels = predictions["labels"]
    obj_ids = (labels == object_class).nonzero()
    if inc_scores == True:
        reduced_predictions = {
            "boxes": predictions["boxes"][obj_ids],
            "labels": predictions["labels"][obj_ids],
            "scores": predictions["scores"][obj_ids],
        }
    else:
        reduced_predictions = {
            "boxes": predictions["boxes"][obj_ids],
            "labels": predictions["labels"][obj_ids],
        }
    return reduced_predictions


def detect_dict_from_idx(inp_dict, ids):
    """
    Return subdictionary of prediction dictionary based on sets of value ids.

    :param inp_dict: Input dictionary
    :param ids: list of ids
    :return: Dictionary containing the values at the locations specified by the ids.
    """
    key_list = list(inp_dict.keys())
    new_dict = {}
    for key in key_list:
        new_dict[key] = inp_dict[key][ids]
    return new_dict


def get_gt_indices(indicator_matrix):
    """
    Gets the ground truth objects corresponding to the predictions
    :param indicator_matrix: Two dimensional matrix of booleans
    :return: ground truth objects tensor
    """
    ground_truth_objs = []
    for idx in range(indicator_matrix.shape[0]):
        gt = indicator_matrix[idx].nonzero()
        if gt.shape[0] == 0:
            gt_obj = -1
        else:
            gt_obj = gt[0]
        ground_truth_objs.append(gt_obj)
    return torch.tensor(ground_truth_objs)


def get_tp_fp(gt_inds):
    """
    Used for the troj imagewise Average Precision score. gets the true positives and false positives as a list. If a
     ground truth object is predicted more than once, every prediction after the first is a false positive.
    :param gt_inds: Ground truth index tensor
    :return: A tensor where a zero entry represents a false positive and a 1 represents a true positive.
    """
    # gets the true positives and false positives as a list. If a ground truth object is predicted more than once, every prediction after the first is
    # a false positive.
    taken_idxs = []
    tp_fp_list = []
    for idx in gt_inds:
        if idx not in taken_idxs and idx != -1:
            taken_idxs.append(idx)
            tp_fp_list.append(1)
        else:
            tp_fp_list.append(0)
    return torch.tensor(tp_fp_list)


def get_fn_indicators(indicator_matrix):
    """
    Gets number of false negatives.
    :param indicator_matrix:  Two dimensional matrix of booleans
    :return: a tensor where the entry is 1 if that index is a false negative and 0 otherwise.
    """
    # check for false negatives
    fn_inds = []
    indices = torch.tensor([i for i in range(indicator_matrix.shape[1])])
    for idx in indices:
        # 1 if false negative, 0 otherwise
        val = 1
        for obj_indicators in indicator_matrix:
            if obj_indicators[idx] == True:
                val = 0
                break
        fn_inds.append(val)
    return torch.tensor(fn_inds)


def accumulated_tp_fp(tp_fp_indicators):
    """
    :param tp_fp_indicators: the index indicator tensor for the true/false positives
    :return: two tensors, one containing the true positive indices and one containing the false positive indices.
    """
    tp_list = []
    fp_list = []
    for idx in range(tp_fp_indicators.shape[0]):
        tp = torch.sum(tp_fp_indicators[: idx + 1])
        tp_list.append(tp)
        fp_list.append(tp_fp_indicators.shape[0] - tp)
    return torch.tensor(tp_list), torch.tensor(fp_list)


def AP(precisions, recalls):
    # AP for PASCAL VOC 2010
    vals = []
    for i in range(recalls.shape[0]):
        p_interp = torch.max(precisions[i:])
        vals.append(p_interp)
    return torch.mean(torch.tensor(vals))


def get_class_ap(class_id, predicts, annots, iou_thresh=0.5):
    # for troj AP
    # Gets average precision of a class on a single image at a certain threshold.
    # if predicts is list of dictionaries, take first entry
    if isinstance(predicts, list):
        predicts = predicts[0]
    # get objects of the given type from annotations and predictions
    obj_preds = get_objects_of_type(predicts, class_id, inc_scores=True)
    obj_annots = get_objects_of_type(annots, class_id, inc_scores=False)
    # compute IOU values between objects of class class_id in annotations and all predictions made by model
    iou_matrix = torchvision.ops.box_iou(
        obj_annots["boxes"].squeeze(1), obj_preds["boxes"].squeeze(1)
    )
    # Get the indices where the IOU of the bounding box is greater than the threshold.
    positive_det = iou_matrix >= iou_thresh
    # store the (transpose) positive detection matrix in the obj_preds dictionary
    obj_preds["iou_thresh_indicator"] = torch.transpose(positive_det, 0, 1)
    # now, sort obj_preds dictionary based on the descending confidence scores
    sorting_args = torch.argsort(obj_preds["scores"].squeeze(1), descending=True)
    sorted_obj_preds = {}
    for key in obj_preds.keys():
        sorted_obj_preds[key] = obj_preds[key][sorting_args]
    # Get the indices for ground truth objects corresponding to predictions. A -1 means a false positive.
    ind_matrix = sorted_obj_preds["iou_thresh_indicator"]
    false_negs = get_fn_indicators(ind_matrix)
    obj_annots["false_neg"] = false_negs
    gto = get_gt_indices(ind_matrix)
    sorted_obj_preds["gt_idx"] = gto
    # indicate whether prediction is true positive or false positive. In OD, true negative has no meaning, so it is ignored.
    tp_fp_tensor = get_tp_fp(sorted_obj_preds["gt_idx"])
    sorted_obj_preds["tp_fp_indicator"] = tp_fp_tensor
    # get accumulated true and false positives
    acc_tp, acc_fp = accumulated_tp_fp(tp_fp_tensor)
    sorted_obj_preds["acc_tp"] = acc_tp
    sorted_obj_preds["acc_fp"] = acc_fp
    # compute precision and recall at different confidences
    recalls = acc_tp / ind_matrix.shape[1]
    precisions = acc_tp / tp_fp_tensor.shape[0]
    sorted_obj_preds["recall"] = recalls
    sorted_obj_preds["precision"] = precisions
    av_prec = AP(precisions, recalls)
    return av_prec, sorted_obj_preds


def check_flip(predictions, ground_truth, obj_cat, iou_thresh=0.5, nms_thresh=0.05):
    """
    Checks for flips of the gt object.

    :param predictions: Model predictions (after nms)
    :param ground_truth: ground truth object.
    :param obj_cat: Deprecated
    :param iou_thresh: Minimum iou thresh to count as detection.
    :param nms_thresh: Deprecated
    :return:
    """

    nms_reduced_preds = predictions  # detect_dict_from_idx(predictions, pred_ids)
    reduced_preds = get_objects_of_type(nms_reduced_preds, obj_cat)
    if reduced_preds["boxes"].nelement() == 0:
        flip = 1
        return flip
        # return flip, nms_reduced_preds
    ious = torchvision.ops.box_iou(
        ground_truth["boxes"], reduced_preds["boxes"].squeeze(dim=1)
    )
    flip = 1
    if torch.max(ious) >= iou_thresh:
        flip = 0
    return flip


def nms_pred_reduce(predictions, nms_thresh=0.05):
    """
    Performs nms on predictions.
    :param predictions: original predictions.
    :param nms_thresh: Suppression threshold
    :return: Suppressed predictions
    """
    pred_ids = torchvision.ops.nms(
        predictions["boxes"], predictions["scores"], nms_thresh
    )
    nms_reduced_preds = detect_dict_from_idx(predictions, pred_ids)
    return nms_reduced_preds
