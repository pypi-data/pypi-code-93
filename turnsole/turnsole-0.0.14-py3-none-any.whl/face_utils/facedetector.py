# -*- coding: utf-8 -*-
# @Author        : Antonio-hi
# @Email         : 9428.al@gmail.com
# @Create Date   : 2021-08-11 18:28:36
# @Last Modified : 2021-08-12 19:27:59
# @Description   : 

import os
import time
import numpy as np 
import tensorflow as tf

def convert_to_corners(boxes):
    """Changes the box format to corner coordinates

    Arguments:
      boxes: A tensor of rank 2 or higher with a shape of `(..., num_boxes, 4)`
        representing bounding boxes where each box is of the format
        `[x, y, width, height]`.

    Returns:
      converted boxes with shape same as that of boxes.
    """
    return tf.concat(
        [boxes[..., :2] - boxes[..., 2:] / 2.0, boxes[..., :2] + boxes[..., 2:] / 2.0],
        axis=-1,
    )

class AnchorBox:
    """Generates anchor boxes.

    This class has operations to generate anchor boxes for feature maps at
    strides `[8, 16, 32, 64, 128]`. Where each anchor each box is of the
    format `[x, y, width, height]`.

    Attributes:
      aspect_ratios: A list of float values representing the aspect ratios of
        the anchor boxes at each location on the feature map
      scales: A list of float values representing the scale of the anchor boxes
        at each location on the feature map.
      num_anchors: The number of anchor boxes at each location on feature map
      areas: A list of float values representing the areas of the anchor
        boxes for each feature map in the feature pyramid.
      strides: A list of float value representing the strides for each feature
        map in the feature pyramid.
    """

    def __init__(self):
        self.aspect_ratios = [0.5, 1.0, 2.0]
        self.scales = [2 ** x for x in [0, 1 / 3, 2 / 3]]

        self._num_anchors = len(self.aspect_ratios) * len(self.scales)
        self._strides = [2 ** i for i in range(3, 8)]
        self._areas = [x ** 2 for x in [32.0, 64.0, 128.0, 256.0, 512.0]]
        self._anchor_dims = self._compute_dims()

    def _compute_dims(self):
        """Computes anchor box dimensions for all ratios and scales at all levels
        of the feature pyramid.
        """
        anchor_dims_all = []
        for area in self._areas:
            anchor_dims = []
            for ratio in self.aspect_ratios:
                anchor_height = tf.math.sqrt(area / ratio)
                anchor_width = area / anchor_height
                dims = tf.reshape(
                    tf.stack([anchor_width, anchor_height], axis=-1), [1, 1, 2]
                )
                for scale in self.scales:
                    anchor_dims.append(scale * dims)
            anchor_dims_all.append(tf.stack(anchor_dims, axis=-2))
        return anchor_dims_all

    def _get_anchors(self, feature_height, feature_width, level):
        """Generates anchor boxes for a given feature map size and level

        Arguments:
          feature_height: An integer representing the height of the feature map.
          feature_width: An integer representing the width of the feature map.
          level: An integer representing the level of the feature map in the
            feature pyramid.

        Returns:
          anchor boxes with the shape
          `(feature_height * feature_width * num_anchors, 4)`
        """
        rx = tf.range(feature_width, dtype=tf.float32) + 0.5
        ry = tf.range(feature_height, dtype=tf.float32) + 0.5
        centers = tf.stack(tf.meshgrid(rx, ry), axis=-1) * self._strides[level - 3]
        centers = tf.expand_dims(centers, axis=-2)
        centers = tf.tile(centers, [1, 1, self._num_anchors, 1])
        dims = tf.tile(
            self._anchor_dims[level - 3], [feature_height, feature_width, 1, 1]
        )
        anchors = tf.concat([centers, dims], axis=-1)
        return tf.reshape(
            anchors, [feature_height * feature_width * self._num_anchors, 4]
        )

    def get_anchors(self, image_height, image_width):
        """Generates anchor boxes for all the feature maps of the feature pyramid.

        Arguments:
          image_height: Height of the input image.
          image_width: Width of the input image.

        Returns:
          anchor boxes for all the feature maps, stacked as a single tensor
            with shape `(total_anchors, 4)`
        """
        anchors = [
            self._get_anchors(
                tf.math.ceil(image_height / 2 ** i),
                tf.math.ceil(image_width / 2 ** i),
                i,
            )
            for i in range(3, 8)
        ]
        return tf.concat(anchors, axis=0)

