from rest_framework import serializers


class PaymentSerializer(serializers.Serializer):
    external_id = serializers.CharField(max_length=128)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2,
                                      coerce_to_string=True)
    currency = serializers.CharField(max_length=3)
    description = serializers.CharField(max_length=128, required=False,
                                        allow_blank=True)

    continue_url = serializers.URLField(required=False, allow_blank=True)
    notify_url = serializers.URLField(required=False, allow_blank=True)

    provider_code = serializers.CharField(max_length=256, required=False,
                                          allow_blank=True)


class NotifySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=256)
    timestamp = serializers.DateTimeField()
    payload = serializers.JSONField()
