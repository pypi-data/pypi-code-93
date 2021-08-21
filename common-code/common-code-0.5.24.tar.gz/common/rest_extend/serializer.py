from datetime import datetime
from rest_framework import serializers


def iot_date_validate_decorator(function):
    def wrapper(obj, data, *args, **kwargs):
        dateTo = data.get("dateTo")
        dateFrom = data.get("dateFrom")
        try:

            if "." in dateTo:
                dateTo = datetime.strptime(dateTo, "%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                dateTo = datetime.strptime(dateTo, "%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            raise serializers.ValidationError("dateTo： " + str(e))
        try:
            if "." in dateFrom:
                dateFrom = datetime.strptime(dateFrom, "%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                dateFrom = datetime.strptime(dateFrom, "%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            raise serializers.ValidationError("dateFrom： " + str(e))
        if dateTo < dateFrom:
            raise serializers.ValidationError("dateTo 需大于  dateFrom")

        return function(obj, data, *args, **kwargs)

    return wrapper


class BaseParamSerializer(serializers.Serializer):
    version = serializers.CharField(required=True, allow_blank=True)
    externalid = serializers.CharField(required=True, allow_blank=True)
    sn = serializers.CharField(required=True, allow_blank=True)
    ops = serializers.CharField(required=True, allow_blank=True)
    gateway_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    data = serializers.DictField(required=True)
