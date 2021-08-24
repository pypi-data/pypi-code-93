"""Postprocessing utils for YOLO3."""
from typing import Tuple, Dict, Any, List
import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K

from PIL import Image, ImageDraw, ImageFont
from iva_applications.yolo2.postprocess import get_spaced_colors
from iva_applications.mscoco17.config import CLASS_NAMES


YOLO3_ANCHORS = [
        (10., 13.), (16., 30.), (33., 23.),
        (30., 61.), (62., 45.), (59., 119.),
        (116., 90.), (156., 198.), (373., 326.)
]


def draw_boxes(
        img: Image,
        boxes: Any,
        font: str = '/usr/share/fonts/liberation/LiberationSans-Regular.ttf',
        class_names: list = CLASS_NAMES) -> Image:
    """
    Draws detected boxes on a single image.

    Parameters
    ----------
    img
        Pillow image used to be drawn at
    boxes
        boxes that should be drawn (in dict or np.ndarray format)
    font
        any font
    class_names
        list of class names
    Returns
    -------
    Pillow image with drawn boxes
    """
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font=font,
                              size=(img.size[0] + img.size[1]) // 100)
    colors = get_spaced_colors(len(class_names))
    if isinstance(boxes, dict):
        for cls in list(boxes.keys()):
            box_ = boxes[cls]
            if np.shape(box_)[0] != 0:
                box = box_[0]
                color = colors[cls]
                xy_coords, confidence = box[:4], box[4]
                xy_coords = np.asarray([xy_coords[0], xy_coords[1], xy_coords[2], xy_coords[3]])
                x0_coord, y0_coord = xy_coords[0], xy_coords[1]
                thickness = (img.size[0] + img.size[1]) // 200
                for tick in np.linspace(0, 1, thickness):
                    xy_coords[0], xy_coords[1] = xy_coords[0] + tick, xy_coords[1] + tick
                    xy_coords[2], xy_coords[3] = xy_coords[2] - tick, xy_coords[3] - tick
                    draw.rectangle(xy_coords, outline=tuple(color))
                text = '{} {:.1f}%'.format(class_names[cls],
                                           confidence * 100)
                text_size = draw.textsize(text, font=font)
                draw.rectangle(
                    [x0_coord, y0_coord - text_size[1], x0_coord + text_size[0], y0_coord],
                    fill=tuple(color))
                draw.text((x0_coord, y0_coord - text_size[1]), text, fill='black',
                          font=font)
    elif isinstance(boxes, np.ndarray):
        confidence = 0
        for cls in range(boxes.shape[0]):
            box = boxes[cls]
            color = colors[int(box[0])]
            class_ = int(box[0])
            if box.shape[0] == 6:
                xy_coords, confidence = box[1:5], box[5]
            else:
                xy_coords = box[1:5]
            xy_coords = np.asarray([xy_coords[0], xy_coords[1], xy_coords[2], xy_coords[3]])
            x0_coord, y0_coord = xy_coords[0], xy_coords[1]
            thickness = (img.size[0] + img.size[1]) // 200
            for tick in np.linspace(0, 1, thickness):
                xy_coords[0], xy_coords[1] = xy_coords[0] + tick, xy_coords[1] + tick
                xy_coords[2], xy_coords[3] = xy_coords[2] - tick, xy_coords[3] - tick
                draw.rectangle([xy_coords[0], xy_coords[1], xy_coords[2], xy_coords[3]], outline=tuple(color))
            if box.shape[0] == 6:
                text = '{} {:.1f}%'.format(class_names[class_], confidence * 100)
            else:
                text = '{}'.format(class_names[class_])
            text_size = draw.textsize(text, font=font)
            draw.rectangle(
                [x0_coord, y0_coord - text_size[1], x0_coord + text_size[0], y0_coord],
                fill=tuple(color))
            draw.text((x0_coord, y0_coord - text_size[1]), text, fill='white',
                      font=font)
    else:
        raise TypeError('unsupported type of boxes %s' % type(boxes))
    img = img.convert('RGB')
    return img


def yolo_head(feats: np.ndarray, anchors: np.ndarray, num_classes: int, input_shape: tf.Tensor) -> tuple:
    """
    Convert final layer features to bounding box parameters.

    Parameters
    ----------
    feats
        Output of a Conv layer.
    anchors
        np.ndarray of anchors of yolo3/tiny_yolo3.
    num_classes
        Number of classes in dataset.
    input_shape
        Input shape of the network.

    Returns
    -------
    Tuple of box coordinates, box size, score and class probability.
    """
    num_anchors = len(anchors)
    # feats = tf.constant(feats, dtype=tf.float32)
    # Reshape to batch, height, width, num_anchors, box_params.
    anchors_tensor = K.reshape(K.constant(anchors), [1, 1, 1, num_anchors, 2])

    grid_shape = K.shape(feats)[1:3]  # height, width
    grid_y = K.tile(K.reshape(K.arange(0, stop=grid_shape[0]), [-1, 1, 1, 1]),
                    [1, grid_shape[1], 1, 1])
    grid_x = K.tile(K.reshape(K.arange(0, stop=grid_shape[1]), [1, -1, 1, 1]),
                    [grid_shape[0], 1, 1, 1])
    grid = K.concatenate([grid_x, grid_y])
    grid = K.cast(grid, K.dtype(K.constant(feats)))

    feats = K.reshape(
        feats, [-1, grid_shape[0], grid_shape[1], num_anchors, num_classes + 5])

    # Adjust predictions to each spatial grid point and anchor size.
    box_xy = (K.sigmoid(feats[..., :2]) + grid) / K.cast(grid_shape[::-1], K.dtype(feats))
    box_wh = K.exp(feats[..., 2:4]) * anchors_tensor / K.cast(input_shape[::-1], K.dtype(feats))
    box_confidence = K.sigmoid(feats[..., 4:5])
    box_class_probs = K.sigmoid(feats[..., 5:])

    return box_xy, box_wh, box_confidence, box_class_probs


