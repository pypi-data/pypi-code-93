"""custom exceptions for the data platform Copyright 2020 Caliber Data Labs."""


#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#


class SearchError(Exception):
    pass


class InvalidFileError(Exception):
    pass


class FileSizeCheckError(Exception):
    pass


class InvalidPathError(Exception):
    pass


class InferenceLabellingError(Exception):
    pass


class AssetError(Exception):
    pass


class JobError(Exception):
    pass


class CredentialsError(Exception):
    pass


class InvalidAssetError(Exception):
    pass


class InvalidQueryError(Exception):
    pass


class InvalidAssetType(Exception):
    pass


class InvalidSetIdentifier(Exception):
    pass


class ResponseError(Exception):
    pass


class InvalidModelError(Exception):
    pass


class SessionManagerError(Exception):
    pass


class InvalidSessionError(Exception):
    pass


class InvalidRequestError(Exception):
    pass


class InvalidRosbagName(Exception):
    pass


class EmptySearchError(Exception):
    pass


class InvalidURLError(Exception):
    pass


class IndexingException(Exception):
    pass


class SessionDoesNotExistError(Exception):
    pass


class InvalidStorageSessionError(Exception):
    pass


class InvalidSessionDirectoryError(Exception):
    pass


class InvalidArgumentsError(Exception):
    pass


class MetadataNotFoundError(Exception):
    pass


class AnnotationSetNotFoundError(Exception):
    pass


class InvalidAnnotationError(Exception):
    pass


class InvalidConfigError(Exception):
    pass


class InvalidHLSOperationError(Exception):
    pass


class ZippingError(Exception):
    pass


class SetsError(Exception):
    pass


class RosbagError(Exception):
    pass


class ModelRegistrationError(Exception):
    pass


class InvalidEventError(Exception):
    pass


class DataEnrichmentError(Exception):
    pass


class TrafficObjectEnrichmentError(Exception):
    pass


class SessionError(Exception):
    pass


class RosIndexerConfigError(Exception):
    pass


class InvalidSessionMetadataException(Exception):
    pass


class InvalidTimeStringError(Exception):
    pass


class RosbagException(Exception):
    pass


class ProjectError(Exception):
    pass


class OperationError(Exception):
    pass


class InvalidAuthorization(Exception):
    pass


class UserManagerError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class HLSException(Exception):
    pass


class HLSIndexerError(Exception):
    pass


class IdentityError(Exception):
    pass


class AssetCompressionError(Exception):
    pass


class ThumbnailNotAvailableError(Exception):
    pass


class Rosbag2XvizConfigError(Exception):
    pass


class InvalidInfluenceTypeError(Exception):
    pass


class InvalidTimeError(Exception):
    pass


class KafkaProducerError(Exception):
    pass


class KafkaConsumerError(Exception):
    pass


class SchemaValidationError(Exception):
    pass


class UsageTrackerError(Exception):
    pass


class QuotaSystemError(Exception):
    pass


class QuotaExceedError(Exception):
    pass


class UploadError(Exception):
    pass


class SimilaritySearchError(Exception):
    pass


class AnnotationsError(Exception):
    pass
