from effdet import DetBenchTrain


class DetBenchTrainVal(DetBenchTrain):
    """
    Wrapper class around DetBenchTrain to override the forward method. DetBenchTrain computes detection on
    validation, which slows down the validation portion of the a training pipeline and is not always desirable.
    This module allows validation to be evaluated purely by the loss functions.
    """
    def __init__(self, model, config):
        """
        :param model: EfficientDet model to train.
        :param config: Model configuration dictionary.
        """
        super(DetBenchTrainVal, self).__init__(model, config)

    def forward(self, x, target):
        """
        Performs forward propagation on a batch.
        :param x: Batch of images.
        :param target: Batch of bounding box labels.
        :return: Output dictionary consisting of total loss, class loss, and box loss.
        """
        class_out, box_out = self.model(x)
        if self.anchor_labeler is None:
            # target should contain pre-computed anchor labels if labeler not present in bench
            assert 'label_num_positives' in target
            cls_targets = [target[f'label_cls_{l}'] for l in range(self.num_levels)]
            box_targets = [target[f'label_bbox_{l}'] for l in range(self.num_levels)]
            num_positives = target['label_num_positives']
        else:
            cls_targets, box_targets, num_positives = self.anchor_labeler.batch_label_anchors(
                target['bbox'], target['cls'])

        loss, class_loss, box_loss = self.loss_fn(class_out, box_out, cls_targets, box_targets, num_positives)
        output = {'loss': loss, 'class_loss': class_loss, 'box_loss': box_loss}
        return output
