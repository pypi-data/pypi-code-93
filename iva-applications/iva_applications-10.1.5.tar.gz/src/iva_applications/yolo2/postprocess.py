"""
Postprocessing utils for YOLO2.

Borrowed from https://github.com/jmpap/YOLOV2-Tensorflow-2.0
"""
from typing import Any, Dict
import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K
from PIL import ImageDraw, ImageFont
from iva_applications.mscoco17.config import ANCHORS, CLASS_NAMES


def scale_boxes(boxes: tf.Tensor, image_shape: tuple):
    """
    Scale boxes from output shape to original image shape.

    Parameters
    ----------
    boxes
        Boxes to scale.
    image_shape
        Original image shape.

    Returns
    -------
    Scaled boxes.
    """
    height = image_shape[0]
    width = image_shape[1]
    image_dims = K.stack([width, height, width, height])
    image_dims = K.reshape(image_dims, [1, 4])
    boxes = boxes * image_dims
    return boxes


def yolo_boxes_to_corners(box_xy: np.ndarray, box_wh: np.ndarray):
    """Convert boxes to corners."""
    box_xy1 = box_xy - 0.5 * box_wh
    box_xy2 = box_xy + 0.5 * box_wh
    boxes = K.concatenate((box_xy1, box_xy2), axis=-1)
    return boxes


def yolo_filter_boxes(box_confidence: tf.Tensor, boxes: tf.Tensor, box_class_probs: tf.Tensor,
                      confidence_threshold: float = .5):
    """Filter boxes by confidence threshold."""
    box_scores = box_confidence * box_class_probs
    box_classes = K.argmax(box_scores, axis=-1)  # best score index
    box_class_scores = K.max(box_scores, axis=-1)  # best score
    prediction_mask = box_class_scores >= confidence_threshold
    boxes = tf.boolean_mask(boxes, prediction_mask)
    scores = tf.boolean_mask(box_class_scores, prediction_mask)
    classes = tf.boolean_mask(box_classes, prediction_mask)
    return scores, boxes, classes


def yolo_head(feats: np.ndarray, anchors: Any, fmap_size: int, num_classes: int):
    """Convert final layer features to bounding box parameters.

    Parameters
    ----------
    feats : tensor
        Final convolutional layer features.
    anchors : array-like
        Anchor box widths and heights.
    fmap_size : int
        Size of a feature map cell.
    num_classes : int
        Number of target classes.

    Returns
    -------
    box_xy : tensor
        x, y box predictions adjusted by spatial location in conv layer.
    box_wh : tensor
        w, h box predictions adjusted by anchors and conv spatial resolution.
    box_confidence : tensor
        Probability estimate for whether each box contains any object.
    box_class_probs : tensor
        Probability distribution estimate for each box over class labels.
    """
    feats = feats.astype(np.float32)
    num_anchors = anchors.shape[0]
    result = tf.reshape(feats, (1, fmap_size, fmap_size, num_anchors, num_classes + 5))

    coord_x = tf.cast(tf.reshape(tf.tile(tf.range(fmap_size), [fmap_size]), (1, fmap_size, fmap_size, 1, 1)),
                      tf.float32)
    coord_y = tf.transpose(coord_x, (0, 2, 1, 3, 4))
    coords = tf.tile(tf.concat([coord_x, coord_y], -1), [1, 1, 1, 5, 1])
    dims = K.cast_to_floatx(K.int_shape(result)[1:3])
    dims = K.reshape(dims, (1, 1, 1, 1, 2))

    # pred_xy and pred_wh shape (m, fmap_size, fmap_size, Anchors, 2)
    pred_xy = K.sigmoid(result[:, :, :, :, 0:2])
    pred_xy = (pred_xy + coords)
    pred_xy = pred_xy / dims
    pred_wh = K.exp(result[:, :, :, :, 2:4])
    pred_wh = (pred_wh * anchors)
    pred_wh = pred_wh / dims
    # pred_confidence
    box_conf = K.sigmoid(result[:, :, :, :, 4:5])
    # pred_class
    box_class_prob = K.softmax(result[:, :, :, :, 5:])

    # Reshape
    box_xy = pred_xy[0, ...]
    box_wh = pred_wh[0, ...]
    box_confidence = box_conf[0, ...]
    box_class_probs = box_class_prob[0, ...]
    return box_confidence, box_xy, box_wh, box_class_probs


