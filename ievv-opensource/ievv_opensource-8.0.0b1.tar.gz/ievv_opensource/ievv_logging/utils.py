"""
An easy to use interface for logging events to the database models in this app.


By using this you can easily log and have a useful overview about what
is going on in e.g. scheduled scripts.

To use, add ievv_opensource.ievv_logging to INSTALLED_APPS. Run migrate, and for example
if you are running a management script called "the_foo_script" nightly, do:

    from ievv_opensource.ievv_logging.utils import IevvLogging

    ievvlogging = IevvLogging(__name__) # or any custom preferred name like 'the_foo_script'
    ievvlogging.begin()

    # the script does its work

    ievvlogging.finish(
        number_of_users_updated=12,
        number_of_users_anonymized=4
    )

"""
from django.utils import timezone

from .models import IevvLoggingEventBase, IevvLoggingEventItem


def getDuration(from_dt, to_dt, interval='default'):
    """
    Examples:

        from_dt = datetime(2019, 3, 5, 23, 8, 15)
        to_dt = datetime.now()

        print(getDuration(from_dt, to_dt))
        print(getDuration(from_dt, to_dt, interval='seconds'))
        print(getDuration(from_dt, to_dt, interval='minutes'))
    """
    duration = to_dt - from_dt
    duration_in_s = duration.total_seconds()

    def years():
        return divmod(duration_in_s, 31556926) # Seconds in a year=31556926.

    def days(seconds = None):
        return divmod(seconds or duration_in_s, 86400) # Seconds in a day = 86400

    def hours(seconds = None):
        return divmod(seconds or duration_in_s, 3600) # Seconds in an hour = 3600

    def minutes(seconds = None):
        if not seconds:
            return (0, 0)
        return divmod(seconds or duration_in_s, 60) # Seconds in a minute = 60

    def seconds(seconds = None):
        if interval == 'seconds':
            return (duration_in_s, 0)
        if seconds:
            return divmod(seconds, 1)
        return (0, 0)

    def totalDuration():
        y = years()
        d = days(y[1]) # Use remainder to calculate next variable
        h = hours(d[1])
        m = minutes(h[1])
        s = seconds(m[1])

        y_ = int(y[0])
        d_ = int(d[0])
        h_ = int(h[0])
        m_ = int(m[0])
        s_ = int(s[0])
        duration_string = f"{y_} years, {d_} days, {h_} hours, {m_} minutes and {s_} seconds"

        if duration_string.startswith('0 years'):
            duration_string = duration_string.replace('0 years, ', '')
            if duration_string.startswith('0 days'):
                duration_string = duration_string.replace('0 days, ', '')
        if duration_string == '0 hours, 0 minutes and 0 seconds':
            duration_string = 'Less than a second'
        return duration_string

    return {
        'minutes': int(minutes()[0]),
        'seconds': int(seconds()[0]),
        'default': totalDuration()
    }[interval]


class IevvLogging():

    def __init__(self, slug):
        self.slug = slug

    def _get_logging_base_from_slug(self):
        if IevvLoggingEventBase.objects.filter(slug=self.slug).exists():
            return IevvLoggingEventBase.objects.get(slug=self.slug)
        return IevvLoggingEventBase(slug=self.slug)

    def exception_as_dict(self, exception_instance):
        return {
            'repr': repr(exception_instance),
            'args': exception_instance.args,
        }

    def begin(self):
        self.loggingbase = self._get_logging_base_from_slug()
        start = timezone.now()
        self.loggingbase.last_started = start
        self.loggingbase.save()
        self.loggingitem = IevvLoggingEventItem(
            logging_base=self.loggingbase,
            start_datetime=start
        )
        self.loggingitem.save()

    def finish(self, error_occured=False, **kwargs):
        finish = timezone.now()
        duration_string = getDuration(self.loggingbase.last_started, finish)
        duration_seconds = getDuration(self.loggingbase.last_started, finish, 'seconds')
        # update the base model
        self.loggingbase.last_finished = finish
        self.loggingbase.time_spent = duration_string
        self.loggingbase.time_spent_in_seconds = duration_seconds
        self.loggingbase.success_run = not error_occured
        self.loggingbase.save()
        # update the item model
        self.loggingitem.time_spent = duration_string
        self.loggingitem.time_spent_in_seconds = duration_seconds
        self.loggingitem.data = kwargs
        self.loggingitem.end_datetime = finish
        self.loggingitem.success_run = not error_occured
        self.loggingitem.save()
