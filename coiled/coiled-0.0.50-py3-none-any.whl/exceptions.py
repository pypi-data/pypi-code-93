class CoiledException(Exception):
    """Custom exception to be used as a base exception.

    This exception needs to include a `code` argument which is
    a constant variable that will give us more information as to
    where the exception happened.

    """

    code = "COILED_EXCEPTION"

    def __init__(self, message: str, **kwargs):
        super().__init__(message)
        self.message = message
        self.extras = kwargs

    def __repr__(self) -> str:
        return f"CoiledException({self.code}: {self.message})"

    def as_json(self) -> dict:
        return {"code": self.code, "message": self.message, **self.extras}


class UnsupportedBackendError(CoiledException):
    code = "UNSUPPORTED_BACKEND"


class ParameterMissingError(CoiledException):
    code = "PARAMETER_MISSING_ERROR"


class GCPCredentialsParameterError(ParameterMissingError):
    code = "GCP_PARAMETER_MISSING_ERROR"


class GCPCredentialsError(CoiledException):
    code = "CREDENTIALS_ERROR"


class AWSCredentialsParameterError(ParameterMissingError):
    code = "AWS_PARAMETER_MISSING_ERROR"


class AzureCredentialsParameterError(ParameterMissingError):
    code = "AZURE_PARAMETER_MISSING_ERROR"


class RegistryParameterError(ParameterMissingError):
    code = "REGISTRY_PARAMETER_ERROR"
