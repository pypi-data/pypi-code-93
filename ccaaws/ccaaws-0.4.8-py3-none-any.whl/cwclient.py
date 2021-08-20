""" CloudWatch client
"""
import datetime
import sys

import ccalogging
from ccautils.errors import errorRaise

from ccaaws.botosession import BotoSession

log = ccalogging.log


class CWClient(BotoSession):
    """ CloudWatch object

    params:
        accountname: [required] this account name
                     used in the generation of metric data
                     as a dimension of each metric
        namespace:   [optional] the namespace for CW metrics
                     defaults to "ccaaws"
    """

    def __init__(self, accountname, namespace="ccaaws", **kwargs):
        super().__init__(**kwargs)
        self.newClient("cloudwatch")
        self.accountname = accountname
        self.namespace = namespace
        self.metrics = {self.namespace: []}

    def addMetric(self, name, value):
        """ adds a metric and it's value into the metrics array

        adds a metric and it's value into the metrics array
        with a unit of None

        params:
            name: [required] the metric name
            value:[required] the metric value
        """
        try:
            self.addUnitMetric(name, value, unit="None")
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def addUnitMetric(self, name, value, unit="None"):
        """ adds a metric and it's unit value into the metrics array

        params:
            name: [required] the metric name
            value:[required] the metric value
            unit: [optional] the unit one of
                  'Seconds'|'Microseconds'|'Milliseconds'
                  |'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'
                  |'Terabytes'|'Bits'|'Kilobits'|'Megabits'
                  |'Gigabits'|'Terabits'|'Percent'|'Count'
                  |'Bytes/Second'|'Kilobytes/Second'
                  |'Megabytes/Second'|'Gigabytes/Second'
                  |'Terabytes/Second'|'Bits/Second'
                  |'Kilobits/Second'|'Megabits/Second'
                  |'Gigabits/Second'|'Terabits/Second'
                  |'Count/Second'|'None'
                  defaults to "None"
        """
        try:
            xd = {
                "MetricName": name,
                "Dimensions": [{"Name": "AccountName", "Value": self.accountname,}],
                "Timestamp": datetime.datetime.now(),
                "Value": float(value),
                "Unit": unit,
                "StorageResolution": 60,
            }
            self.metrics[self.namespace].append(xd)
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def updateCW(self):
        """ posts the metrics to CloudWatch
        """
        try:
            for key in self.metrics:
                if len(self.metrics[key]) > 0:
                    self.client.put_metric_data(
                        Namespace=key, MetricData=self.metrics[key]
                    )
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)
