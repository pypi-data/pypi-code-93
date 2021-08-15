import datetime as dt
import json

import pytz
from django import forms
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _
from django_scopes.forms import SafeModelChoiceField
from i18nfield.forms import I18nModelForm

from pretalx.api.serializers.room import AvailabilitySerializer
from pretalx.common.mixins.forms import ReadOnlyFlag
from pretalx.schedule.models import Availability, Room, TalkSlot


class AvailabilitiesFormMixin(forms.Form):
    availabilities = forms.CharField(
        label=_("Availability"),
        help_text=_(
            "Please click and drag to mark your availability during the conference with green blocks. "
            "We will try to schedule your slot during these times. You can click a block twice to remove it."
        ),
        widget=forms.TextInput(attrs={"class": "availabilities-editor-data"}),
        required=False,
    )

    def _serialize(self, event, instance):
        def is_valid(availability):
            return availability["end"] > availability["start"]

        if instance:
            availabilities = AvailabilitySerializer(
                instance.availabilities.all(), many=True
            ).data
        else:
            availabilities = []

        result = {
            "availabilities": [a for a in availabilities if is_valid(a)],
            "event": {
                "timezone": event.timezone,
                "date_from": str(event.date_from),
                "date_to": str(event.date_to),
            },
        }
        if self.resolution:
            result["resolution"] = self.resolution
        return json.dumps(result)

    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        self.resolution = kwargs.pop("resolution", None)
        initial = kwargs.pop("initial", dict())
        initial["availabilities"] = self._serialize(self.event, kwargs["instance"])
        if not isinstance(self, forms.BaseModelForm):
            kwargs.pop("instance")
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)
        if self.event and "availabilities" in self.fields:
            self.fields["availabilities"].help_text += " " + str(
                _("Please note that all times are in the event timezone, {tz}.")
            ).format(tz=self.event.timezone)

    def _parse_availabilities_json(self, jsonavailabilities):
        try:
            rawdata = json.loads(jsonavailabilities)
        except ValueError as e:
            raise forms.ValidationError(
                f"Submitted availabilities are not valid json: {e}."
            )
        if not isinstance(rawdata, dict):
            raise forms.ValidationError(
                f"Availability JSON does not comply with expected format: Should be object, but is {type(rawdata)}"
            )
        availabilities = rawdata.get("availabilities")
        if not isinstance(availabilities, list):
            raise forms.ValidationError(
                f"Availability JSON does not comply with expected format: `availabilities` should be a list, but is {type(availabilities)}"
            )
        return availabilities

    def _parse_datetime(self, strdate):
        tz = pytz.timezone(self.event.timezone)

        obj = parse_datetime(strdate)
        if not obj:
            raise TypeError
        if obj.tzinfo is None:
            obj = tz.localize(obj)

        return obj

    def _validate_availability(self, rawavail):
        message = _(
            "The submitted availability does not comply with the required format."
        )
        if not isinstance(rawavail, dict):
            raise forms.ValidationError(message)
        rawavail.pop("id", None)
        rawavail.pop("allDay", None)
        if not set(rawavail.keys()) == {"start", "end"}:
            raise forms.ValidationError(message)

        try:
            for key in ("start", "end"):
                raw_value = rawavail[key]
                if not isinstance(raw_value, dt.datetime):
                    rawavail[key] = self._parse_datetime(raw_value)
        except (TypeError, ValueError):
            raise forms.ValidationError(
                _("The submitted availability contains an invalid date.")
            )

        tz = pytz.timezone(self.event.timezone)

        timeframe_start = tz.localize(
            dt.datetime.combine(self.event.date_from, dt.time())
        )
        if rawavail["start"] < timeframe_start:
            rawavail["start"] = timeframe_start

        # add 1 day, not 24 hours, https://stackoverflow.com/a/25427822/2486196
        timeframe_end = dt.datetime.combine(self.event.date_to, dt.time())
        timeframe_end = timeframe_end + dt.timedelta(days=1)
        timeframe_end = tz.localize(timeframe_end, is_dst=None)
        # If the submitted availability ended outside the event timeframe, fix it silently
        rawavail["end"] = min(rawavail["end"], timeframe_end)

    def clean_availabilities(self):
        data = self.cleaned_data.get("availabilities")
        required = (
            "availabilities" in self.fields and self.fields["availabilities"].required
        )
        if not data:
            if required:
                raise forms.ValidationError(_("Please fill in your availability!"))
            return None

        rawavailabilities = (
            self.data["availabilities"]
            if isinstance(self.data.get("availabilities"), list)
            else self._parse_availabilities_json(data)
        )
        availabilities = []

        for rawavail in rawavailabilities:
            self._validate_availability(rawavail)
            availabilities.append(Availability(event_id=self.event.id, **rawavail))
        if not availabilities and required:
            raise forms.ValidationError(_("Please fill in your availability!"))
        return availabilities

    def _set_foreignkeys(self, instance, availabilities):
        """Set the reference to `instance` in each given availability.

        For example, set the availabilitiy.room_id to instance.id, in
        case instance of type Room.
        """
        reference_name = instance.availabilities.field.name + "_id"

        for avail in availabilities:
            setattr(avail, reference_name, instance.id)

    def _replace_availabilities(self, instance, availabilities):
        with transaction.atomic():
            # TODO: do not recreate objects unnecessarily, give the client the IDs, so we can track modifications and leave unchanged objects alone
            instance.availabilities.all().delete()
            Availability.objects.bulk_create(availabilities)

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        availabilities = self.cleaned_data.get("availabilities")

        if availabilities is not None:
            self._set_foreignkeys(instance, availabilities)
            self._replace_availabilities(instance, availabilities)

        return availabilities


class RoomForm(AvailabilitiesFormMixin, ReadOnlyFlag, I18nModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolution = "00:15:00"
        self.fields["name"].widget.attrs["placeholder"] = _("Room I")
        self.fields["description"].widget.attrs["placeholder"] = _(
            "Description, e.g.: Our main meeting place, Room I, enter from the right."
        )
        self.fields["speaker_info"].widget.attrs["placeholder"] = _(
            "Information for speakers, e.g.: Projector has only HDMI input."
        )
        self.fields["capacity"].widget.attrs["placeholder"] = "300"

    class Meta:
        model = Room
        fields = ["name", "description", "speaker_info", "capacity"]


class QuickScheduleForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))

    def __init__(self, event, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)
        self.fields["room"].queryset = self.event.rooms.all()
        if self.instance.start:
            self.fields["start_date"].initial = self.instance.start.date()
            self.fields["start_time"].initial = self.instance.start.time()
        else:
            self.fields["start_date"].initial = event.date_from

    def save(self):
        talk = self.instance
        tz = pytz.timezone(self.event.timezone)
        talk.start = tz.localize(
            dt.datetime.combine(
                self.cleaned_data["start_date"], self.cleaned_data["start_time"]
            )
        )
        talk.end = talk.start + dt.timedelta(minutes=talk.submission.get_duration())
        return super().save()

    class Meta:
        model = TalkSlot
        fields = ("room",)
        field_classes = {
            "room": SafeModelChoiceField,
        }
