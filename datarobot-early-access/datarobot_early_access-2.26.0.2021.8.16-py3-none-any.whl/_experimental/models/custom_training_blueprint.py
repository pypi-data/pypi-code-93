import trafaret as t

from datarobot import CustomModelVersion, ExecutionEnvironment, ExecutionEnvironmentVersion
from datarobot._compat import Int, String
from datarobot._experimental.models.custom_training_model import CustomTrainingModel
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2
from datarobot.utils.pagination import unpaginate


class CustomTrainingBlueprint(APIObject):
    """A custom training blueprint.

    .. versionadded:: v2.21

    Attributes
    ----------
    id: str
        user blueprint id
    custom_model_version: dict
        dict with 2 keys: `id` and `label`,
        where `id` is the ID of the custom model version
        and `label` is the version label
    training_history: list
        List of dicts with 6 keys:
        where `pid` is the ID of the project
        and `project_name` is the name of the project
        and `lid` is the leaderboard id
        and `creation_date` is a ISO-8601 timestamp of when the project
          the blueprint was trained on was created
        and `project_models_count` is the number of models in the project
          that the blueprint was trained on
        and `target_name` is the name of the project's target
    """

    _path = "customTrainingBlueprints/"
    _converter = t.Dict(
        {
            t.Key("user_blueprint_id") >> "id": String(),
            t.Key("custom_model_version"): t.Dict(
                {t.Key("id"): String(), t.Key("label"): String()}
            ),
            t.Key("training_history"): t.List(
                t.Dict(
                    {
                        t.Key("pid"): String(),
                        t.Key("project_name"): String(),
                        t.Key("lid"): String(),
                        t.Key("creation_date"): String(),
                        t.Key("project_models_count"): Int(),
                        t.Key("target_name"): String(),
                    }
                )
            ),
        }
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return encode_utf8_if_py2(u"{}({!r})".format(self.__class__.__name__, self.id))

    def _set_values(
        self, id, custom_model_version, training_history, project_id=None, filenames=None,
    ):
        self.id = id
        self.custom_model_version = custom_model_version
        self.training_history = training_history
        self.project_id = project_id
        self.filenames = filenames

    @classmethod
    def create(
        cls, custom_model_version_id=None, custom_model_id=None,
    ):
        """Create a custom training blueprint.

        .. versionadded:: v2.21

        Parameters
        ----------
        custom_model_version_id: Optional[str]
            the id of the custom model version
        custom_model_id: Optional[str]
            the id of the custom model


        if custom_model_id is provided, latest version will be used.

        Returns
        -------
        CustomTrainingBlueprint
            created custom training blueprint

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        if not custom_model_version_id:
            if not custom_model_id:
                raise ValueError(u"Must provide custom_model_version_id or custom_model_id")

            model = CustomTrainingModel.get(custom_model_id=custom_model_id)
            custom_model_version_id = model.latest_version.id
        payload = {
            "custom_model_version_id": custom_model_version_id,
        }
        response = cls._client.post(cls._path, data=payload)
        return cls.from_server_data(response.json())

    @classmethod
    def create_from_scratch(cls, name, environment_dir, training_code_files, target_type):
        desc = "Generated from python client"
        # Make environment
        ee = ExecutionEnvironment.create(
            name=name + "-environment", description=desc, programming_language="python"
        )
        ExecutionEnvironmentVersion.create(
            str(ee.id), environment_dir, description=desc,
        )

        # Make custom model
        cm = CustomTrainingModel.create(
            name=name + "-model", target_type=target_type, description=desc
        )
        cmv = CustomModelVersion.create_clean(
            custom_model_id=cm.id, base_environment_id=ee.id, files=training_code_files
        )

        blueprint = cls.create(custom_model_version_id=cmv.id)
        blueprint.filenames = training_code_files
        return blueprint

    @classmethod
    def create_from_dropin(
        cls, model_name, dropin_env_id, target_type, training_code_files=None, folder_path=None
    ):
        new_custom_training_model = CustomTrainingModel.create(
            name=model_name, target_type=target_type
        )
        cmv = CustomModelVersion.create_clean(
            new_custom_training_model.id,
            base_environment_id=dropin_env_id,
            files=training_code_files,
            folder_path=folder_path,
        )
        blueprint = cls.create(custom_model_version_id=cmv.id)
        blueprint.filenames = training_code_files
        return blueprint

    @classmethod
    def list(cls):
        """List custom training blueprints.

        .. versionadded:: v2.21

        Returns
        -------
        List[CustomTrainingBlueprint]
            a list of custom learning blueprints

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        data = unpaginate(cls._path, {}, cls._client)
        return [cls.from_server_data(item) for item in data]
