from datetime import date, datetime, time
from bson.codec_options import TypeEncoder

class DateEncoder(TypeEncoder):
  python_type = date

  def transform_python(self, value: date):
    return datetime.combine(value, time())