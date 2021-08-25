from ...manifest.namings import alias_df
from enum import Enum, IntEnum
from .routing import routing_df
from ...fold import ns_path

__all__ = ["AddressPath"]

class AddressPart(str):
    def __new__(cls, *args, **kw):
        return super().__new__(cls, *args, **kw)


class NameSpaceString(AddressPart):
    pass


class DomainString(AddressPart):
    pass


class DomainAliasString(AddressPart):
    pass


class DigitStringPart(AddressPart):
    @property
    def int(self):
        return self._int

    @int.setter
    def int(self, i):
        assert isinstance(i, int), f"Not an integer: '{type(i)}'"
        self._int = i


class YyDigitString(DigitStringPart):
    def __init__(self, y):
        assert len(y) == 2, f"Expected a 2-digit string, got '{y}'"
        self.int = int(y)  # expect e.g. "20" to indicate the year 2020

    @property
    def year(self):
        return 2000 + self.int


class MonthInt(IntEnum):
    jan = 1
    feb = 2
    mar = 3
    apr = 4
    may = 5
    jun = 6
    jul = 7
    aug = 8
    sep = 9
    oct = 10
    nov = 11
    dec = 12


class MonthUtilMixin:
    @staticmethod
    def month_int_to_enum(month_int):
        return MonthInt._value2member_map_.get(month_int)

    @staticmethod
    def month_str_to_enum(month_str):
        return MonthInt._member_map_.get(month_str)

    @staticmethod
    def validate_month_int(month_int):
        assert 1 <= month_int <= 12, f"Expected integer from 1-12, got '{month_int}'"
        return


class MmDigitString(DigitStringPart, MonthUtilMixin):
    def __init__(self, m):
        mi = int(m)
        self.validate_month_int(mi)
        self.int = mi  # expect e.g. "10" to indicate the month November

    @property
    def as_enum(self):
        return self.month_int_to_enum(self.int)

    @property
    def as_str(self):
        return self.as_enum.name


class mmmString(AddressPart, MonthUtilMixin):
    def __init__(self, m):
        mi = self.month_str_to_enum(m).value
        assert 1 <= mi <= 12, f"Expected an integer from 1 to 12, got '{mi}'"
        self.int = mi  # expect e.g. "10" to indicate the month November

    @property
    def as_enum(self):
        return self.month_int_to_str(self.int)

    @property
    def as_str(self):
        return self


class DdDigitString(DigitStringPart):
    def __init__(self, d):
        di = int(d)
        self.validate_day_int(di)  # weakly validate (presume calendar obeyed)
        self.int = di  # expect e.g. "1" to indicate the 1st day of the month

    @staticmethod
    def validate_day_int(day_int):
        assert 1 <= day_int <= 31, f"Expected day number from 1-31, got {day_int}"


# TODO: alternative DdDigitString class, for {01,02,03} rather than {1,2,3}


class FileIntString(DigitStringPart):
    def __init__(self, f):
        self.int = int(f)


class AddressParts(Enum):
    NameSpace = NameSpaceString
    Domain = DomainString
    DomainAlias = DomainAliasString
    YY = YyDigitString
    MM = MmDigitString
    mmm = mmmString
    DD = DdDigitString
    FileInt = FileIntString


def pop_part(part_list):
    try:
        return part_list.pop(0)
    except IndexError as e:
        return e


def interpret_filepath(address_path=None):
    if address_path is None:
        address_path = example_path
    elif type(address_path) is str:
        address_path = AddressPath(address_path)
    namespace = address_path.namespace
    domain = address_path.domain
    route_query = f"namespace == '{namespace}' and domain == '{domain}'"
    #route_result = routing_df.query(route_query)
    custom_route = routing_df.query(route_query).route.item()
    route = custom_route if custom_route else domain
    domain_filepath = (ns_path / route).resolve()
    has_y, has_m, has_d, has_f = [
        hasattr(address_path, attrib) for attrib in "year month day fileint".split()
    ]
    # Delayed to avoid circular import
    from ...fold.wire import standup
    standup_config = standup(domains_list=[domain], dry_config=True, verbose=False)
    if domain in standup_config:
        # The domain is being served, so get the directory from which it is served
        domain_filepath = standup_config.get(domain).get("directory")
    if has_y:
        yeardir = domain_filepath / address_path.year
        if has_m:
            month_str = f"{address_path.month.int:02d}{address_path.month.as_str}"
            monthdir = yeardir / month_str
            if has_d:
                daydir = monthdir / address_path.day
                if has_f:
                    if daydir.is_dir():
                        # Will raise StopIteration exception if glob comes back empty
                        p = next(daydir.glob(f"{address_path.fileint}*"))
                    else:
                        raise FileNotFoundError(f"Expected a directory at {daydir}")
                else:
                    p = daydir
            else:
                p = monthdir
        else:
            p = yeardir
    else:
        p = domain_filepath
    return p