class DecodePredictions(tf.keras.layers.Layer):
    """A Keras layer that decodes predictions of the RetinaNet model.

    Attributes:
      num_classes: Number of classes in the dataset
      confidence_threshold: Minimum class probability, below which detections
        are pruned.
      nms_iou_threshold: IOU threshold for the NMS operation
      max_detections_per_class: Maximum number of detections to retain per
       class.
      max_detections: Maximum number of detections to retain across all
        classes.
      box_variance: The scaling factors used to scale the bounding box
        predictions.
    """

    def __init__(
        self,
        num_classes=80,
        confidence_threshold=0.05,
        nms_iou_threshold=0.5,
        max_detections_per_class=100,
        max_detections=100,
        box_variance=[0.1, 0.1, 0.2, 0.2],
        **kwargs
    ):
        super(DecodePredictions, self).__init__(**kwargs)
        self.num_classes = num_classes
        self.confidence_threshold = confidence_threshold
        self.nms_iou_threshold = nms_iou_threshold
        self.max_detections_per_class = max_detections_per_class
        self.max_detections = max_detections

        self._anchor_box = AnchorBox()
        self._box_variance = tf.convert_to_tensor(
            [0.1, 0.1, 0.2, 0.2], dtype=tf.float32
        )

    def _decode_box_predictions(self, anchor_boxes, box_predictions):
        boxes = box_predictions * self._box_variance
        boxes = tf.concat(
            [
                boxes[:, :, :2] * anchor_boxes[:, :, 2:] + anchor_boxes[:, :, :2],
                tf.math.exp(boxes[:, :, 2:]) * anchor_boxes[:, :, 2:],
            ],
            axis=-1,
        )
        boxes_transformed = convert_to_corners(boxes)
        return boxes_transformed

    def _decode_landm_predictions(self, anchor_boxes, landm_predictions):               # anchor_boxes shape=(1, 138105, 4)
        landmarks = tf.reshape(landm_predictions,
            [tf.shape(landm_predictions)[0], tf.shape(anchor_boxes)[1], 5, 2])
        anchor_boxes = tf.broadcast_to(
            input=tf.expand_dims(anchor_boxes, 2),
            shape=[tf.shape(landm_predictions)[0], tf.shape(anchor_boxes)[1], 5, 4])
        landmarks *= (self._box_variance[:2] * anchor_boxes[:, :, :, 2:])
        landmarks += anchor_boxes[:, :, :, :2]
        return landmarks

    def call(self, images, predictions):
        image_shape = tf.cast(tf.shape(images), dtype=tf.float32)
        anchor_boxes = self._anchor_box.get_anchors(image_shape[1], image_shape[2])

        box_predictions = predictions[:, :, :4]
        cls_predictions = tf.nn.sigmoid(predictions[:, :, 4])
        landm_predictions = predictions[:, :, 5:15]

        boxes = self._decode_box_predictions(anchor_boxes[None, ...], box_predictions)
        landmarks = self._decode_landm_predictions(anchor_boxes[None, ...], landm_predictions)

        selected_indices = tf.image.non_max_suppression(
                                boxes=boxes[0],
                                scores=cls_predictions[0],
                                max_output_size=self.max_detections,
                                iou_threshold=0.5,
                                score_threshold=self.confidence_threshold
                                )
        selected_boxes = tf.gather(boxes[0], selected_indices)
        selected_landmarks = tf.gather(landmarks[0], selected_indices)

        return selected_boxes, selected_landmarks

class FaceDetector:
    def __init__(self, model_path, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        self.model = tf.keras.models.load_model(filepath=model_path,
                                                compile=False)
        self.inference_model = self.build_inference_model()

    def build_inference_model(self):
        image = self.model.input
        x = tf.keras.applications.mobilenet_v2.preprocess_input(image)
        predictions = self.model(x, training=False)
        detections = DecodePredictions(confidence_threshold=self.confidence_threshold)(image, predictions)
        inference_model = tf.keras.Model(inputs=image, outputs=detections)
        return inference_model

    def resize_and_pad_image(
        self, image, min_side=128.0, max_side=1333.0, jitter=[256, 960], stride=128.0
    ):
        """Resizes and pads image while preserving aspect ratio.

        Returns:
          image: Resized and padded image.
          image_shape: Shape of the image before padding.
          ratio: The scaling factor used to resize the image
        """
        image_shape = tf.cast(tf.shape(image)[:2], dtype=tf.float32)
        if jitter is not None:
            min_side = tf.random.uniform((), jitter[0], jitter[1], dtype=tf.float32)
        ratio = min_side / tf.reduce_min(image_shape)
        if ratio * tf.reduce_max(image_shape) > max_side:
            ratio = max_side / tf.reduce_max(image_shape)
        image_shape = ratio * image_shape      # tf.float32
        image = tf.image.resize(image, tf.cast(image_shape, dtype=tf.int32))
        padded_image_shape = tf.cast(
            tf.math.ceil(image_shape / stride) * stride, dtype=tf.int32
        )
        image = tf.image.pad_to_bounding_box(
            image, 0, 0, padded_image_shape[0], padded_image_shape[1]
        )
        return image, image_shape, ratio

    def predict(self, image, min_side=128):
        
        # input a image return boxes and landmarks
        image, _, ratio = self.resize_and_pad_image(image, min_side=min_side, jitter=None)

        detections = self.inference_model.predict(tf.expand_dims(image, axis=0))
        boxes, landmarks = detections

        boxes = np.array(boxes/ratio, dtype=np.int32)
        landmarks = np.array(landmarks/ratio, dtype=np.int32)
        return boxes, landmarks

        # 格式转换
        results = {
        'boxes': boxes.tolist(),
        'landmarks': landmarks.tolist(),
        }
        return results

if __name__ == '__main__':
    import cv2

    facedetector = FaceDetector(model_path='./model/facedetector.h5')

    image_path = '/home/lk/Project/Face_Age_Gender/data/WIDER/WIDER_train/images/28--Sports_Fan/28_Sports_Fan_Sports_Fan_28_615.jpg'
    # image_path = '/home/lk/Project/Face_Age_Gender/data/Emotion/emotion/010021_female_yellow_22/angry.jpg'

    image = cv2.imread(image_path)

    x = facedetector.predict(image, min_side=256)

    print(x)