"""Postprocessing utils for YOLO4."""
from typing import Tuple, List, Dict

import numpy as np
import tensorflow as tf

YOLO4_ANCHORS = np.array([
    [(12., 16.), (19., 36.), (40., 28.)],
    [(36., 75.), (76., 55.), (72., 146.)],
    [(142., 110.), (192., 243.), (459., 401.)]
])
STRIDES = (8, 16, 32)
XYSCALE = (1.2, 1.1, 1.05)


def decode_output(conv_outputs: Dict[str, np.ndarray], num_classes: int = 80) -> List[np.ndarray]:
    """
    Return tensor of shape [batch_size, output_size, output_size, anchor_per_scale, 5 + num_classes].

    Returns
    -------
    List[np.ndarray].
    """
    decoded_outputs = []
    for key in conv_outputs.keys():
        conv_output = conv_outputs[key]
        conv_shape = tf.shape(conv_output)
        batch_size = conv_shape[0]
        output_size_1, output_size_2 = conv_shape[1:3]

        conv_output = tf.reshape(conv_output, (batch_size, output_size_1, output_size_2, 3, 5 + num_classes))
        conv_raw_xywh, conv_raw_conf, conv_raw_prob = tf.split(conv_output, (4, 1, num_classes), -1)

        pred_conf = tf.sigmoid(conv_raw_conf)
        pred_prob = tf.sigmoid(conv_raw_prob)

        concat = tf.concat([conv_raw_xywh, pred_conf, pred_prob], -1).numpy()   # EagerTensor problems?
        decoded_outputs.append(concat)

    return decoded_outputs


def bboxes_iou(best_box: np.ndarray, remained_boxes: np.ndarray) -> np.ndarray:
    """
    Calculate IoU between the best bounding box and the remaining class boxes.

    Returns
    -------
    np.ndarray of IoUs.
    """
    best_box = np.array(best_box)
    remained_boxes = np.array(remained_boxes)

    boxes1_area = (best_box[..., 2] - best_box[..., 0]) * (best_box[..., 3] - best_box[..., 1])
    boxes2_area = (remained_boxes[..., 2] - remained_boxes[..., 0]) * (remained_boxes[..., 3] - remained_boxes[..., 1])

    left_up = np.maximum(best_box[..., :2], remained_boxes[..., :2])
    right_down = np.minimum(best_box[..., 2:], remained_boxes[..., 2:])

    inter_section = np.maximum(right_down - left_up, 0.0)
    inter_area = inter_section[..., 0] * inter_section[..., 1]
    union_area = boxes1_area + boxes2_area - inter_area
    ious = np.maximum(1.0 * inter_area / union_area, np.finfo(np.float32).eps)

    return ious


def yolo_head(feats: List[np.ndarray], anchors: np.ndarray,
              strides: Tuple[int, int, int], xyscale: Tuple[float, float, float]) -> np.ndarray:
    """
    Convert final layers features to initial bounding boxes parameters.

    Parameters
    ----------
    feats
        Outputs of a yolo4.
    anchors
        np.ndarray of anchors of yolo4.
    strides
        Tuple of strides of yolo4.
    xyscale
        Tuple of xyscales of yolo4.

    Returns
    -------
    np.ndarray of initial box coordinates, scores and classes confidences.
    """
    for i, pred in enumerate(feats):
        conv_shape = pred.shape
        output_size_2, output_size_1 = conv_shape[1:3]
        conv_raw_dxdy = pred[:, :, :, :, 0:2]
        conv_raw_dwdh = pred[:, :, :, :, 2:4]
        xy_grid = np.meshgrid(np.arange(output_size_1), np.arange(output_size_2))   # need to debug
        xy_grid = np.expand_dims(np.stack(xy_grid, axis=-1), axis=2)  # [gx, gy, 1, 2]

        xy_grid = np.tile(tf.expand_dims(xy_grid, axis=0), [1, 1, 1, 3, 1])
        xy_grid = xy_grid.astype(np.float)

        pred_xy = ((tf.sigmoid(conv_raw_dxdy) * xyscale[i]) - 0.5 * (xyscale[i] - 1) + xy_grid) * strides[i]
        pred_wh = (tf.exp(conv_raw_dwdh) * anchors[i])
        pred[:, :, :, :, 0:4] = tf.concat([pred_xy, pred_wh], -1)

    pred_bbox = [tf.reshape(x, (-1, tf.shape(x)[-1])) for x in feats]
    pred_bbox = tf.concat(pred_bbox, 0)
    return np.array(pred_bbox)


