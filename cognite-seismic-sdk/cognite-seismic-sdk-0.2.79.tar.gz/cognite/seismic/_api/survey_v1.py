# Copyright 2020 Cognite AS

import os
from typing import *

from cognite.seismic._api.api import API
from cognite.seismic._api.utility import get_exact_match_filter
from cognite.seismic.data_classes.api_types import Survey, SurveyGridTransformation
from cognite.seismic.data_classes.errors import SeismicServiceError
from grpc import StatusCode

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.types_pb2 import CRS, CoverageParameters
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import SearchSpec
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import SearchSurveysRequest
else:
    from cognite.seismic._api.shims import SearchSpec


class SurveyV1API(API):
    def __init__(self, query, metadata, v0_survey_api):
        super().__init__(metadata=metadata, query=query)
        self.v0_survey_api = v0_survey_api

    def list(
        self,
        list_seismics: bool = False,
        list_seismic_stores: bool = False,
        include_metadata: bool = False,
        crs: Optional[str] = None,
        in_wkt: Optional[bool] = None,
        include_grid_transformation: Optional[bool] = False,
        include_custom_coverage: Optional[bool] = False,
    ):
        """List all the surveys.
        Provide either crs or in_wkt to get surveys' coverage.

        Args:
            list_seismics (bool): true if the seismics ids from the surveys should be listed.
            list_seismic_stores (bool): true if seismic stores ids from the surveys should be listed. Only permitted if the user is a data manager (write access to all partitions).
            include_metadata (bool): true if metadata should be included in the response.
            crs(str): the crs in which the surveys' coverage is returned, default is original survey crs
            in_wkt(bool): surveys' coverage format, set to true if wkt format is needed, default is geojson format
            include_grid_transformation (bool): if set to True, return the user-specified transformation between bin grid and projected coordinates
            include_custom_coverage (bool): if set to True, return the customer-specified survey coverage

        Returns:
            List[Survey]: the requested surveys and their files (if requested).
        """

        return self._search_internal(
            [],
            list_seismics,
            list_seismic_stores,
            include_metadata,
            crs,
            in_wkt,
            include_grid_transformation,
            include_custom_coverage,
        )

    def search(
        self,
        name_substring: Optional[str] = None,
        survey_name_substring: Optional[str] = None,
        external_id_substring: Optional[str] = None,
        survey_external_id_substring: Optional[str] = None,
        survey_contains_exact_metadata: Optional[Mapping[str, str]] = None,
        list_seismics: bool = False,
        list_seismic_stores: bool = False,
        include_metadata: bool = False,
        crs: Optional[str] = None,
        in_wkt: Optional[bool] = None,
        include_grid_transformation: Optional[bool] = False,
        include_custom_coverage: Optional[bool] = False,
    ):
        """Search for subset of surveys.
        Provide either crs or in_wkt to get surveys' coverage.

        Args:
            name_substring (str): find surveys whose name contains this substring
            external_id_substring (str): find surveys whose external id contains this substring
            survey_contains_exact_metadata (Dict[str, str]): find surveys whose metadata contains an exact match of the keys and values of the provided metadata. It is also case-sensitive.
            list_seismics (bool): true if the seismics ids from the surveys should be listed.
            list_seismic_stores (bool): true if seismic stores ids from the surveys should be listed. Only permitted if the user is a data manager (write access to all partitions).
            include_metadata (bool): true if metadata should be included in the response.
            crs(str): the crs in which the surveys' coverage is returned, default is original survey crs
            in_wkt(bool): surveys' coverage format, set to true if wkt format is needed, default is geojson format
            include_grid_transformation (bool): if set to True, return the user-specified transformation between bin grid and projected coordinates
            include_custom_coverage (bool): if set to True, return the customer-specified survey coverage

        Returns:
            List[Survey]: the requested surveys and their files (if requested).
        """
        if name_substring is None:
            name_substring = survey_name_substring
        if external_id_substring is None:
            external_id_substring = survey_external_id_substring

        if name_substring is None and external_id_substring is None and survey_contains_exact_metadata is None:
            raise Exception(
                "one of survey_name_substring, survey_external_id_substring, survey_contains_exact_metadata must be specified"
            )

        search_specs = []
        if name_substring is not None:
            search_specs.append(SearchSpec(name_substring=name_substring))
        if external_id_substring is not None:
            search_specs.append(SearchSpec(external_id_substring=external_id_substring))
        if survey_contains_exact_metadata:
            metadata_filter = get_exact_match_filter(survey_contains_exact_metadata)
            search_specs.append(SearchSpec(metadata=metadata_filter))

        return self._search_internal(
            search_specs,
            list_seismics,
            list_seismic_stores,
            include_metadata,
            crs,
            in_wkt,
            include_grid_transformation,
            include_custom_coverage,
        )

    def get(
        self,
        id: Optional[str] = None,
        survey_id: Optional[str] = None,
        external_id: Optional[str] = None,
        survey_external_id: Optional[str] = None,
        name: Optional[str] = None,
        survey_name: Optional[str] = None,
        list_seismics: bool = False,
        list_seismic_stores: bool = False,
        include_metadata: bool = False,
        crs: Optional[str] = None,
        in_wkt: Optional[bool] = None,
        include_grid_transformation: Optional[bool] = False,
        include_custom_coverage: Optional[bool] = False,
    ):
        """
        Get a survey by either id, external_id or name.
        Provide either crs or in_wkt to get survey coverage.

        Args:
            id (str, optional): survey id.
            external_id (str, optional): survey external id.
            name (str, optional): survey name.
            list_seismics (bool): true if the ids of seismics from this survey should be listed.
            list_seismic_stores (bool): true if seismic stores ids from the surveys should be listed. Only permitted if the user is a data manager (write access to all partitions).
            include_metadata (bool): true if metadata should be included in the response.
            crs(str): the crs in which the survey coverage is returned, default is original survey crs
            in_wkt(bool): survey coverage format, set to true if wkt format is needed, default is geojson format
            include_grid_transformation (bool): if set to True, return the user-specified transformation between bin grid and projected coordinates
            include_custom_coverage (bool): if set to True, return the customer-specified survey coverage

        Returns:
            Survey: the requested survey, its seismics, seismic stores and metadata (if requested).
        """
        if id is None:
            id = survey_id
        if external_id is None:
            external_id = survey_external_id
        if name is None:
            name = survey_name

        search_spec = None
        if id is None and external_id is None and name is None:
            raise Exception("Must specify either survey_id, survey_name or survey_external_id.")

        if id is not None:
            search_spec = SearchSpec(id_string=id)
        elif external_id is not None:
            search_spec = SearchSpec(external_id=external_id)
        else:
            search_spec = SearchSpec(name=name)

        result = self._search_internal(
            [search_spec],
            list_seismics,
            list_seismic_stores,
            include_metadata,
            crs,
            in_wkt,
            include_grid_transformation,
            include_custom_coverage,
        )
        if len(result) == 0:
            raise SeismicServiceError(StatusCode.NOT_FOUND, "survey not found")
        else:
            return result[0]

    def register(
        self,
        name: str,
        survey_name: str,
        metadata: dict = None,
        external_id: Optional[str] = None,
        crs: Optional[str] = None,
        grid_transformation: Optional[SurveyGridTransformation] = None,
        custom_coverage_wkt: Optional[str] = None,
        custom_coverage_geojson: Optional[dict] = None,
    ):
        """Finds surveys for which the coverage area intersects with the given set of coordinates or exact metadata key-value match.

        Args:
            survey_name (str): survey name.
            metadata (dict): metadata of the survey.
            external_id: external id of the survey.
            crs (str): Coordinate reference system to be used by all
                                 members of this survey
            grid_transformation (SurveyGridTransformation):
                Manually specify an affine transformation between bin grid
                coordinates and projected crs coordinates, either using an
                origin point and the azimuth of the xline axis
                (:py:class:`~cognite.seismic.data_classes.api_types.P6Transformation`)
                or by specifying three or more corners of the grid as a list of
                :py:class:`~cognite.seismic.data_classes.api_types.DoubleTraceCoordinates`.
                This transformation must be valid for all members of this survey.
            custom_coverage_wkt (Optional[str]):
                Specify a custom coverage polygon for this survey in the wkt format
            custom_coverage_geojson (Optional[dict]):
                Specify a custom coverage polygon for this survey in the geojson format

        Returns:
            RegisterSurveyResponse: id, name and metadata of the survey.
        """
        if name is None:
            name = survey_name

        return self.v0_survey_api.register(
            name, metadata, external_id, crs, grid_transformation, custom_coverage_wkt, custom_coverage_geojson
        )

    def edit(
        self,
        id: Optional[str] = None,
        survey_id: Optional[str] = None,
        name: Optional[str] = None,
        survey_name: Optional[str] = None,
        metadata: dict = None,
        external_id: Optional[str] = None,
        survey_external_id: Optional[str] = None,
        crs: Optional[str] = None,
        grid_transformation: Optional[SurveyGridTransformation] = None,
        custom_coverage_wkt: Optional[str] = None,
        custom_coverage_geojson: Optional[dict] = None,
        clear_custom_coverage: Optional[bool] = False,
    ):
        """Edit a survey

        Args:
            id (Optional[str]): id of the survey to edit.
            name (Optional[str]): name of the survey to edit.
            metadata (dict): metadata of the survey to edit.
            crs (Optional[str]): Coordinate reference system to be used by all
                                 members of this survey
            grid_transformation (Optional[SurveyGridTransformation]):
                Manually specify an affine transformation between bin grid
                coordinates and projected crs coordinates, either using an
                origin point and the azimuth of the xline axis
                (:py:class:`~cognite.seismic.data_classes.api_types.P6Transformation`)
                or by specifying three or more corners of the grid as a list of
                :py:class:`~cognite.seismic.data_classes.api_types.DoubleTraceCoordinates`.
                This transformation must be valid for all members of this survey.
            custom_coverage_wkt (Optional[str]):
                Specify a custom coverage polygon for this survey in the wkt format
            custom_coverage_geojson (Optional[dict]):
                Specify a custom coverage polygon for this survey in the geojson format
            clear_custom_coverage (Optional[bool]):
                Set this to True to clear the custom coverage from this survey, so that coverage is 
                computed as a union of the coverage of the data sets included in the survey.

        Returns:
            EditSurveyResponse: id, name and metadata of the survey.

        """
        if id is None:
            id = survey_id
        if name is None:
            name = survey_name
        if external_id is None:
            external_id = survey_external_id
        return self.v0_survey_api.edit(
            id,
            name,
            metadata,
            external_id,
            crs,
            grid_transformation,
            custom_coverage_wkt,
            custom_coverage_geojson,
            clear_custom_coverage,
        )

    def delete(
        self,
        id: Optional[str] = None,
        survey_id: Optional[str] = None,
        name: Optional[str] = None,
        survey_name: Optional[str] = None,
    ):
        """Delete a survey

        Args:
            id (Optional[str]): id of the survey to delete.
            name (Optional[str]): name of the survey to delete.

        Returns:
            Nothing

        """
        if id is None:
            id = survey_id
        if name is None:
            name = survey_name
        return self.v0_survey_api.delete(id, name)

    def _search_internal(
        self,
        search_specs: List[SearchSpec],
        list_seismics: bool = False,
        list_seismic_stores: bool = False,
        include_metadata: bool = False,
        crs: Optional[str] = None,
        in_wkt: Optional[bool] = None,
        include_grid_transformation: Optional[bool] = False,
        include_custom_coverage: Optional[bool] = False,
    ):
        coverageParamCrs = CRS(crs=crs) if crs is not None else None
        coverageParams = (
            CoverageParameters(crs=coverageParamCrs, in_wkt=in_wkt)
            if coverageParamCrs is not None or in_wkt is not None
            else None
        )
        request = SearchSurveysRequest(
            surveys=search_specs,
            list_seismic_ids=list_seismics,
            list_seismic_store_ids=list_seismic_stores,
            include_metadata=include_metadata,
            include_coverage=coverageParams,
            include_grid_transformation=include_grid_transformation,
            include_custom_coverage=include_custom_coverage,
        )
        return [
            Survey.from_proto(survey_proto)
            for survey_proto in self.query.SearchSurveys(request, metadata=self.metadata)
        ]
