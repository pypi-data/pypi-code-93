import json
import time
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union
from urllib.parse import urljoin

import numpy as np
import pandas
import pyspark
import pytimeparse
import requests
from google.protobuf.json_format import MessageToJson

import tecton
from tecton import conf
from tecton import LoggingConfig
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton._internals.sdk_decorators import sdk_public_method
from tecton._internals.utils import infer_timestamp
from tecton._internals.utils import is_materializable_workspace
from tecton.fco import Fco
from tecton.feature_services.query_helper import _QueryHelper
from tecton.interactive.data_frame import DataFrame
from tecton.interactive.data_frame import FeatureVector
from tecton.interactive.dataset import Dataset
from tecton.interactive.feature_package import FeaturePackage
from tecton.interactive.feature_set_config import FeatureSetConfig
from tecton.interactive.feature_view import FeatureView
from tecton.tecton_context import TectonContext
from tecton_proto.api.featureservice.feature_service_pb2 import GetFeatureServiceStateRequest
from tecton_proto.data.feature_service_pb2 import FeatureService as FeatureServiceProto
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureServiceRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureServiceSummaryRequest
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger
from tecton_spark.transformation import RequestContext

logger = get_logger("FeatureService")


class FeatureService(Fco):
    """
    FeatureService class.

    FeatureServices are used to serve feature values from :class:`FeatureView`. Users can use FeatureServices
    to make offline requests (e.g. to fetch a training dataset) using the :py:meth:`get_feature_dataframe`
    method, and online requests (e.g. for online serving) using the :py:meth:`get_feature_vector`
    method. A FeatureService consists of a set of FeatureViews, plus configuration options.

    To get a FeatureService instance, call :py:func:`tecton.get_feature_service`.
    """

    proto: FeatureServiceProto
    feature_set_config: FeatureSetConfig
    _uri: str

    _query_helper: _QueryHelper

    def __init__(self):
        """ Do not call this directly. Use :py:func:`tecton.get_feature_service` """
        pass

    def __str__(self):
        return f"FeatureService|{self.name}"

    @classmethod
    def _from_proto(cls, feature_service: FeatureServiceProto):
        from tecton.interactive.feature_set_config import FeatureSetConfig

        obj = cls.__new__(cls)

        obj.proto = feature_service

        obj.feature_set_config = FeatureSetConfig._from_protos(feature_service.feature_set_items)

        # add dependent feature views into the FeatureSetConfig, uniquely per odfv
        # The namespaces of the dependencies have _udf_internal in the name and are filtered out before
        # being returned by TectonContext.execute()
        odfv_ids = set()
        for item in feature_service.feature_set_items:
            if item.enrichments.HasField("feature_view"):
                fv_id = IdHelper.to_string(item.feature_view_id)
                if fv_id in odfv_ids:
                    continue
                odfv_ids.add(fv_id)

                from tecton.interactive.feature_view import _find_dependent_feature_set_items

                inputs = _find_dependent_feature_set_items(
                    item.enrichments.feature_view.pipeline.root,
                    visited_inputs={},
                    fv_id=fv_id,
                )
                obj.feature_set_config._definitions_and_configs = (
                    obj.feature_set_config._definitions_and_configs + inputs
                )

        return obj

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "feature_service"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "feature_services"

    @property
    def _fco_metadata(self):
        return self.proto.fco_metadata

    @property  # type: ignore
    @sdk_public_method
    def feature_packages(self) -> List[FeaturePackage]:
        """
        Returns the Feature Packages enclosed in this FeatureService.
        """
        return [
            FeaturePackage._from_proto(d.fp) for d in self.feature_set_config.feature_packages if not d.is_feature_view
        ]

    @property  # type: ignore
    @sdk_public_method
    def feature_views(self) -> List[FeatureView]:
        """
        Returns the Feature Views enclosed in this FeatureService.
        """
        return [FeatureView(d.fv) for d in self.feature_set_config.feature_packages if d.is_feature_view]

    @property  # type: ignore
    @sdk_public_method
    def features(self) -> List[str]:
        """
        Returns the features generated by the enclosed feature views.
        """
        return self.feature_set_config.features

    @sdk_public_method
    def query_features(self, join_keys: Mapping[str, Union[np.int_, int, str, bytes]]) -> "tecton.DataFrame":
        """
        [Advanced Feature] Queries the FeatureService with a partial set of join_keys defined in the ``online_serving_index``
        of the included FeatureViews. Returns a Tecton :class:`DataFrame` of all matched records.

        :param join_keys: Query join keys, i.e., a union of join keys in the ``online_serving_index`` of all
            enclosed FeatureViews.
        :return: A Tecton :class:`DataFrame`
        """
        if not is_materializable_workspace(self.proto.fco_metadata.workspace):
            raise errors.UNSUPPORTED_OPERATION_IN_NON_PROD_WORKSPACE("query_features")
        if not self.proto.online_serving_enabled:
            raise errors.UNSUPPORTED_OPERATION(
                "query_features", "online_serving_enabled was not defined for this Feature Service."
            )
        if not isinstance(join_keys, dict):
            raise errors.INVALID_JOIN_KEYS_TYPE(type(join_keys))

        return _QueryHelper(self.proto.fco_metadata.workspace, feature_service_name=self.name).query_features(join_keys)

    @sdk_public_method
    def get_feature_vector(
        self,
        join_keys: Optional[Mapping[str, Union[int, np.int_, str, bytes]]] = None,
        include_join_keys_in_response: bool = False,
        request_context_map: Optional[Mapping[str, Union[int, np.int_, str, bytes, float]]] = None,
    ) -> FeatureVector:
        """
        Returns a single Tecton :class:`FeatureVector` from the Online Store.
        At least one of join_keys or request_context_map is required.

        :param join_keys: Join keys of the enclosed FeatureViews.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.
        :param request_context_map: Dictionary of request context values.

        :return: A :class:`FeatureVector` of the results.
        """
        if not is_materializable_workspace(self.proto.fco_metadata.workspace):
            raise errors.UNSUPPORTED_OPERATION_IN_NON_PROD_WORKSPACE("get_feature_vector")
        if not self.proto.online_serving_enabled:
            raise errors.UNSUPPORTED_OPERATION(
                "get_feature_vector", "online_serving_enabled was not defined for this Feature Service."
            )
        if join_keys is None and request_context_map is None:
            raise errors.FS_GET_FEATURE_VECTOR_REQUIRED_ARGS
        if join_keys is not None and not isinstance(join_keys, dict):
            raise errors.INVALID_JOIN_KEYS_TYPE(type(join_keys))
        if request_context_map is not None and not isinstance(request_context_map, dict):
            raise errors.INVALID_REQUEST_CONTEXT_TYPE(type(request_context_map))
        return _QueryHelper(self.proto.fco_metadata.workspace, feature_service_name=self.name).get_feature_vector(
            join_keys or {},
            include_join_keys_in_response,
            request_context_map or {},
            self._request_context,
        )

    @sdk_public_method
    def get_feature_dataframe(
        self,
        spine: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None],
        timestamp_key: Optional[str] = None,
        include_feature_package_timestamp_columns: bool = False,
        use_materialized_data: bool = True,
        save: bool = None,
        save_as: str = None,
    ) -> DataFrame:
        """
        Fetch a :class:`DataFrame` of feature values from this FeatureService.

        This method will return feature values for each row provided in the spine DataFrame. The feature values
        returned by this method will respect the timestamp provided in the timestamp column of the Spine DataFrame.

        This method fetches features from the Offline Store. If ``use_materialized_data==False``, feature values
        will instead be computed on the fly from raw data.

        :param spine: A dataframe of join keys and timestamps that specify which feature values to fetch.
        :param timestamp_key: Name of the time column in the spine dataframe. This column must be of type Spark timestamp.
        :param include_feature_package_timestamp_columns: (Optional) Include timestamp columns for each FeatureView in the FeatureService.
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled.
        :param save: (Optional) set to True to persist DataFrame as a Dataset object
        :param save_as: (Optional) name to save the DataFrame as. Not applicable when save=False.
            If unspecified and save=True, a name will be generated.
        :return: A Tecton :class:`DataFrame`.
        """
        TectonContext.validate_spine_type(spine)

        if timestamp_key is None:
            if spine is not None:
                timestamp_key = infer_timestamp(spine)
            else:
                keys = [fp.timestamp_key for fp in self.feature_packages if not fp.is_online]
                if len(keys) > 0:
                    if not all([key == keys[0] for key in keys]):
                        raise errors.FS_AMBIGUOUS_TIMESTAMP_KEY(keys)
                    timestamp_key = keys[0]

        df = self.feature_set_config.get_feature_dataframe(
            spine,
            timestamp_key=timestamp_key,
            include_feature_package_timestamp_columns=include_feature_package_timestamp_columns,
            use_materialized_data=use_materialized_data,
        )
        if save:
            return Dataset._create(
                df=df,
                save_as=save_as,
                feature_service_id=self.id,
                spine=spine,
                timestamp_key=timestamp_key,
            )
        return df

    @sdk_public_method
    def wait_until_ready(self, timeout="15m", wait_for_materialization=True, verbose=False):
        """Blocks until the service is ready to serve real-time requests.

        The FeatureService is considered ready once every FeatureView that has been added to it
        has had at least once successful materialization run.

        :param timeout: Timeout string.
        :param wait_for_materialization: If False, does not wait for batch materialization to complete.
        """
        if not is_materializable_workspace(self.proto.fco_metadata.workspace):
            raise errors.UNSUPPORTED_OPERATION_IN_NON_PROD_WORKSPACE("wait_until_ready")

        timeout_seconds = pytimeparse.parse(timeout)
        deadline = time.time() + timeout_seconds

        has_been_not_ready = False
        while True:
            request = GetFeatureServiceStateRequest()
            request.feature_service_locator.feature_service_name = self.name
            request.feature_service_locator.workspace_name = self.proto.fco_metadata.workspace
            http_response = requests.post(
                urljoin(conf.get_or_raise("FEATURE_SERVICE") + "/", "v1/feature-service/get-feature-service-state"),
                data=MessageToJson(request),
                headers=_QueryHelper(
                    self.proto.fco_metadata.workspace, feature_service_name=self.name
                )._prepare_headers(),
            )
            details = http_response.json()
            if http_response.status_code == 404:
                # FeatureService is not ready to serve
                if verbose:
                    logger.info(f" Waiting for FeatureService to be ready to serve ({details['message']})")
                else:
                    logger.info(f" Waiting for FeatureService to be ready to serve")
            elif http_response.status_code == 200:
                # FeatureService is ready
                if verbose:
                    logger.info(f"wait_until_ready: Ready! Response={http_response.text}")
                else:
                    logger.info(f"wait_until_ready: Ready!")
                # Extra wait time due to different FS hosts being potentially out-of-sync in picking up the latest state
                if has_been_not_ready:
                    time.sleep(20)
                return
            else:
                http_response.raise_for_status()
                return
            if time.time() > deadline:
                logger.info(f"wait_until_ready: Response={http_response.text}")
                raise TimeoutError()
            has_been_not_ready = True
            time.sleep(10)
            continue

    @sdk_public_method
    def summary(self) -> Displayable:
        """
        Returns various information about this FeatureService, including the most critical metadata such
        as the FeatureService's name, owner, features, etc.
        """
        return Displayable.from_items(headings=["Property", "Value"], items=self._summary_items())

    @property  # type: ignore
    @sdk_public_method
    def id(self) -> str:
        """
        Legacy attribute. Use name to refer to a FeatureService.
        """
        return IdHelper.to_string(self.proto.feature_service_id)

    def _summary_items(self):
        request = GetFeatureServiceSummaryRequest()
        request.feature_service_id.CopyFrom(self.proto.feature_service_id)
        request.workspace = self.workspace
        response = metadata_service.instance().GetFeatureServiceSummary(request)
        items_map = {}
        summary_items = []
        for item in response.general_items:
            items_map[item.key] = item
            if item.display_name:
                summary_items.append((item.display_name, item.multi_values if item.multi_values else item.value))

        if "curlEndpoint" in items_map and "curlParamsJson" in items_map:
            api_service = conf.get_or_none("API_SERVICE")
            assert api_service is not None, "API_SERVICE must be configured"
            if "localhost" not in api_service and "ingress" not in api_service:
                assert api_service.endswith(
                    "/api"
                ), "API_SERVICE should look like https://<deployment-name>.tecton.ai/api"
            service_url = urljoin(api_service, items_map["curlEndpoint"].value)
            curl_params_json = json.dumps(json.loads(items_map["curlParamsJson"].value), indent=2)
            curl_header = items_map["curlHeader"].value
            curl_str = "curl -X POST " + service_url + '\\\n-H "' + curl_header + "\"-d\\\n'" + curl_params_json + "'"
            summary_items.append(("Example Curl", curl_str))
        return summary_items

    @property
    def _request_context(self):
        merged_context = RequestContext({})
        for fp in self.feature_packages:
            if fp.is_online:
                merged_context._merge(fp._request_context)
        for fv in self.feature_views:
            if fv.is_online:
                merged_context._merge(fv._request_context)
        return merged_context

    @property
    def logging(self) -> Optional["LoggingConfig"]:
        """
        Returns the logging configuration of this FeatureService.
        """
        return LoggingConfig._from_proto(self.proto.logging)


@sdk_public_method
def get_feature_service(name: str, workspace_name: Optional[str] = None) -> FeatureService:
    """
    Fetch an existing :class:`FeatureService` by name.

    :param name: Name or string ID of the :class:`FeatureService`.
    :return: An instance of :class:`FeatureService`.
    """
    request = GetFeatureServiceRequest()
    request.service_reference = name
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetFeatureService(request)

    if not response.HasField("feature_service"):
        raise errors.FCO_NOT_FOUND(FeatureService, name)

    return FeatureService._from_proto(response.feature_service)
