import pytz


class DeploymentQueryBuilderMixin(object):
    @staticmethod
    def _build_query_params(start_time=None, end_time=None, **kwargs):
        def timezone_aware(dt):
            return dt.replace(tzinfo=pytz.utc) if not dt.tzinfo else dt

        if start_time:
            kwargs["start"] = timezone_aware(start_time).isoformat()
        if end_time:
            kwargs["end"] = timezone_aware(end_time).isoformat()
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        return kwargs
