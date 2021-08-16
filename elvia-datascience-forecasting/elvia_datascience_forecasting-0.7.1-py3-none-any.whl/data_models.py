from dataclasses import dataclass
import uuid


# Log-friendly class that encapsulate the information of incoming HTTP requests
@dataclass
class EndpointRequest:
    """
    Represent an incoming request.

    :param str endpoint: Endpoint name
    """
    endpoint: str
    region_id: str
    trafo_id: str

    def __post_init__(self):
        """Generate a unique request ID to make easier the tracking of a particular request."""
        self.request_id = str(uuid.uuid4())

    def __str__(self) -> str:
        return \
f'''
{self.__class__.__name__}:
request_id= {str(self.request_id)};
endpoint= {str(self.endpoint)};
region_id= {str(self.region_id)};
trafo_id= {str(self.trafo_id)};
'''
