from datetime import datetime
from json import JSONDecoder, JSONEncoder


class DateTimeEncoderDecoder(JSONDecoder, JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
