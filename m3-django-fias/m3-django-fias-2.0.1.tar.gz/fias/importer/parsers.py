import datetime


def make_datetime_parser(extractor, formats):
    def parse(value):
        for (fmt, length) in formats:
            try:
                result = extractor(
                    datetime.datetime.strptime(value[:length], fmt)
                )
                break
            except ValueError:
                pass
        else:
            raise AssertionError()
        return result
    return parse


datetime_parser = make_datetime_parser(lambda x: x, formats=(
    ('%d.%m.%y %H:%M:%S', 19),
    ('%d.%m.%Y %H:%M:%S', 19),
    ('%Y-%m-%dT%H:%M:%S', 19),
    ('%Y-%m-%d %H:%M:%S', 19),
    ('%Y-%m-%dT%H:%M', 16),
    ('%Y-%m-%d %H:%M', 16),
    ('%d.%m.%Y %H:%M', 16),
    ('%Y-%m-%d', 10),
    ('%d.%m.%Y', 10),
    ('%H:%M:%S', 8),
    ('%H:%M', 5),
))