from rest_framework import serializers

from huscy.email_recruitment import models, services


class InvitationEMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InvitationEMail
        fields = 'id', 'footer', 'project', 'text'
        read_only_fields = 'project',

    def create(self, validated_data):
        return services.create_invitation_email(**validated_data)


class UpdateInvitationEMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InvitationEMail
        fields = 'footer', 'text'

    def update(self, invitation_email, validated_data):
        return services.update_invitation_email(invitation_email, **validated_data)


class ReminderEMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReminderEMail
        fields = 'id', 'footer', 'project', 'text'
        read_only_fields = 'project',

    def create(self, validated_data):
        return services.create_reminder_email(**validated_data)


class UpdateReminderEMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReminderEMail
        fields = 'footer', 'text'

    def update(self, reminder_email, validated_data):
        return services.update_reminder_email(reminder_email, **validated_data)
