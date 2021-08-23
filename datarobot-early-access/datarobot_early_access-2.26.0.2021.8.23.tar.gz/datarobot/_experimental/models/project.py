from datarobot import AUTOPILOT_MODE
from datarobot import Project as datarobot_project
from datarobot._experimental.models.enums import UnsupervisedTypeEnum
from datarobot._experimental.models.model import CombinedModel
from datarobot._experimental.models.restore_discarded_features import DiscardedFeaturesInfo
from datarobot._experimental.models.segmentation import SegmentationTask
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.utils import deprecation_warning


class Project(datarobot_project):
    """
    Please see datarobot.Project for primary documentation.

    The experimental version of project adds the following functionality:
    - Add support for passing segmentation_task_id
    - Add support for restoring discarded features in time series projects
    """

    def set_target(
        self,
        target=None,
        mode=AUTOPILOT_MODE.QUICK,
        metric=None,
        quickrun=None,
        worker_count=None,
        positive_class=None,
        partitioning_method=None,
        featurelist_id=None,
        advanced_options=None,
        max_wait=DEFAULT_MAX_WAIT,
        target_type=None,
        credentials=None,
        feature_engineering_prediction_point=None,
        unsupervised_mode=False,
        relationships_configuration_id=None,
        segmentation_task_id=None,
        unsupervised_type=None,
        autopilot_cluster_list=None,
    ):
        """
        Set target variable of an existing project and begin the autopilot process (unless manual
        mode is specified).

        Target setting is asynchronous process, which means that after
        initial request we will keep polling status of async process
        that is responsible for target setting until it's finished.
        For SDK users this only means that this method might raise
        exceptions related to it's async nature.

        When execution returns to the caller, the autopilot process will already have commenced
        (again, unless manual mode is specified).

        Parameters
        ----------
        target : str, optional
            The name of the target column in the uploaded file. Should not be provided if
            ``unsupervised_mode`` is ``True``.
        mode : str, optional
            You can use ``AUTOPILOT_MODE`` enum to choose between

            * ``AUTOPILOT_MODE.FULL_AUTO``
            * ``AUTOPILOT_MODE.MANUAL``
            * ``AUTOPILOT_MODE.QUICK``
            * ``AUTOPILOT_MODE.COMPREHENSIVE``: Runs all blueprints in the repository (warning:
              this may be extremely slow).

            If unspecified, ``QUICK`` is used. If the ``MANUAL`` value is used, the model
            creation process will need to be started by executing the ``start_autopilot``
            function with the desired featurelist. It will start immediately otherwise.
        metric : str, optional
            Name of the metric to use for evaluating models. You can query
            the metrics available for the target by way of
            ``Project.get_metrics``. If none is specified, then the default
            recommended by DataRobot is used.
        quickrun : bool, optional
            Deprecated - pass ``AUTOPILOT_MODE.QUICK`` as mode instead.
            Sets whether project should be run in ``quick run`` mode. This
            setting causes DataRobot to recommend a more limited set of models
            in order to get a base set of models and insights more quickly.
        worker_count : int, optional
            The number of concurrent workers to request for this project. If
            `None`, then the default is used.
            (New in version v2.14) Setting this to -1 will request the maximum number
            available to your account.
        partitioning_method : PartitioningMethod object, optional
            Instance of one of the :ref:`Partition Classes <partitions_api>` defined in
            ``datarobot.helpers.partitioning_methods``.
        positive_class : str, float, or int; optional
            Specifies a level of the target column that should treated as the
            positive class for binary classification.  May only be specified
            for binary classification targets.
        featurelist_id : str, optional
            Specifies which feature list to use.
        advanced_options : AdvancedOptions, optional
            Used to set advanced options of project creation.
        max_wait : int, optional
            Time in seconds after which target setting is considered
            unsuccessful.
        target_type : str, optional
            Override the automatically selected target_type. An example usage would be setting the
            target_type='Mutliclass' when you want to preform a multiclass classification task on a
            numeric column that has a low cardinality. You can use ``TARGET_TYPE`` enum.
        credentials: list, optional,
             a list of credentials for the datasets used in relationship configuration
             (previously graphs).
        feature_engineering_prediction_point : str, optional
            additional aim parameter.
        unsupervised_mode : boolean, default ``False``
            (New in version v2.20) Specifies whether to create an unsupervised project. If ``True``,
            ``target`` may not be provided.
        relationships_configuration_id : str, optional
            (New in version v2.21) id of the relationships configuration to use
        segmentation_task_id : str or SegmentationTask, optional
            the segmentation task that should be used to split the project for segmented modeling.
        unsupervised_type : UnsupervisedTypeEnum, optional
            Specifies whether an unsupervised project is anomaly detection or clustering.
        autopilot_cluster_list : list(int), optional
            Specifies the list of clusters to build for each model during autopilot. Specifying
            multiple values in a list will build models with each number of clusters for
            the leaderboard.

        Returns
        -------
        project : Project
            The instance with updated attributes.

        Raises
        ------
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code
        AsyncProcessUnsuccessfulError
            Raised if target setting was unsuccessful
        AsyncTimeoutError
            Raised if target setting took more time, than specified
            by ``max_wait`` parameter
        TypeError
            Raised if ``advanced_options``, ``partitioning_method`` or
            ``target_type`` is provided, but is not of supported type

        See Also
        --------
        datarobot.models.Project.start : combines project creation, file upload, and target
            selection. Provides fewer options, but is useful for getting started quickly.
        """
        if quickrun:
            alternative = "Pass `AUTOPILOT_MODE.QUICK` as the mode instead."
            deprecation_warning(
                "quickrun parameter",
                deprecated_since_version="v2.4",
                will_remove_version="v3.0",
                message=alternative,
            )
        if mode == AUTOPILOT_MODE.QUICK or quickrun:
            mode = AUTOPILOT_MODE.FULL_AUTO
            quickrun = True
        elif mode == AUTOPILOT_MODE.FULL_AUTO and quickrun is None:
            quickrun = False

        if worker_count is not None:
            self.set_worker_count(worker_count)

        aim_payload = self._construct_aim_payload(target, mode, metric)

        if advanced_options is not None:
            self._load_advanced_options(advanced_options, aim_payload)
        if positive_class is not None:
            aim_payload["positive_class"] = positive_class
        if quickrun is not None:
            aim_payload["quickrun"] = quickrun
        if target_type is not None:
            aim_payload["target_type"] = self._validate_and_return_target_type(target_type)
        if featurelist_id is not None:
            aim_payload["featurelist_id"] = featurelist_id
        if credentials is not None:
            aim_payload["credentials"] = credentials
        if feature_engineering_prediction_point is not None:
            aim_payload[
                "feature_engineering_prediction_point"
            ] = feature_engineering_prediction_point
        if partitioning_method:
            self._load_partitioning_method(partitioning_method, aim_payload)
            partitioning_method.prep_payload(self.id, max_wait=max_wait)
        if unsupervised_mode:
            aim_payload["unsupervised_mode"] = unsupervised_mode
            if unsupervised_type:
                aim_payload["unsupervised_type"] = unsupervised_type
            if unsupervised_type == UnsupervisedTypeEnum.CLUSTERING:
                if autopilot_cluster_list:
                    if not isinstance(autopilot_cluster_list, list):
                        raise ValueError("autopilot_cluster_list must be a list of integers")
                    aim_payload["autopilot_cluster_list"] = autopilot_cluster_list
        if relationships_configuration_id is not None:
            aim_payload["relationships_configuration_id"] = relationships_configuration_id

        # SUPPORT FOR SEGMENTATION
        if segmentation_task_id is not None:
            if isinstance(segmentation_task_id, SegmentationTask):
                aim_payload["segmentation_task_id"] = segmentation_task_id.id
            elif isinstance(segmentation_task_id, str):
                aim_payload["segmentation_task_id"] = segmentation_task_id
            else:
                raise ValueError(
                    "segmentation_task_id must be either a string id or a SegmentationTask object"
                )

        url = "{}{}/aim/".format(self._path, self.id)
        response = self._client.patch(url, data=aim_payload)
        async_location = response.headers["Location"]

        # Waits for project to be ready for modeling, but ignores the return value
        self.from_async(async_location, max_wait=max_wait)

        self.refresh()
        return self

    def get_combined_models(self):
        models_response = self._client.get(
            "{}{}/combinedModels/".format(self._path, self.id)
        ).json()
        model_data_list = models_response["data"]
        return [CombinedModel.from_server_data(data) for data in model_data_list]

    def get_segments_models(self, combined_model_id=None):
        """Retrieve a list of all models belonging to the segments/child projects
        of the segmented project.

        Parameters
        ----------
        combined_model_id : str, optional
            Id of the combined model to get segments for. If there is only a single
            combined model it can be retrieved automatically, but this must be
            specified when there are > 1 combined models.
        use_project_id_keys : bool, optional

        Returns
        -------
        segments_models : list(dict)
            A list of dictionaries containing all of the segments/child projects,
            each with a list of their models ordered by metric from best to worst.

        """
        if combined_model_id is None:
            combined_model_list = self.get_combined_models()
            if len(combined_model_list) > 1:
                raise ValueError(
                    "More than 1 combined_model_id was found, please specify the id "
                    "that you wish to use."
                )
            combined_model = combined_model_list[0]
        else:
            combined_model = CombinedModel.get(
                project_id=self.id, combined_model_id=combined_model_id
            )

        segments = combined_model.get_segments_info()
        segments_models = []
        for segment in segments:
            project_id = segment.project_id
            project = Project.get(project_id)
            project_models = project.get_models()

            segments_models.append(
                {
                    "segment": segment.segment,
                    "project_id": project_id,
                    "parent_project_id": self.id,
                    "combined_model_id": combined_model.id,
                    "models": project_models,
                }
            )

        return segments_models

    def get_discarded_features(self):
        """ Retrieve discarded during feature generation features. Applicable for time
        series projects. Can be called at the modeling stage.

        Returns
        -------
        discarded_features_info: DiscardedFeaturesInfo
        """
        return DiscardedFeaturesInfo.retrieve(self.id)

    def restore_discarded_features(self, features, max_wait=DEFAULT_MAX_WAIT):
        """ Restore discarded during feature generation features. Applicable for time
        series projects. Can be called at the modeling stage.

        Returns
        -------
        modeling features: list of ModelingFeature objects
            List of all modeling features, including restored ones.
        """
        return DiscardedFeaturesInfo.restore(self.id, features, max_wait=max_wait)
