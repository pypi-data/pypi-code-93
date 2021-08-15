from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import CustomVisionErrorException, Image, ImageCreateSummary, ImageFileCreateBatch, ImageFileCreateEntry, ImageUrlCreateBatch, ImageUrlCreateEntry, Iteration, IterationPerformance, Tag
from elvia_louvre.louvre_client import LouvreClient
import logging
from louvre_vision.data_models import ClassificationTrainingImage, ImageRegion, ObjectDetectionTrainingImage, RegionBoundingBox, UploadImageEntry
from louvre_vision.dataset import ObjectDetectionDataset
import time
from typing import List, Optional, Union


class Train:
    """Class with methods to automate model training."""

    _train_client: CustomVisionTrainingClient

    def __init__(self, train_client: CustomVisionTrainingClient,
                 logger: logging.Logger):
        """TODO."""
        super().__init__()
        self._train_client = train_client
        self._logger = logger

    def publish_iteration(self, project_id: str, iteration_id: str,
                          publish_name: str, prediction_resource_id) -> bool:
        """Publish iteration."""

        return self._train_client.publish_iteration(
            project_id=project_id,
            iteration_id=iteration_id,
            publish_name=publish_name,
            prediction_id=prediction_resource_id)

    def delete_project(self, project_id: str) -> None:
        """
        Unpublishes any published iterations and then deletes a Custom Vision project.

        :param str project_id:

        :raises CustomVisionErrorException:
        """
        iterations = self._train_client.get_iterations(project_id=project_id)
        for iteration in iterations:
            try:
                self._logger.info(
                    user_message=f'Now unpublishing iteration {iteration.name}'
                )
                # All iterations must be unpublished before deleting the project
                self._train_client.unpublish_iteration(
                    project_id=project_id, iteration_id=iteration.id)
            except CustomVisionErrorException as exception:
                self._logger.warning(
                    user_message=
                    f'Iteration {iteration.name} ({iteration.id}) could not be unpublished: {exception}'
                )
        self._train_client.delete_project(project_id=project_id)

    def delete_project_by_name(
        self,
        project_name: str,
    ) -> bool:
        """
        Unpublishes any published iterations and then deletes a Custom Vision project.

        :param str project_name:

        :rtype: bool
        :return: True if success.

        :raises CustomVisionErrorException:
        """
        project_id = next((project.id
                           for project in self._train_client.get_projects()
                           if project.name == project_name), None)
        if project_id:
            self.delete_project(project_id=project_id)
            return True
        return False

    def extract_unique_categories(
        self, dataset: Union[List[ClassificationTrainingImage],
                             List[ObjectDetectionTrainingImage]]
    ) -> List[str]:
        """
        Return the unique categories from a list of images.
        
        :param dataset:
        :type dataset: List[ClassificationTrainingImage] | List[ObjectDetectionTrainingImage]
        
        :rtype: List[str]
        """
        tags = []
        for image in dataset:
            if isinstance(image, ClassificationTrainingImage):
                tags.extend(image.labels)
            elif isinstance(image, ObjectDetectionTrainingImage):
                for image_region in image.regions:
                    tags.append(image_region.tag_name)
        return list(set(tags))

    def upload_training_images(self,
                               project_id: str,
                               dataset: Union[
                                   List[ClassificationTrainingImage],
                                   List[ObjectDetectionTrainingImage]],
                               tags: List[Tag],
                               louvre_client: LouvreClient,
                               batch_size: int = 64,
                               using_production_images: bool = True) -> None:
        """
        Adds training images to a Custom Vision project. Accepts datasets with both 
        URLs and IDs.

        :param str project_id: Custom Vision project id
        :param dataset: List of images to be added to the Custom Vision project.
        :type dataset: List[ClassificationTrainingImage] | List[ObjectDetectionTrainingImage]
        :param tags: List with Tag objects corresponding to the Custom Vision project with id ``project_id``. 
        :type tags: List[Tag]
        :param int batch_size: Number of images in each upload batch. Each batch counts towards the number of Custom Vision transactions, the maximum batch size allowed by CV is 64.
        :param bool using_production_images: Whether to use production credentials when calling ImageAPI.

        :raises KeyException: If the metadata structure coming from ImageAPI does not match what's expected.
        :raises QueryError: If the request against ImageAPI fails.
        :raises RequestException: If problems fetching the image for resizing
        :raises ValueException: When the image is too small or doesn't exist
        :raises CustomVisionErrorException: If something fails when uploading to Custom Vision.
        """
        image_list: List[UploadImageEntry] = []

        for index in range(0, len(dataset)):
            # Populate image_list
            image_create_entry = dataset[index].get_imagecreateentry(
                tags=tags,
                louvre_client=louvre_client,
                using_production_images=using_production_images)
            if image_create_entry:
                image_list.append(
                    UploadImageEntry(
                        image_create_entry=image_create_entry,
                        metadata={'identifier': dataset[index].identifier}))

            self._logger.info(user_message='Progress: ' + str(index + 1) +
                              ' out of ' + str(len(dataset)) +
                              '; Just processed: ' + dataset[index].identifier)

            # Upload entries
            image_list = self._upload_images_if_batch_size_reached(
                project_id=project_id,
                image_list=image_list,
                batch_size=batch_size,
                force_dispatch=index == len(dataset) - 1
                and len(image_list) > 0)

    def _upload_images_if_batch_size_reached(
            self,
            project_id: str,
            image_list: List[UploadImageEntry],
            batch_size: int,
            force_dispatch: bool = False) -> List[UploadImageEntry]:
        """
        Manages image batch uploading to a Custom Vision project.
        If ``force_dispatch`` is False, the images are only uploaded if they are larger in number than
        the batch_size threshold value. The batch_size threshold applies separately for 
        ``ImageFileCreateEntry`` objects and ``ImageUrlCreateEntry`` objects.
        
        :param str project_id: Custom Vision project id.
        :param image_list: List of ``UploadImageEntry`` representing the images to be uploaded.
        :type image_list: List[UploadImageEntry]
        :param int batch_size: Number of images in each upload batch. The maximum batch size allowed by Custom Vision is 64. Larger values will be ignored.
        :param bool force_dispatch: Whether to upload the images even if they are fewer than batch_size.

        :rtype: List[UploadImageEntry]
        :returns: Remaining images not yet uploaded, if any.

        :raises CustomVisionErrorException: If something fails when uploading to Custom Vision.        
        """
        if batch_size > 64:
            batch_size = 64

        create_entry_classes = [ImageFileCreateEntry, ImageUrlCreateEntry]

        for create_entry_class in create_entry_classes:

            image_count = sum([
                1 for image in image_list
                if isinstance(image.image_create_entry, create_entry_class)
            ])

            if image_count and (force_dispatch or image_count == batch_size):
                images = [
                    image_list.pop(index)
                    for index in reversed(range(0, len(image_list)))
                    if isinstance(image_list[index].image_create_entry,
                                  create_entry_class)
                ]
                if create_entry_class == ImageUrlCreateEntry:
                    self._upload_imageurlcreateentry_batch(
                        project_id=project_id, images_batch=images)
                else:
                    self._upload_imagefilecreateentry_batch(
                        project_id=project_id, images_batch=images)

        return image_list

    def _upload_imageurlcreateentry_batch(
            self, project_id: str,
            images_batch: List[UploadImageEntry]) -> None:

        upload_result = self._train_client.create_images_from_urls(
            project_id=project_id,
            batch=ImageUrlCreateBatch(
                images=[entry.image_create_entry for entry in images_batch],
                metadata=images_batch[0].metadata
                if len(images_batch) == 1 else {}))
        self._log_upload_results(upload_result)

    def _upload_imagefilecreateentry_batch(
            self, project_id: str,
            images_batch: List[UploadImageEntry]) -> None:

        upload_result = self._train_client.create_images_from_files(
            project_id=project_id,
            batch=ImageFileCreateBatch(
                images=[entry.image_create_entry for entry in images_batch],
                metadata=images_batch[0].metadata
                if len(images_batch) == 1 else {}))
        self._log_upload_results(upload_result)

    def _log_upload_results(self, upload_result: Optional[ImageCreateSummary]):
        if upload_result:
            if not upload_result.is_batch_successful:
                self._logger.info(
                    user_message=
                    "There were some errors while uploading images: " + str([
                        "Image status: {} \n".format(upload_image.status)
                        for upload_image in upload_result.images
                    ]))
            else:
                self._logger.info(user_message=str(len(upload_result.images)) +
                                  ' images uploaded.')

    def train_project(self, project_id: str) -> Iteration:
        """
        Train the project.
        
        :param str project_id:
        :rtype: Iteration
        """
        self._logger.info("Now training...")
        iteration = self._train_client.train_project(project_id)
        while iteration.status != "Completed":
            iteration = self._train_client.get_iteration(
                project_id, iteration.id)
            self._logger.info("Training status: " + iteration.status)
            time.sleep(5)

        return iteration

    def get_iteration_performance(self, iteration: Iteration) -> dict:
        """
        Return the model performance stats seen on the web UI.
        
        :param Iteration iteration:
        :rtype: dict
        """
        performance: IterationPerformance = self._train_client.get_iteration_performance(
            iteration.project_id, iteration.id)
        result = {}
        tag_performance = {}
        for tag in performance.per_tag_performance:
            tag_performance[tag.name] = {
                'precision': tag.precision,
                'recall': tag.recall,
                'average_precision': tag.average_precision
            }
        result['precision'] = performance.precision
        result['recall'] = performance.recall
        result['F1 score'] = 2 * performance.precision * performance.recall / (
            performance.precision + performance.recall)
        result['average precision'] = performance.average_precision
        result['performance by tag'] = tag_performance

        return result

    def get_last_trained_published_iteration(
            self, project_id: str) -> Union[Iteration, None]:
        """
        Return the last-trained iteration among the published ones.
        
        :param str project_id:
        :rtype: Iteration | None
        """
        result: Optional[Iteration] = None
        iterations = self._train_client.get_iterations(project_id=project_id)
        if iterations is not None and len(iterations) > 0:
            train_date = None
            for iteration in iterations:
                if iteration.publish_name is not None and (
                        train_date is None
                        or train_date < iteration.trained_at):
                    train_date = iteration.trained_at
                    result = iteration
        return result

    def get_model(self, model_name: str) -> Union[Iteration, None]:
        """
        Return the latest published model for a given model name.
        
        :param str model_name:
        :rtype: Iteration | None        
        """

        for p in self._train_client.get_projects():
            if p.name == model_name:
                return self.get_last_trained_published_iteration(
                    project_id=p.id)

        return None

    def get_object_detection_project(
            self, project_id: str) -> ObjectDetectionDataset:
        """
        Return an object detection project from Custom Vision as a dataset object.
        Images will be ignored unless the Elvia ID is present in Custom Vision as metadata, which 
        is automatically taken care of if the upload process happens with batch size 1.

        :param str project_id:
        :rtype: ObjectDetectionDataset
        """
        images = self.get_custom_vision_project_images(project_id=project_id)

        training_images = []
        for image in images:
            if not len(image.metadata.keys()
                       ) > 0 or not 'identifier' in image.metadata.keys():
                continue
            regions = []
            for region in image.regions:
                regions.append(
                    ImageRegion(bounding_box=RegionBoundingBox(
                        top=region.top,
                        left=region.left,
                        width=region.width,
                        height=region.height),
                                tag_name=region.tag_name))
            training_images.append(
                ObjectDetectionTrainingImage(
                    identifier=image.metadata['identifier'], regions=regions))

        return ObjectDetectionDataset(images=training_images)

    def get_custom_vision_project_images(self, project_id: str) -> List[Image]:
        """
        :param str project_id:
        :rtype: List[azure.cognitiveservices.vision.customvision.training.models.Image]
        """
        step = 256
        skip = 0

        images = []
        while skip < self._train_client.get_tagged_image_count(
                project_id=project_id):
            images.extend(
                self._train_client.get_tagged_images(project_id,
                                                     skip=skip,
                                                     take=step))
            skip += step

        return images
