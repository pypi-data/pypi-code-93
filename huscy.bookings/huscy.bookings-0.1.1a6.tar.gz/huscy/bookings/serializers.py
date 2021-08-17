from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from huscy.bookings import models, services


class TimeslotSerializer(serializers.ModelSerializer):
    active = serializers.ReadOnlyField()
    session_title = serializers.CharField(source='session.title', read_only=True)

    class Meta:
        model = models.Timeslot
        fields = (
            'active',
            'id',
            'session',
            'session_title',
            'start',
            'end',
        )

    def create(self, validated_data):
        return services.add_timeslot(**validated_data)

    def update(self, instance, validated_data):
        try:
            return services.move_timeslot(instance, validated_data['start'])
        except services.BookingExistsException as e:
            raise ValidationError(e)