def yolo_boxes_and_scores(pred_bbox: np.ndarray,
                          image_shape: Tuple[int, int],
                          input_size: Tuple[int, int],
                          score_threshold: float = 0.5) -> np.ndarray:
    """
    Get corrected boxes.

    Parameters
    ----------
    pred_bbox
        Initially  postprocessed yolo4 outputs.
    input_size
        Size of the yolo4 input.

    Returns
    -------
    np.ndarray of scaled boxes, scores and classes.
    """
    yolo_w, yolo_h = input_size

    valid_scale = [0, np.inf]
    pred_bbox = pred_bbox

    pred_xywh = pred_bbox[:, 0:4]
    pred_conf = pred_bbox[:, 4]
    pred_prob = pred_bbox[:, 5:]

    # # (1) (x, y, w, h) --> (xmin, ymin, xmax, ymax)
    pred_coor = np.concatenate([pred_xywh[:, :2] - pred_xywh[:, 2:] * 0.5,
                                pred_xywh[:, :2] + pred_xywh[:, 2:] * 0.5], axis=-1)
    # # (2) (xmin, ymin, xmax, ymax) -> (xmin_org, ymin_org, xmax_org, ymax_org)
    org_h, org_w = image_shape
    resize_ratio = min(yolo_w / org_w, yolo_h / org_h)

    delta_w = (yolo_w - resize_ratio * org_w) / 2
    delta_h = (yolo_h - resize_ratio * org_h) / 2

    pred_coor[:, 0::2] = 1.0 * (pred_coor[:, 0::2] - delta_w) / resize_ratio
    pred_coor[:, 1::2] = 1.0 * (pred_coor[:, 1::2] - delta_h) / resize_ratio

    # # (3) clip some boxes those are out of range
    pred_coor = np.concatenate([np.maximum(pred_coor[:, :2], [0, 0]),
                                np.minimum(pred_coor[:, 2:], [org_w - 1, org_h - 1])], axis=-1)
    invalid_mask = np.logical_or((pred_coor[:, 0] > pred_coor[:, 2]), (pred_coor[:, 1] > pred_coor[:, 3]))
    pred_coor[invalid_mask] = 0

    # # (4) discard some invalid boxes
    bboxes_scale = np.sqrt(np.multiply.reduce(pred_coor[:, 2:4] - pred_coor[:, 0:2], axis=-1))
    scale_mask = np.logical_and((valid_scale[0] < bboxes_scale), (bboxes_scale < valid_scale[1]))

    # # (5) discard some boxes with low scores
    classes = np.argmax(pred_prob, axis=-1)
    scores = pred_conf * pred_prob[np.arange(len(pred_coor)), classes]
    score_mask = scores > score_threshold
    mask = np.logical_and(scale_mask, score_mask)
    coors, scores, classes = pred_coor[mask], scores[mask], classes[mask]

    return np.concatenate([coors, scores[:, np.newaxis], classes[:, np.newaxis]], axis=-1)


def nms(bboxes: np.ndarray, iou_threshold: float = 0.5, sigma: float = 0.3, method: str = 'nms') -> np.ndarray:
    """
    Perform nms.

    Parameters
    ----------
    bboxes: (xmin, ymin, xmax, ymax, score, class)

    Note: soft-nms, https://arxiv.org/pdf/1704.04503.pdf
        https://github.com/bharatsingh430/soft-nms

    iou_threshold
        IoU threshold for boxes
    sigma
        nms parameter
    method
        nms or soft-nms

    Returns
    -------
    nms processed boxes in format: np.ndarray of (class, xmin, ymin, xmax, ymax, score)
    """
    classes_in_img = list(set(bboxes[:, 5]))
    best_bboxes = []

    for cls in classes_in_img:
        cls_mask = (bboxes[:, 5] == cls)
        cls_bboxes = bboxes[cls_mask]

        while len(cls_bboxes) > 0:
            max_ind = np.argmax(cls_bboxes[:, 4])
            best_bbox = cls_bboxes[max_ind]
            #   (cls, box, score) for mAP calculation in IVA format
            best_bboxes.append([best_bbox[5], *best_bbox[:5]])
            cls_bboxes = np.concatenate([cls_bboxes[: max_ind], cls_bboxes[max_ind + 1:]])
            iou = bboxes_iou(best_bbox[np.newaxis, :4], cls_bboxes[:, :4])
            weight = np.ones((len(iou),), dtype=np.float32)

            assert method in ['nms', 'soft-nms']

            if method == 'nms':
                iou_mask = iou > iou_threshold
                weight[iou_mask] = 0.0

            if method == 'soft-nms':
                weight = np.exp(-(1.0 * iou ** 2 / sigma))

            cls_bboxes[:, 4] = cls_bboxes[:, 4] * weight
            score_mask = cls_bboxes[:, 4] > 0.
            cls_bboxes = cls_bboxes[score_mask]

    return np.array(best_bboxes)


def yolo_eval(yolo_outputs: Dict[str, np.ndarray],
              anchors: np.ndarray,
              strides: Tuple[int, int, int],
              xyscale: Tuple[float, float, float],
              image_shape: Tuple[int, int],
              yolo_size: Tuple[int, int] = (608, 608),
              num_classes: int = 80,
              score_threshold: float = 0.5,
              iou_threshold: float = 0.5) -> np.ndarray:
    """
    Evaluate YOLO4 model on given input and return filtered predictions.

    Parameters
    ----------
    yolo_outputs
        List of outputs of yolo4.
    anchors
        np.ndarray of anchors of yolo4.
    image_shape
        Shape of the initial input image.
    yolo_size
        Size of the yolo4 input.
    score_threshold
        Score threshold for detections.
    iou_threshold
        IoU threshold for boxes.

    Returns
    -------
    np.ndarray of classes, detected boxes and scores.
    """
    decoded_outputs = decode_output(yolo_outputs, num_classes)
    initial_bboxes = yolo_head(decoded_outputs, anchors, strides, xyscale)
    boxes_and_scores = yolo_boxes_and_scores(initial_bboxes, image_shape, yolo_size, score_threshold)
    predictions = nms(boxes_and_scores, iou_threshold, method='nms')

    return predictions
