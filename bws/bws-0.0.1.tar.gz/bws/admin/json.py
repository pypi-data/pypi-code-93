import datetime
import decimal
from flask import json


class JSONEncoderCurstom(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)

        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()

        try:
            return super().default(o)
        except:
            return str(o)