def yolo_correct_boxes(box_xy: tf.Tensor, box_wh: tf.Tensor, image_shape: Tuple[float, float]) -> tf.Tensor:
    """
    Get corrected boxes.

    Parameters
    ----------
    box_xy
        Box coordinates.
    box_wh
        Box size.
    image_shape
        Shape of the initial input image.

    Returns
    -------
    Tensor of scaled boxes.
    """
    box_yx = box_xy[..., ::-1]
    box_hw = box_wh[..., ::-1]
    image_shape = K.cast(image_shape, K.dtype(box_yx))

    box_mins = box_yx - (box_hw / 2.)
    box_maxes = box_yx + (box_hw / 2.)

    boxes = K.concatenate([
        box_mins[..., 1:2],  # x_min
        box_mins[..., 0:1],  # y_min
        box_maxes[..., 1:2],  # x_max
        box_maxes[..., 0:1]  # y_max
    ])

    # Scale boxes back to original image shape.
    boxes *= K.concatenate([image_shape, image_shape])
    return boxes


def yolo_boxes_and_scores(feats: np.ndarray, anchors: np.ndarray, num_classes: int,
                          input_shape: tf.Tensor, image_shape: Tuple[float, float]) -> tuple:
    """
    Process the output of the conv layer.

    Parameters
    ----------
    feats
        Output of a Conv layer.
    anchors
        np.ndarray of anchors of yolo3/tiny_yolo3.
    num_classes
        Number of classes in dataset.
    input_shape
        Input shape of the network.
    image_shape
        Shape of the initial input image.

    Returns
    -------
    Detected boxes and scores.
    """
    box_xy, box_wh, box_confidence, box_class_probs = yolo_head(feats,
                                                                anchors, num_classes, input_shape)
    boxes = yolo_correct_boxes(box_xy, box_wh, image_shape)
    boxes = K.reshape(boxes, [-1, 4])
    box_scores = box_confidence * box_class_probs
    box_scores = K.reshape(box_scores, [-1, num_classes])
    return boxes, box_scores


def yolo_eval_processing(
        yolo_outputs: List[np.ndarray],
        anchors: np.ndarray,
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
    num_layers = len(yolo_outputs)
    input_shape = K.shape(yolo_outputs[0])[1:3] * 32
    boxes = []
    box_scores = []
    for layer in range(num_layers):

        # FIXME: this ugly code is only for the purpose of creating DEMO benck ASAP!
        #  Major refactorign and redesign is neede for the whole module!
        if num_layers == 2:
            if layer == 0:
                _anchors = np.array(anchors[3:6])
            elif layer == 1:
                _anchors = np.array(anchors[0:3])
        if num_layers == 3:
            if layer == 0:
                _anchors = np.array(anchors[6:9])
            elif layer == 1:
                _anchors = np.array(anchors[3:6])
            elif layer == 2:
                _anchors = np.array(anchors[0:3])

        _boxes, _box_scores = yolo_boxes_and_scores(yolo_outputs[layer], _anchors,
                                                    num_classes, input_shape, image_shape)
        boxes.append(_boxes)
        box_scores.append(_box_scores)
    boxes = K.concatenate(boxes, axis=0)
    box_scores_tensor = K.concatenate(box_scores, axis=0)

    mask = box_scores_tensor >= score_threshold
    max_boxes_tensor = K.constant(max_boxes, dtype='int32')
    boxes_ = []
    scores_ = []
    classes_ = []
    for class_ in range(num_classes):
        class_boxes = tf.boolean_mask(boxes, mask[:, class_])
        class_box_scores = tf.boolean_mask(box_scores_tensor[:, class_], mask[:, class_])
        nms_index = tf.image.non_max_suppression(
            class_boxes, class_box_scores, max_boxes_tensor, iou_threshold=iou_threshold)
        class_boxes = K.gather(class_boxes, nms_index)
        class_box_scores = K.gather(class_box_scores, nms_index)
        classes = K.ones_like(class_box_scores, 'int32') * class_
        boxes_.append(class_boxes)
        scores_.append(class_box_scores)
        classes_.append(classes)
    out_boxes = K.concatenate(boxes_, axis=0)
    scores_tensor = K.concatenate(scores_, axis=0)
    classes_tensor = K.concatenate(classes_, axis=0)

    out_scores = tf.reshape(scores_tensor, (-1, 1))
    out_classes = tf.reshape(classes_tensor, (-1, 1))
    return out_boxes, out_scores, out_classes


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
    assert yolo_outputs[out_names[0]].shape == (1, 19, 19, 255)
    assert yolo_outputs[out_names[1]].shape == (1, 38, 38, 255)
    assert yolo_outputs[out_names[2]].shape == (1, 76, 76, 255)

    _yolo_outputs = [
        yolo_outputs[out_names[0]],
        yolo_outputs[out_names[1]],
        yolo_outputs[out_names[2]]
    ]
    _out_boxes, _out_scores, _out_classes = yolo_eval_processing(
        _yolo_outputs,
        YOLO3_ANCHORS,
        num_classes,
        image_shape,
        max_boxes,
        score_threshold,
        iou_threshold)
    return _out_boxes, _out_scores, _out_classes
