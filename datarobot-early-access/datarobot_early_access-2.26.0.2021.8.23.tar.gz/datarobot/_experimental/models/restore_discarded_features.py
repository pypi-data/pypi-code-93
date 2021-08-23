import trafaret as t

from datarobot import ModelingFeature
from datarobot.client import get_client, staticproperty
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.models.api_object import APIObject
from datarobot.utils.pagination import unpaginate
from datarobot.utils.waiters import wait_for_async_resolution


class DiscardedFeaturesInfo(APIObject):
    """An object containing information about time series features which were reduced
    during time series feature generation process. These features can be restored back to the
    project. They will be included into All Time Series Features and can be used to create new
    feature lists.

    Attributes
    ----------
    total_restore_limit : int
      The total limit indicating how many features can be restored in this project.
    remaining_restore_limit : int
      The remaining available number of the features which can be restored in this project.
    features : list of strings
      Discarded features which can be restored.
    count : int
      Discarded features count.

    """

    _client = staticproperty(get_client)
    _get_url = "projects/{}/discardedFeatures/"
    _post_url = "projects/{}/modelingFeatures/fromDiscardedFeatures/"

    _converter = t.Dict(
        {
            t.Key("count"): t.Int(gte=0),
            t.Key("total_restore_limit"): t.Int(gte=0),
            t.Key("remaining_restore_limit"): t.Int(gte=0),
            t.Key("features"): t.List(t.String),
        }
    ).ignore_extra("*")

    def __init__(self, total_restore_limit, remaining_restore_limit, count, features):
        self.total_restore_limit = total_restore_limit
        self.remaining_restore_limit = remaining_restore_limit
        self.count = count
        self.features = features

    @classmethod
    def restore(cls, project_id, features_to_restore, max_wait=DEFAULT_MAX_WAIT):
        """Bring features back to the All Time Series Features.

        Parameters
        ----------
        project_id: string
        features_to_restore: list of strings
            List of the feature names to restore
        max_wait: int, optional
            max time to wait for features to be restored.
            Defaults to 10 min

        Returns
        -------
        modeling features: list of ModelingFeature objects
            List of all modeling features, including restored ones. Restored features have attribute
            `is_restored_after_reduction` set to True.

        """
        payload = {"features_to_restore": features_to_restore}
        response = cls._client.post(cls._post_url.format(project_id), data=payload)
        results_url = wait_for_async_resolution(
            cls._client, response.headers["Location"], max_wait=max_wait
        )
        return [
            ModelingFeature.from_server_data(item)
            for item in unpaginate(results_url, {}, cls._client)
        ]

    @classmethod
    def retrieve(cls, project_id):
        """

        Parameters
        ----------
        project_id: string

        Returns
        -------
        info: DiscardedFeaturesInfo
            information about features which were discarded during feature generation process and
            limits how many features can be restored.
        """
        return cls.from_location(cls._get_url.format(project_id))
