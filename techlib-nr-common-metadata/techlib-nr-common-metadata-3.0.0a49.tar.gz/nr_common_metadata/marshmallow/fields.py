import re

import arrow
import idutils
import isbnlib
from arrow import ParserError, Arrow
from marshmallow import fields, ValidationError
from stdnum import issn
from stdnum.exceptions import InvalidChecksum, InvalidLength, InvalidFormat, InvalidComponent


class NRDate(fields.Field):
    """Field that parse date and date range.
    """

    def _deserialize(self, value, attr, data, **kwargs):
        return serialize_date(value)


class DateRange(fields.Field):
    """Field that parse date and date range.
    """

    def _deserialize(self, value, attr, data, **kwargs):
        date_str = value.replace(" ", "")
        date_arr = date_str.split("/")
        try:
            val_date_arr = [self.validate_min_max(arrow.get(date, "YYYY-MM-DD")) for date in
                            date_arr]
        except ValueError as e:
            raise ValidationError(str(e))
        l: int = len(val_date_arr)
        if l > 2:
            raise ValidationError("Date period cannot contain more then two dates")
        if l == 2:
            return f"{val_date_arr[0].format('YYYY-MM-DD')}/{val_date_arr[1].format('YYYY-MM-DD')}"
        if l == 1:
            return val_date_arr[0].format('YYYY-MM-DD')
        else:
            raise ValidationError("Unexpected time period format")

    @staticmethod
    def validate_min_max(date: Arrow):
        if date > arrow.get() or date < arrow.get("1700-01-01"):
            raise ValidationError("The date is in the future or before 1700.")
        return date


class DateString(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            value = str(value).strip()
            a = arrow.get(value, "YYYY-MM-DD")
            if a < arrow.get("1700-01-01"):
                raise ValidationError(
                    "Date is lower then 1700")
            if a > arrow.get():
                raise ValidationError("Cannot use year higher than current year")
            return a.format("YYYY-MM-DD")
        except ParserError:
            raise ValidationError("Wrong date format")


class Year(fields.Field):

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            value = str(value).strip()
            a = arrow.get(value)
            if a < arrow.get("1700"):
                raise ValidationError(
                    "Date is lower then 1700")
            if a > arrow.get():
                raise ValidationError("Cannot use year higher than current year")
            return a.format("YYYY")
        except ParserError:
            raise ValidationError("Wrong date format")


class ISBN(fields.Field):

    def _deserialize(self, value, attr, data, **kwargs):
        return self.extract_isbn(value)

    @staticmethod
    def extract_isbn(value):
        try:
            isbns = isbnlib.get_isbnlike(value)
            isbn = isbns[0]
        except:
            raise ValidationError(f"Bad format {value}")
        if len(isbns) > 1:
            raise ValidationError("Too much ISBN numbers")
        elif (len(isbns) == 0) or (not isbnlib.is_isbn10(isbn) and not isbnlib.to_isbn13(isbn)):
            raise ValidationError("It is not ISBN number")
        elif len(isbns) == 1:
            return isbnlib.mask(isbn)
        else:
            raise ValidationError("Unexpected option")


class ISSN(fields.Field):

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            issn.validate(value)
            return issn.format(value)
        except (InvalidChecksum, InvalidLength, InvalidFormat, InvalidComponent) as e:
            raise ValidationError(str(e))
        except:
            raise ValidationError(f"Bad format {value}")


class DOI(fields.Field):

    def _deserialize(self, value, attr, data, **kwargs):
        doi = idutils.is_doi(value)
        if not doi:
            raise ValidationError(f"It is not valid doi: \"{value}\"")
        return doi.string


class RIV(fields.Field):

    def _deserialize(self, value, attr, data, **kwargs):
        pattern = r"RIV/\w{8}:\w{5}/\d{2}:\d{8}$"
        match = re.match(pattern, value.strip())
        if not match:
            raise ValidationError(f"It is not valid RIV id: \"{value.strip()}\"")
        return match.string


def extract_date(value):
    try:
        obj = re.search(r"(\d{4})[/.-]+(\d{4})", value)
    except TypeError as e:
        raise ValidationError(str(e))
    if obj:
        groups = obj.groups()
        return [(groups[0],), (groups[1],)]
    pattern = r"(\d{4})[/.-]?(\d{2})?[/.-]?(\d{2})?"
    dates = re.findall(pattern, value)
    if dates:
        return dates
    return


def serialize_date(value):
    dates = extract_date(value)
    dates = _serialize_dates(dates)
    if len(dates) > 2:
        raise ValidationError("Too much dates. Only two dates are allowed for date range")
    elif len(dates) == 2:
        return " / ".join(dates)
    elif len(dates) == 1:
        return dates[0]
    else:
        raise ValidationError(f"Unsupported date format or missing date in value: \"{value}\"")


def _serialize_dates(dates):
    result = []
    if not dates:
        raise ValidationError("Wrong date format")
    for date in dates:
        new_date = [stage.strip() for stage in date if len(stage) > 0]
        l = len(new_date)
        date_str = "-".join(new_date)
        try:
            a = arrow.get(date_str)
        except ValueError as e:
            raise ValidationError(str(e))
        if a > arrow.get():
            raise ValidationError("Can't select a future date")
        if l == 3:
            result.append(a.format("YYYY-MM-DD"))
        elif l == 2:
            result.append(a.format("YYYY-MM"))
        elif l == 1:
            result.append(a.format("YYYY"))
        else:
            raise ValidationError("Wrong date format")
    return result


class OAI(fields.Field):

    def _deserialize(self, value, attr, data, **kwargs):
        pattern = r"oai:[a-zA-Z][a-zA-Z0-9\-]*(\.[a-zA-Z][a-zA-Z0-9\-]*)+:[a-zA-Z0-9\-_\.!~\*'\(" \
                  r"\);/\?:@&=\+$,%]+"
        match = re.match(pattern, value.strip())
        if not match:
            raise ValidationError(f"It is not valid oai identifier \"{value}\"")
        return match.string
