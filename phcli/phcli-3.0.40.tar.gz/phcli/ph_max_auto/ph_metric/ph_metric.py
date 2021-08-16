import os
import base64
from phcli.ph_logs.phLogs.ph_logs import phlogger
from phcli import define_value as dv
from phcli.ph_aws.ph_sts import PhSts
from phcli.ph_aws.ph_cloud_watch import PhCloudWatch, PhMetricData, PhMetricDataUnit


class PhMetric(object):
    def __init__(self):
        phsts = PhSts().assume_role(
            base64.b64decode(dv.ASSUME_ROLE_ARN).decode(),
            dv.ASSUME_ROLE_EXTERNAL_ID,
        )
        self.phcw = PhCloudWatch(phsts=phsts)
        self.cw_namespace = "Ph/Phcli"

    def _verify_call_type(self, call_type):
        return call_type if call_type in ["cli", "api"] else "unknown"

    def _format_dimensions(self, call_type, api, dag_name, job_name):
        return {
            "User": os.getenv("USER", "unknown"),
            "Type": call_type,
            "Group": 'maxauto',
            "API": api,
            "DAG_NAME": dag_name if dag_name else "debug",
            "JOB_NAME": job_name if job_name else "debug",
        }

    def _put_call_count(self, call_type, api, dag_name, job_name, call_state):
        phlogger.debug("put_metric_data >>> " + " ".join([call_type, api, dag_name, job_name, call_state]))

        call_type = self._verify_call_type(call_type)
        dimensions = self._format_dimensions(call_type, api, dag_name, job_name)

        return self.phcw.put_metric_data(
            self.cw_namespace,
            PhMetricData("TotalCall", dimensions, value=1.0, unit=PhMetricDataUnit.COUNT),
            PhMetricData("SuccessCall", dimensions, value=1.0 if call_state == "success" else 0.0, unit=PhMetricDataUnit.COUNT),
            PhMetricData("FailedCall", dimensions, value=0.0 if call_state == "success" else -1.0, unit=PhMetricDataUnit.COUNT),
        )

    def put_call_cli_count(self, api, dag_name="", job_name="", call_state="success"):
        return self._put_call_count("cli", api, dag_name, job_name, call_state)

    def put_call_api_count(self, api, dag_name, job_name, call_state="success"):
        return self._put_call_count("api", api, dag_name, job_name, call_state)

    def _put_call_duration_time(self, call_type, api, dag_name, job_name, call_state, duration_time: float):
        phlogger.debug("put_metric_data >>> " + " ".join([call_type, api, dag_name, job_name, call_state, str(duration_time)]))

        call_type = self._verify_call_type(call_type)
        dimensions = self._format_dimensions(call_type, api, dag_name, job_name)

        return self.phcw.put_metric_data(
            self.cw_namespace,
            PhMetricData("Duration", dimensions, value=duration_time if call_state == "success" else -1.0, unit=PhMetricDataUnit.MCS),
        )

    def put_call_cli_duration_time(self, api, dag_name="", job_name="", call_state="success", duration_time: float=0.0):
        return self._put_call_duration_time("cli", api, dag_name, job_name, call_state, duration_time)

    def put_call_api_duration_time(self, api, dag_name, job_name, call_state="success", duration_time: float=0.0):
        return self._put_call_duration_time("api", api, dag_name, job_name, call_state, duration_time)


if __name__ == '__main__':
    import datetime
    starttime = datetime.datetime.now()

    metric = PhMetric()
    metric.put_call_cli_count("maxauto.delete", call_state="failed")
    metric.put_call_cli_count("maxauto.create", call_state="success")
    metric.put_call_api_count("maxauto.delete", dag_name="test_dag", job_name="test_job", call_state="failed")
    metric.put_call_api_count("maxauto.create", dag_name="test_dag", job_name="test_job", call_state="success")

    metric.put_call_cli_duration_time("maxauto.create", call_state="success", duration_time=(datetime.datetime.now()-starttime).microseconds)