class AddressPath(list):
    def __init__(self, address_str, sep="⠶"):
        self.sep = sep
        self.parts = SeparatedString(address_str, sep=sep)
    
    @property
    def as_str(self, sep=None):
        if sep is None:
            sep = self.sep
        return sep.join(self)

    @property
    def filepath(self):
        return interpret_filepath(self.as_str)

    @property
    def parts(self):
        return self._parts

    @parts.setter
    def parts(self, p):
        """
        Setting a list of `parts` triggers parsing those part strings into the typed
        `AddressParts` and appending them as the main `AddressPath` list items. The
        parts are stored but not appended to the path until validated.
        """
        self._parts = p
        self._parse()

    def _parse(self, strict=True):
        """
        If parsing strictly, expect either:
          - ∫⠶log
          - ∫⠶log⠶20⠶10⠶25
          - ∫⠶log⠶20⠶10⠶25⠶0
        Else if not `strict`, just parse as much as possible after the first part.
        """
        pp = self.parts.copy()  # copy so popping can indicate if reached final part
        if strict:
            assert len(pp) in (2, 5, 6), f"Bad address length: {len(pp)}"
        ns = pp.pop(0)  # Permit IndexError here if parts is an empty list
        assert ns in alias_df.namespace.cat.categories, f"Bad namespace: '{ns}'"
        self.namespace = AddressParts.NameSpace.value(ns)
        self.append(self.namespace)  # append typed string to path
        ns_query = f"namespace == '{self.namespace}'"
        if isinstance(d := pop_part(pp), IndexError):
            if strict:
                raise d  # we strictly want a domain in the address
            else:
                return  # reached end of the parts list so finish parsing without error
        elif d in (ns_df := alias_df.query(ns_query)).alias.to_list():
            alias = AddressParts.DomainAlias.value(d)
            # note the following will raise ValueError if multiple dealiased values
            [dealiased] = ns_df[ns_df.alias == d].domain.to_list()
            domain = AddressParts.Domain.value(dealiased)
            self.domain, self.domain_alias = dealiased, alias
            self.append(self.domain_alias)
        elif d in ns_df.domain.to_list():
            domain = AddressParts.Domain.value(d)
            # if an alias exists but isn't being used, just ignore it here (as `None`)
            self.domain, self.domain_alias = domain, None
            self.append(self.domain)
        else:
            raise ValueError("Couldn't parse address {namespace}⠶{domain|alias}")
        if isinstance(y := pop_part(pp), IndexError):
            # 2 is a permitted number of address parts, so no need to check `strict`
            return
        else:
            self.year = AddressParts.YY.value(y)
            self.append(self.year)
        if isinstance(month := pop_part(pp), IndexError):
            if strict:
                raise month  # we strictly want a full date if we saw a year
            else:
                return  # reached end of the parts list so finish parsing without error
        else:
            if month.isnumeric():
                self.month = AddressParts.MM.value(month)
            else:
                self.month = AddressParts.mmm.value(month)
            self.append(self.month)
        if isinstance(day := pop_part(pp), IndexError):
            if strict:
                raise day  # we strictly want a full date if we saw a year and month
            else:
                return  # reached end of the parts list so finish parsing without error
        else:
            self.day = AddressParts.DD.value(day)
            self.append(self.day)
        if isinstance(f := pop_part(pp), IndexError):
            # 5 is a permitted number of address parts, so no need to check `strict`
            return
        else:
            self.fileint = AddressParts.FileInt.value(f)
            self.append(self.fileint)
        if strict:
            assert len(pp) == 0, f"Strict parsing enabled but extra parts in path: {pp}"
        else:
            self.extend(pp)  # just... add extra to path untyped? ¯\_(ツ)_/¯
        return

    @classmethod
    def from_parts(cls, domain, ymd=None, n=None, sep="⠶"):
        ns = alias_df[alias_df.domain.eq(domain)].namespace.item()
        path_parts = [ns, domain]
        if ymd:
            y, m, d = map(str, ymd)
            y = y[-2:]
            m = m.zfill(2)
            d = d.zfill(2)
            path_parts.extend([y, m, d])
        if n:
            path_parts.append(str(n))
        return cls(sep.join(path_parts))

class SeparatedString(list):
    def __init__(self, sep_str, sep):
        self.extend(sep_str.split(sep))
