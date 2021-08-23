import json

import responses
from six.moves.urllib.parse import urljoin

from datarobot.models.visualai.augmentation import (
    ImageAugmentationList,
    ImageAugmentationOptions,
    ImageAugmentationSample,
)


@responses.activate
def test_augmentation_options(visualai_aug_options, augmentation_options_url, aug_pid):
    responses.add(
        responses.GET,
        augmentation_options_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_aug_options),
    )
    options = ImageAugmentationOptions.get(aug_pid)
    assert isinstance(options, ImageAugmentationOptions)

    from datarobot.utils import from_api

    data = from_api(visualai_aug_options)
    expected = ImageAugmentationOptions(**data)
    assert options.project_id == expected.project_id
    assert options.id == expected.id


@responses.activate
def test_augmentation_list_get(visualai_augmentation_list, image_augmentations_url):
    aug_id = visualai_augmentation_list["id"]
    aug_list_url = urljoin(image_augmentations_url, str(aug_id) + "/")
    responses.add(
        responses.GET,
        aug_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_augmentation_list),
    )
    aug_list = ImageAugmentationList.get(aug_id)
    assert isinstance(aug_list, ImageAugmentationList)
    assert aug_list.id == visualai_augmentation_list["id"]
    assert aug_list.project_id == visualai_augmentation_list["projectId"]


@responses.activate
def test_augmentation_list_create(visualai_augmentation_list, image_augmentations_url):
    aug_id = visualai_augmentation_list["id"]
    responses.add(
        responses.POST,
        image_augmentations_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"augmentationListId": aug_id}),
    )
    aug_list_url = urljoin(image_augmentations_url, str(aug_id) + "/")
    responses.add(
        responses.GET,
        aug_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_augmentation_list),
    )
    from datarobot.utils import from_api

    data = from_api(visualai_augmentation_list)
    del data["id"]
    name = data.pop("name")
    pid = data.pop("project_id")
    new_aug_list = ImageAugmentationList.create(name, pid, **data)
    assert isinstance(new_aug_list, ImageAugmentationList)


@responses.activate
def test_augmentation_sample_compute(
    visualai_augmentation_list, augmentation_samples_url, status_url, status_id
):
    responses.add(
        responses.POST,
        augmentation_samples_url,
        content_type="application/json",
        body=json.dumps({"status_id": status_id}),
        status=202,
        adding_headers={"Location": status_url},
    )
    from datarobot.utils import from_api

    data = from_api(visualai_augmentation_list)
    control_list = ImageAugmentationList(**data)
    ret_status_url = ImageAugmentationSample.compute(control_list, 4)
    assert ret_status_url == status_url


@responses.activate
def test_augmentation_sample_retrieve(augmentation_samples_url):
    sample_url = urljoin(augmentation_samples_url, "5e7e562528513130ab237875/")
    a_sample = {
        "imageId": "1234",
        "width": 256,
        "height": 256,
        "originalImageId": "5678",
        "project_id": "1234",
    }
    ret_data = {"totalCount": 1, "next": None, "previous": None, "data": [a_sample]}
    responses.add(responses.GET, sample_url, body=json.dumps(ret_data), status=200)

    ret_sample = ImageAugmentationSample.list("5e7e562528513130ab237875")
    assert len(ret_sample) == 1
    assert ret_sample[0].image_id == a_sample["imageId"]
    assert ret_sample[0].height == a_sample["height"]
    assert ret_sample[0].width == a_sample["width"]
    assert ret_sample[0].original_image_id == a_sample["originalImageId"]
