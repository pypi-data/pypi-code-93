"""Postprocessing utils for Tiny YOLO3."""
from typing import Tuple, Dict
import numpy as np
from iva_applications.yolo3.postprocess import yolo_eval_processing


TINY_YOLO3_ANCHORS = [
        (10., 14.), (23., 27.), (37., 58.),
        (81., 82.), (135., 169.), (344., 319.),
]


def yolo_eval(yolo_outputs: Dict[str, np.ndarray],
              num_classes: int,
              image_shape: Tuple[float, float],
              max_boxes: int = 20,
              score_threshold: float = .5,
              iou_threshold: float = .5) -> tuple:
    """
    Evaluate YOLO model on given input and return filtered boxes.

    Parameters
    ----------
    yolo_outputs
        List of outputs of yolo3/tiny_yolo3.
    anchors
        np.ndarray of anchors of yolo3/tiny_yolo3.
    num_classes
        Number of classes in dataset.
    image_shape
        Shape of the initial input image.
    max_boxes
        Maximum amount of boxes detected.
    score_threshold
        Score threshold for detections.
    iou_threshold
        IOU threshold for boxes.

    Returns
    -------
    Tuple of detected boxes, scores and classes.
    """
    out_names = list(yolo_outputs.keys())
    assert yolo_outputs[out_names[0]].shape == (1, 13, 13, 255)
    assert yolo_outputs[out_names[1]].shape == (1, 26, 26, 255)

    _yolo_outputs = [
        yolo_outputs[out_names[0]],
        yolo_outputs[out_names[1]]
    ]
    out_boxes, out_scores, out_classes = yolo_eval_processing(
        _yolo_outputs,
        TINY_YOLO3_ANCHORS,
        num_classes,
        image_shape,
        max_boxes,
        score_threshold,
        iou_threshold)
    return out_boxes, out_scores, out_classes
