import arrow
import json
from psycopg2._range import DateTimeTZRange

from django.conf import settings
from rest_framework.fields import ModelField


class DateTimeRangeSerializerField(ModelField):
    """
    Add timezone to upper and lower datetime values if they do not contain TZ-formatting.

    We need to do this to store the correct UTC value in the database, so the stored
    value is not actually the local time.

    If the stored value is actually the local time stored as "UTC", we end
    being one hour behind if the timezone for Norway.
    """
    def to_internal_value(self, data):
        rel = self.model_field.remote_field
        require_tz_adjust = False
        if data:
            data_dict = json.loads(data)
            iso_lower = data_dict.get('lower')
            iso_upper = data_dict.get('upper')
            require_tz_adjust = (iso_lower and '+' not in iso_lower) or (iso_upper and '+' not in iso_upper)
        if rel is not None:
            return rel.model._meta.get_field(rel.field_name).to_python(data)
        result = self.model_field.to_python(data)
        if require_tz_adjust:
            lower = result.lower
            upper = result.upper
            if lower is not None:
                lower = arrow.get(result.lower, settings.TIME_ZONE).datetime
            if upper is not None:
                upper = arrow.get(result.upper, settings.TIME_ZONE).datetime
            return DateTimeTZRange(lower, upper)
        return result

    def __isoformat_datetime(self, datetime):
        if datetime:
            return arrow.get(datetime).to(settings.TIME_ZONE).format('YYYY-MM-DD HH:mm:ss')
        return None

    def to_representation(self, obj):
        datetimerange_value = getattr(obj, self.field_name, None)
        if not datetimerange_value:
            return None
        data = {
            "bounds": "[)",
            "lower": self.__isoformat_datetime(datetimerange_value.lower),
            "upper": self.__isoformat_datetime(datetimerange_value.upper),
        }
        return json.dumps(data)
