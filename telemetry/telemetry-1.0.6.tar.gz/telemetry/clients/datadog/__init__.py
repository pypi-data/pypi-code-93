import os
from dateutil.parser import parse as dateutil_parser
from datadog_api_client.v1 import ApiClient, ApiException, Configuration
from datadog_api_client.v1.api import metrics_api
from datadog_api_client.v1.models import *
from pprint import pprint
# See configuration.py for a list of all supported configuration parameters.
configuration = Configuration()


class DataDogTelemeter:
    def __init__(self):
        self.configuration = Configuration()

    def guage(self, metric, *values):

# Enter a context with an instance of the API client
with ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = metrics_api.MetricsApi(api_client)
    body = MetricsPayload(
        series=[
            Series(
                host="test.example.com",
                interval=20,
                metric="system.load.1",
                points=[
                    Point([[1575317847,0.5]]),
                ],
                tags=["environment:test"],
                type="rate",
            ),
        ],
    )  # MetricsPayload |

    # example passing only required values which don't have defaults set
    try:
        # Submit metrics
        api_response = api_instance.submit_metrics(body)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling MetricsApi->submit_metrics: %s\n" % e)