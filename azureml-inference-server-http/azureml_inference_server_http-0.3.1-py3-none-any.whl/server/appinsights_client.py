import os
import json
import sys

import applicationinsights as appinsights


class AppInsightsClient(object):
    """Batching parameters, whichever of the below conditions gets hit first will trigger a send.
        send_interval: interval in seconds
        send_buffer_size: max number of items to batch before sending
    """
    send_interval = 5.0
    send_buffer_size = 100

    def __init__(self):
        self.enabled = False
        self._model_ids = self._get_model_ids()

        if os.getenv('AML_APP_INSIGHTS_ENABLED') == 'true' and 'AML_APP_INSIGHTS_KEY' in os.environ:
            instrumentation_key = os.getenv('AML_APP_INSIGHTS_KEY')
            exception_channel = self._make_telemetry_channel()
            self.telemetry_client = appinsights.TelemetryClient(instrumentation_key, exception_channel)
            self._request_channel = self._make_telemetry_channel()
            self._container_id = os.getenv('HOSTNAME', 'Unknown')
            self.enabled = True

        self.mdc_enabled = os.getenv('AML_MODEL_DC_STORAGE_ENABLED') == 'true'

    def log_app_insights_exception(self, ex):
        print("Error logging to Application Insights:")
        print(ex)

    def send_model_data_log(self, request_id, model_input, prediction):
        try:
            if not self.enabled or not self.mdc_enabled:
                return
            properties = {'Container Id': self._container_id,
                          'Request Id': request_id,
                          'Workspace Name': os.environ.get('WORKSPACE_NAME', ''),
                          'Service Name': os.environ.get('SERVICE_NAME', ''),
                          'Models': self._model_ids,
                          'Input': json.dumps(model_input),
                          'Prediction': json.dumps(prediction)}
            self.telemetry_client.track_trace('model_data_collection', properties)
        except Exception as ex:
            self.log_app_insights_exception(ex)

    def send_request_log(self, request_id, response_value, name, url, success, start_time, duration, response_code, http_method):
        try:
            if not self.enabled:
                return
            data = appinsights.channel.contracts.RequestData()
            data.id = request_id
            data.name = name
            data.start_time = start_time
            data.duration = self._calc_duration(duration)

            data.response_code = response_code
            data.success = success
            data.http_method = http_method
            data.url = url

            data.workspace_name = os.environ.get("WORKSPACE_NAME", "")
            data.service_name = os.environ.get("SERVICE_NAME", "")

            if not isinstance(response_value, str):
                response_value = response_value.decode('utf-8')
            data.properties = { 'Container Id': self._container_id, 'Response Value': json.dumps(response_value) }

            self._request_channel.write(data, self.telemetry_client.context)
        except Exception as ex:
            self.log_app_insights_exception(ex)

    def send_exception_log(self, exc_info, request_id='Unknown'):
        try:
            if not self.enabled:
                return
            properties_dict = { 'Container Id': self._container_id, 'Request Id': request_id }
            self.telemetry_client.track_exception(*exc_info, properties=properties_dict)
        except Exception as ex:
            self.log_app_insights_exception(ex)

    def _make_telemetry_channel(self):
        sender = appinsights.channel.AsynchronousSender(os.environ.get("AML_APP_INSIGHTS_ENDPOINT", "https://dc.services.visualstudio.com/v2/track"))
        sender.send_interval = AppInsightsClient.send_interval
        sender.send_buffer_size = AppInsightsClient.send_buffer_size
        queue = appinsights.channel.AsynchronousQueue(sender)
        telemetry_channel = appinsights.channel.TelemetryChannel(None, queue)
        return telemetry_channel

    def _calc_duration(self, duration):
        local_duration = duration or 0
        duration_parts = []
        for multiplier in [1000, 60, 60, 24]:
            duration_parts.append(local_duration % multiplier)
            local_duration //= multiplier
        duration_parts.reverse()
        formatted_duration = '%02d:%02d:%02d.%03d' % tuple(duration_parts)
        if local_duration:
            formatted_duration = '%d.%s' % (local_duration, formatted_duration)
        return formatted_duration

    def _get_model_ids(self):
        # Model information is stored in /var/azureml-app/model_config_map.json in AKS deployments. But, in ACI
        # deployments, that file does not exist due to a bug in container build-out code. Until the bug is fixed
        # /var/azureml-app/azureml-models will be used to enumerate all the models.
        # Details: https://msdata.visualstudio.com/Vienna/_workitems/edit/511413
        model_ids = []
        models_root_dir = os.path.join(os.environ.get('AML_APP_ROOT', '/var/azureml-app'), 'azureml-models')
        try:
            models = [str(model) for model in os.listdir(models_root_dir)]

            for model in models:
                versions = [int(version) for version in os.listdir(os.path.join(models_root_dir, model))]
                ids = ['{}:{}'.format(model, version) for version in versions]
                model_ids.extend(ids)
        except:
            self.send_exception_log(sys.exc_info())

        return model_ids