def draw_boxes(image, out_scores, out_boxes, out_classes, class_names, colors):
    """Draw boxes at original image."""
    font = ImageFont.truetype(font='/usr/share/fonts/liberation/LiberationSans-Regular.ttf',
                              size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
    thickness = (image.size[0] + image.size[1]) // 300
    for index, class_id in reversed(list(enumerate(out_classes))):
        predicted_class = class_names[class_id]
        box = out_boxes[index]
        score = out_scores[index]
        label = '{} {:.2f}'.format(predicted_class, score)
        draw = ImageDraw.Draw(image)
        label_size = draw.textsize(label, font)
        top, left, bottom, right = box
        top = max(0, np.floor(top + 0.5).astype('int32'))
        left = max(0, np.floor(left + 0.5).astype('int32'))
        bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
        right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
        print(label, (left, top), (right, bottom))
        if top - label_size[1] >= 0:
            text_origin = np.array([left, top - label_size[1]])
        else:
            text_origin = np.array([left, top + 1])
        # My kingdom for a good redistributable image drawing library.
        for j in range(thickness):
            draw.rectangle([left + j, top + j, right - j, bottom - j], outline=colors[class_id])
        draw.rectangle([tuple(text_origin), tuple(text_origin + label_size)], fill=colors[class_id])
        draw.text(text_origin, label, fill=(0, 0, 0), font=font)
        del draw


def yolo_non_max_suppression(scores: tf.Tensor, boxes: tf.Tensor, classes: tf.Tensor,
                             max_boxes: int = 20, iou_threshold: float = 0.5):
    """Non max suppression for boxes and scores."""
    nms_indices = tf.image.non_max_suppression(boxes, scores, max_boxes, iou_threshold)
    boxes = K.gather(boxes, nms_indices)
    scores = K.gather(scores, nms_indices)
    classes = K.gather(classes, nms_indices)
    return scores, boxes, classes


def yolo_eval(yolo_outputs: tuple, image_shape: tuple = (720., 1280.), max_boxes: int = 10,
              confidence_threshold: float = .5, iou_threshold: float = .5):
    """Postprocess yolo2 with TF utils."""
    box_confidence, box_xy, box_wh, box_class_probs = yolo_outputs
    boxes = yolo_boxes_to_corners(box_xy, box_wh)
    scores, boxes, classes = yolo_filter_boxes(
        box_confidence,
        boxes,
        box_class_probs,
        confidence_threshold=confidence_threshold)
    boxes = scale_boxes(boxes, image_shape)
    scores, boxes, classes = yolo_non_max_suppression(scores, boxes, classes,
                                                      max_boxes=max_boxes, iou_threshold=iou_threshold)
    boxes = boxes.numpy()
    scores = scores.numpy()
    classes = classes.numpy()
    return scores, boxes, classes


def get_spaced_colors(number):
    """Get spaced colors for drawing."""
    max_value = 255 ** 3
    interval = int(max_value / number)
    colors = [hex(ind)[2:].zfill(6) for ind in range(0, max_value, interval)]
    return [(int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)) for color in colors]


def get_postprocessed_predictions(predictions: Dict[str, np.ndarray], image_shape: tuple,
                                  confidence_threshold: float = .5, iou_threshold: float = .5,
                                  fmap_size: int = 19) -> tuple:
    """Convert output convolution tensor to final scores, boxes, classes."""
    anchors = np.array(ANCHORS)
    out_name = list(predictions.keys())[0]
    predictions = predictions[out_name]
    yolo_outputs = yolo_head(predictions, anchors, fmap_size, len(CLASS_NAMES))

    out_scores, out_boxes, out_classes = yolo_eval(yolo_outputs, image_shape,
                                                   confidence_threshold=confidence_threshold,
                                                   iou_threshold=iou_threshold)
    return out_scores, out_boxes, out_classes
