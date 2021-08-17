from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from tecton import LoggingConfig
from tecton._internals.feature_definition import FeatureDefinition
from tecton.feature_packages.feature_package import FeaturePackage
from tecton_proto.args import feature_service_pb2
from tecton_proto.args.basic_info_pb2 import BasicInfo
from tecton_proto.args.feature_service_pb2 import FeatureServiceArgs
from tecton_spark.id_helper import IdHelper


class FeaturesConfig(object):
    """
    Configuration used to specify a list of features.

    By default, you can add all of the features in a FeatureView to a FeatureService by passing
    the FeatureView into the ``features`` parameter of a FeatureService. However, if you want to specify a subset, you can use this class.

    You can use the double-bracket notation ``my_feature_view[[<features>]]``
    as a short-hand for generating a FeaturesConfig from a FeatureView. This is the preferred way to select a subset of
    of the features contained in a FeatureView. As an example:

    .. highlight:: python
    .. code-block:: python

       from tecton import FeatureService
       from feature_repo.features import my_feature_view_1, my_feature_view_2

       my_feature_service = FeatureService(
           name='my_feature_service',
           features=[
               # Add all features from my_feature_view_1 to this FeatureService
               my_feature_view_1,
               # Add a single feature from my_feature_view_2, 'my_feature'
               my_feature_view_2[['my_feature']]
           ]
       )

    :param namespace: (Optional) A namespace used to prefix the features joined from this FeatureView.
        By default, namespace is set to the FeatureView name.
    :param features: The subset of features to select from the FeatureView.
    :param override_join_keys: (advanced) map of spine join key to feature view join key overrides.
    :param feature_view: The Feature View.
    """

    def __init__(
        self,
        *,
        # This param should be renamed since it accepts more than just feature packages, but is a kwarg
        # and is referred to by users which makes it hard to change.
        feature_package: Optional[Union[FeaturePackage, FeatureDefinition]] = None,
        namespace: str = None,
        features: Optional[List[str]] = None,
        override_join_keys: Optional[Dict[str, str]] = None,
        feature_view: Optional[FeatureDefinition] = None
    ):
        self._fv = feature_view or feature_package
        assert self._fv is not None, "Either feature_package or feature_view must be set."
        self.namespace = namespace or self._fv.name
        self.features = features
        self.override_join_keys = override_join_keys
        self.id = self._fv._id()


def prepare_args(
    *,
    basic_info: BasicInfo,
    online_serving_enabled: bool,
    features: List[Union[FeaturesConfig, FeaturePackage, FeatureDefinition]],
    logging: Optional[LoggingConfig]
) -> FeatureServiceArgs:
    args = FeatureServiceArgs()
    args.feature_service_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
    args.info.CopyFrom(basic_info)
    args.online_serving_enabled = online_serving_enabled
    if logging is not None:
        args.logging.CopyFrom(logging._to_proto())
    for fp in features:
        fsfp = feature_service_pb2.FeatureServiceFeaturePackage()
        if isinstance(fp, FeaturePackage) or isinstance(fp, FeatureDefinition):
            # get default FeaturesConfig
            fp = fp[None]
        if fp.override_join_keys:
            fsfp.override_join_keys.extend(
                feature_service_pb2.ColumnPair(spine_column=k, feature_column=v)
                for k, v in sorted(fp.override_join_keys.items())
            )
        fsfp.feature_package_id.CopyFrom(fp.id)
        fsfp.namespace = fp.namespace
        fsfp.features.extend(fp.features)
        args.feature_packages.append(fsfp)
    return args
