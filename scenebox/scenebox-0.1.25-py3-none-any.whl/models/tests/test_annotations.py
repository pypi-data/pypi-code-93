import numpy as np
from shared.external.models.annotation import (BoundingBox, Polygon,
                                               BoundingBoxAnnotation, PolygonAnnotation,
                                               ClassificationAnnotation, Label,
                                               MRCNNAnnotation)


def test_create_mrcnn_annotation():
    annotation_id = "dd0f5995-ec1d-43fa-bfc8-f8a1f9c7b9fe_frame_0.ann"
    media_asset_id = "dd0f5995-ec1d-43fa-bfc8-f8a1f9c7b9fe_frame_0.png"
    formatted_response = {
        'labels': ['car'],
        'masks': None,
        'bounding_boxes': np.array([[467, 448, 487, 485], ], dtype=np.int32),
        'confidences': np.array([0.99512035], dtype=np.float32),
        'resolution': None
    }
    annotation_binary_id = "2b17d2fc-ae58-4df0-becd-4bdf6c2efd1b.ann"
    destination_set = None

    annotation = MRCNNAnnotation(
        id=annotation_id,
        media_asset_id=media_asset_id,
        file_labels=formatted_response,
        annotation_binary_id=annotation_binary_id,
        destination_set=destination_set)

    assert annotation.id == annotation_id
    assert annotation.annotation_type == 'two_d_bounding_box'
    assert annotation.ground_truth == 'false'
    assert annotation.inference_labelling_model == 'mrcnn'
    assert annotation.file_labels == formatted_response
    annotation_dict = annotation.to_dic()
    annotation_entities = annotation_dict['annotation_entities']
    annotation_entities[0].pop("uid")
    assert annotation_entities == \
        [
            {
                'annotation_type': 'two_d_bounding_box',
                'attributes': {},
                'category_id': None,
                'confidence': 0.9951203465461731,
                'coordinates': [{'x': 448.0, 'y': 467.0},
                                {'x': 485.0, 'y': 467.0},
                                {'x': 485.0, 'y': 487.0},
                                {'x': 448.0, 'y': 487.0}],
                'label': 'car',
                'related_annotations': []
            }
        ]


def test_create_bbox_annotation():
    media_asset_id = "test_bbox_asset_id"

    bboxes = []
    x_min = 10.0
    y_min = 11.0
    for i in range(3):
        bboxes.append(
            BoundingBox(x_min=x_min,
                        y_min=y_min,
                        x_max=x_min + 20 * (i + 1),
                        y_max=y_min + 25 * (i + 1),
                        label="test_label_{}".format(i),
                        confidence=0.7 + 0.1 * i,
                        category_id=i
                        )
        )

    annotation = BoundingBoxAnnotation(
        image_id=media_asset_id,
        bounding_boxes=bboxes,
        provider="my_model",
        ground_truth=False,
        version="my_model_version",
        id="test_bbox_ann_id"

    )

    assert annotation.id == "test_bbox_ann_id"
    assert annotation.asset_id == media_asset_id
    assert annotation.annotation_type == "two_d_bounding_box"
    assert annotation.ground_truth == "false"
    assert annotation.provider == "my_model"
    assert annotation.version == "my_model_version"
    annotation_dict = annotation.to_dic()
    annotation_entities = annotation_dict['annotation_entities']
    assert len(annotation_entities) == 3


def test_create_polygon_annotation():
    media_asset_id = "test_polygon_asset_id"

    polygons = []
    for i in range(3):
        polygons.append(
            Polygon(coordinates=[(100.0+10.0*i, 200.0-10.0*i),
                                 (150.0+10.0*i, 250.0-10.0*i),
                                 (300.0+10.0*i, 100.0-10.0*i),
                                 (100.0+10.0*i, 200.0-10.0*i)],
                    label="test_label_{}".format(i),
                    confidence=0.7 + 0.1 * i,
                    category_id=i
                    )
        )

    annotation = PolygonAnnotation(
        image_id=media_asset_id,
        polygons=polygons,
        provider="my_model",
        ground_truth=False,
        version="my_model_version",
        id="test_polygon_ann_id"

    )

    assert annotation.id == "test_polygon_ann_id"
    assert annotation.asset_id == media_asset_id
    assert annotation.annotation_type == "polygon"
    assert annotation.ground_truth == "false"
    assert annotation.provider == "my_model"
    assert annotation.version == "my_model_version"
    annotation_dict = annotation.to_dic()
    annotation_entities = annotation_dict['annotation_entities']
    assert len(annotation_entities) == 3


def test_create_classification_annotation():
    media_asset_id = "test_cls_asset_id"
    annotation = ClassificationAnnotation(
        asset_id=media_asset_id,
        labels=[Label(
            label="my_label",
            confidence=0.98,
            category_id=1,
            class_name="my_class_name"
        )],
        provider="my_model",
        ground_truth=False,
        version="my_model_version",
        id="test_cls_ann_id"
    )

    assert annotation.id == "test_cls_ann_id"
    assert annotation.asset_id == media_asset_id
    assert annotation.annotation_type == "classification"
    assert annotation.ground_truth == "false"
    assert annotation.provider == "my_model"
    assert annotation.version == "my_model_version"
    annotation_dict = annotation.to_dic()
    annotation_entities = annotation_dict['annotation_entities']
    assert len(annotation_entities) == 1
    assert annotation_entities[0]["label"] == "my_label"
    assert annotation_entities[0]["class_name"] == "my_class_name"
    assert annotation_entities[0]["confidence"] == 0.98
    assert annotation_entities[0]["category_id"] == 1
