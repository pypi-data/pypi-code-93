from datetime import timedelta
from typing import List

import py4j


class TectonValidationError(ValueError):
    """
    Exception that indicates a problem in validating user inputs against
    the data in the system. Typically recoverable by the user.
    """


class AccessError(ValueError):
    """
    Exception that indicates a problem in accessing raw data. Information about connecting to data sources can be found here:
    https://docs.tecton.ai/v2/setting-up-tecton/03-connecting-data-sources.html
    """


class TectonInternalError(RuntimeError):
    """
    Exception that indicates an unexpected error within Tecton.
    Can be persistent or transient. Recovery typically requires involving
    Tecton support.
    """


def handleDataAccessErrors(func, details):
    try:
        return func()
    except Exception as e:
        if isinstance(
            e, py4j.protocol.Py4JJavaError
        ) and "com.amazonaws.services.s3.model.AmazonS3Exception: Forbidden" in str(e):
            raise AccessError(f"Unable to access file: {details}") from e
        raise e


def INGEST_DF_MISSING_COLUMNS(columns: List[str]):
    return TectonValidationError(f"Missing columns in the DataFrame: {', '.join(columns)}")


def INGEST_COLUMN_TYPE_MISMATCH(column_name: str, expected_type: str, actual_type: str):
    return TectonValidationError(
        f"Column type mismatch for column '{column_name}', expected {expected_type}, got {actual_type}"
    )


class TectonFeatureTimeError(TectonValidationError):
    def __init__(self, timestamp_key, feature_timestamp, feature_start_time, feature_end_time):
        super().__init__(
            f"Tecton feature query emitted record with feature timestamp {feature_timestamp}, which is not in the expected range of the query: [{feature_start_time}, {feature_end_time - timedelta(microseconds=1)}]. If you did not intend this value to be computed, please add a filter like `WHERE {timestamp_key} >= '{{context.feature_start_time_string}}' AND {timestamp_key} < '{{context.feature_end_time_string}}'` using tecton.materialization_context()"
        )
