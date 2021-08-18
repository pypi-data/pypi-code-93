'''
# [kollavarsham](http://kollavarsham.org/)

[![Circle CI Status](https://img.shields.io/circleci/build/github/kollavarsham/kollavarsham-js?label=CircleCI)](https://app.circleci.com/pipelines/github/kollavarsham/kollavarsham-js) [![Travis CI Status](https://img.shields.io/travis/kollavarsham/kollavarsham-js.svg?label=TravisCI)](https://travis-ci.org/kollavarsham/kollavarsham-js) [![Coverage Status](https://img.shields.io/coveralls/github/kollavarsham/kollavarsham-js?label=Coveralls)](https://coveralls.io/github/kollavarsham/kollavarsham-js?branch=main) [![Dependency Status](https://img.shields.io/david/kollavarsham/kollavarsham-js)](https://david-dm.org/kollavarsham/kollavarsham-js) [![Dev-Dependency Status](https://img.shields.io/david/dev/kollavarsham/kollavarsham-js)](https://david-dm.org/kollavarsham/kollavarsham-js?type=dev)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fkollavarsham%2Fkollavarsham-js.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fkollavarsham%2Fkollavarsham-js?ref=badge_shield)

> Convert Gregorian date to Kollavarsham date and vice versa

## Install

### TypeScript/JavaScript/Node.js [![NPM version](https://img.shields.io/npm/v/kollavarsham)](https://www.npmjs.com/package/kollavarsham)

```sh
$ npm install kollavarsham
```

### Python [![PyPI version](https://img.shields.io/pypi/v/kollavarsham)](https://pypi.org/project/kollavarsham/)

```sh
$ pip install kollavarsham
```

### Java [![Maven version](https://img.shields.io/maven-central/v/org.kollavarsham.converter/kollavarsham-converter)](https://search.maven.org/artifact/org.kollavarsham.converter/kollavarsham-converter)

```xml
<dependency>
  <groupId>org.kollavarsham.converter</groupId>
  <artifactId>kollavarsham-converter</artifactId>
  <version>2.0.1</version>
</dependency>
```

### C#/dotnet [![NuGet version](https://img.shields.io/nuget/v/KollavarshamOrg.Converter)](https://www.nuget.org/packages/KollavarshamOrg.Converter)

```sh
$ dotnet add package KollavarshamOrg.Converter
```

## Usage

### TypeScript/JavaScript/Node.js

```js
import { Kollavarsham } from 'kollavarsham';

const options = {
  system: 'SuryaSiddhanta',
  latitude: 10,
  longitude: 76.2
};

const kollavarsham = new Kollavarsham(options);

const today = kollavarsham.fromGregorianDate(new Date());

console.log(today.year, today.mlMasaName, today.date, `(${today.mlNaksatraName})`);
```

### Python

```python
import datetime
import pytz
import kollavarsham

now = pytz.utc.localize(datetime.datetime.utcnow())
kv = kollavarsham.Kollavarsham(latitude=10, longitude=76.2, system="SuryaSiddhanta")

today = kv.from_gregorian_date(date=now)
print(today.year, today.ml_masa_name, today.date, '(' + today.naksatra.ml_malayalam + ')')
```

### Java

```java
package org.kollavarsham.tester;

import java.time.Instant;

import org.kollavarsham.converter.Kollavarsham;
import org.kollavarsham.converter.KollavarshamDate;
import org.kollavarsham.converter.Settings;
import org.kollavarsham.converter.Settings.Builder;

public class App {
    public static void main( final String[] args) {
        final Settings settings = new Builder().latitude(10).longitude(76.2).system("SuryaSiddhanta").build();
        final Kollavarsham kv = new Kollavarsham(settings);
        final KollavarshamDate today = kv.fromGregorianDate(Instant.now());
        System.out.println( today.getYear() + today.getMlMasaName() + today.getDate() + '(' + today.getMlNaksatraName() + ')' );
    }
}
```

### C#/dotnet

```csharp
using System;

namespace KollavarshamOrg.Tester
{
    class Program
    {
        static void Main(string[] args)
        {
            var settings = new Settings {
                Latitude = 10,
                Longitude = 76.2,
                System = "SuryaSiddhanta"
            };
            var kv = new Kollavarsham(settings);
            var today = kv.FromGregorianDate(DateTime.Now);
            Console.WriteLine($"{today.Year.ToString()} {today.MlMasaName} {today.Date.ToString()} ({today.MlNaksatraName})");
        }
    }
}
```

## Documentation

### TypeScript/JavaScript/Node.js

Check out the [Kollavarsham class](https://kollavarsham.org/kollavarsham-js/module-kollavarsham.Kollavarsham.html) within the API documentation as this is the entry point into the library.

## Release History

Check out the history at [GitHub Releases](https://github.com/kollavarsham/kollavarsham-js/releases)

## License

Copyright (c) 2014-2021 The Kollavarsham Team. Licensed under the [MIT license](http://kollavarsham.org/LICENSE.txt).

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fkollavarsham%2Fkollavarsham-js.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fkollavarsham%2Fkollavarsham-js?ref=badge_large)
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *


class BaseDate(metaclass=jsii.JSIIAbstractClass, jsii_type="kollavarsham.BaseDate"):
    '''Serves as the base class for both the {@link JulianDate} and {@link KollavarshamDate} classes.

    **INTERNAL/PRIVATE**

    :class: BaseDate
    :constructor: true
    '''

    def __init__(
        self,
        year: typing.Optional[jsii.Number] = None,
        month: typing.Optional[jsii.Number] = None,
        date: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param year: -
        :param month: -
        :param date: -
        '''
        jsii.create(BaseDate, self, [year, month, date])

    @jsii.member(jsii_name="getMasaName") # type: ignore[misc]
    @builtins.classmethod
    def get_masa_name(cls, masa_number: jsii.Number) -> "MasaName":
        '''Returns the month names object that has Saka, Saura and Kollavarsham (English & Malayalam) month names for the specified index ``masaNumber``.

        :param masa_number: -

        :for: BaseDate
        :method: getMasaName
        '''
        return typing.cast("MasaName", jsii.sinvoke(cls, "getMasaName", [masa_number]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''Converts the Date to a nicely formatted string with year, month and date.

        :for: BaseDate
        :method: toString
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mlWeekdayName")
    def ml_weekday_name(self) -> builtins.str:
        '''Returns the weekday (in Malayalam) for the current instance of date.

        :property: mlWeekdayName
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "mlWeekdayName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sauraMasaName")
    def saura_masa_name(self) -> builtins.str:
        '''Returns the Saura Masa name for the current instance of date.

        :property: sauraMasaName
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "sauraMasaName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weekdayName")
    def weekday_name(self) -> builtins.str:
        '''Returns the weekday (in English) for the current instance of date.

        :property: weekdayName
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "weekdayName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ahargana")
    def ahargana(self) -> jsii.Number:
        '''The ``Ahargana`` corresponding to this instance of the date. **Set separately after an instance is created**.

        In Sanskrit ``ahoratra`` means one full day and ``gana`` means count.
        Hence, the Ahargana on any given day stands for the number of lunar days that have elapsed starting from an epoch.

        *Source*: http://cs.annauniv.edu/insight/Reading%20Materials/astro/sharptime/ahargana.htm

        :property: ahargana
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "ahargana"))

    @ahargana.setter
    def ahargana(self, value: jsii.Number) -> None:
        jsii.set(self, "ahargana", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="date")
    def date(self) -> jsii.Number:
        '''The date corresponding to this instance of the date.

        :property: date
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "date"))

    @date.setter
    def date(self, value: jsii.Number) -> None:
        jsii.set(self, "date", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gregorianDate")
    def gregorian_date(self) -> datetime.datetime:
        '''The gregorian date corresponding to this instance of the date.

        **Set separately after an instance is created**

        :property: gregorianDate
        :type: {Date}
        '''
        return typing.cast(datetime.datetime, jsii.get(self, "gregorianDate"))

    @gregorian_date.setter
    def gregorian_date(self, value: datetime.datetime) -> None:
        jsii.set(self, "gregorianDate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="julianDay")
    def julian_day(self) -> jsii.Number:
        '''The ``Julian Day`` corresponding to this instance of the date.

        **Set separately after an instance is created**
        Julian day is the continuous count of days since the beginning of the Julian Period used primarily by astronomers.

        *Source*: https://en.wikipedia.org/wiki/Julian_day

        :property: julianDay
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "julianDay"))

    @julian_day.setter
    def julian_day(self, value: jsii.Number) -> None:
        jsii.set(self, "julianDay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="month")
    def month(self) -> jsii.Number:
        '''The month corresponding to this instance of the date.

        :property: month
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "month"))

    @month.setter
    def month(self, value: jsii.Number) -> None:
        jsii.set(self, "month", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="naksatra")
    def naksatra(self) -> "Naksatra":
        return typing.cast("Naksatra", jsii.get(self, "naksatra"))

    @naksatra.setter
    def naksatra(self, value: "Naksatra") -> None:
        jsii.set(self, "naksatra", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sauraDivasa")
    def saura_divasa(self) -> jsii.Number:
        '''The ``Saura Divasa`` (Solar Calendar Day) for this instance of the date.

        **Set separately after an instance is created**

        :property: sauraDivasa
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "sauraDivasa"))

    @saura_divasa.setter
    def saura_divasa(self, value: jsii.Number) -> None:
        jsii.set(self, "sauraDivasa", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sauraMasa")
    def saura_masa(self) -> jsii.Number:
        '''The ``Saura Masa`` (Solar Calendar Month) for this instance of the date.

        **Set separately after an instance is created**

        :property: sauraMasa
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "sauraMasa"))

    @saura_masa.setter
    def saura_masa(self, value: jsii.Number) -> None:
        jsii.set(self, "sauraMasa", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="year")
    def year(self) -> jsii.Number:
        '''The year corresponding to this instance of the date.

        :property: year
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "year"))

    @year.setter
    def year(self, value: jsii.Number) -> None:
        jsii.set(self, "year", value)


class _BaseDateProxy(BaseDate):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseDate).__jsii_proxy_class__ = lambda : _BaseDateProxy


class JulianDate(
    BaseDate,
    metaclass=jsii.JSIIMeta,
    jsii_type="kollavarsham.JulianDate",
):
    '''Represents a Julian date's year, month and day ``toGregorianDateFromSaka`` method of the {@link Kollavarsham} class returns an instance of this type for dates older than ``1st January 1583 AD``.

    **INTERNAL/PRIVATE**

    :class: JulianDate
    :constructor: true
    :extends: BaseDate
    '''

    def __init__(
        self,
        year: typing.Optional[jsii.Number] = None,
        month: typing.Optional[jsii.Number] = None,
        day: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param year: -
        :param month: -
        :param day: -
        '''
        jsii.create(JulianDate, self, [year, month, day])


class Kollavarsham(metaclass=jsii.JSIIMeta, jsii_type="kollavarsham.Kollavarsham"):
    '''The Kollavarsham class implements all the public APIs of the library.

    Create a new instance of this class, passing in the relevant options and call methods on the instance.

    :class: Kollavarsham
    :constructor: true

    Example::

        # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
        Kollavarsham = require("kollavarsham")
        
        options = {
            "system": "SuryaSiddhanta",
            "latitude": 10,
            "longitude": 76.2
        }
        
        kollavarsham = Kollavarsham(options)
        
        today_in_malayalam_era = kollavarsham.from_gregorian_date(Date())
        
        today = kollavarsham.to_gregorian_date(today_in_malayalam_era)
    '''

    def __init__(
        self,
        *,
        latitude: jsii.Number,
        longitude: jsii.Number,
        system: builtins.str,
    ) -> None:
        '''
        :param latitude: 
        :param longitude: 
        :param system: 
        '''
        options = Settings(latitude=latitude, longitude=longitude, system=system)

        jsii.create(Kollavarsham, self, [options])

    @jsii.member(jsii_name="fromGregorianDate")
    def from_gregorian_date(self, date: datetime.datetime) -> "KollavarshamDate":
        '''Converts a Gregorian date to the equivalent Kollavarsham date, respecting the current configuration.

        :param date: The Gregorian date to be converted to Kollavarsham.

        :return: Converted date

        :for: Kollavarsham
        :method: fromGregorianDate

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            Kollavarsham = require("Kollavarsham")
            kollavarsham = Kollavarsham()
            today = kollavarsham.from_gregorian_date(Date(1979, 4, 22))
        '''
        return typing.cast("KollavarshamDate", jsii.invoke(self, "fromGregorianDate", [date]))

    @jsii.member(jsii_name="toGregorianDate")
    def to_gregorian_date(self, date: "KollavarshamDate") -> datetime.datetime:
        '''Converts a Kollavarsham date (an instance of {@link kollavarshamDate}) to its equivalent Gregorian date, respecting the current configuration.

        This method Will return {@link JulianDate} object for any date before 1st January 1583 AD and
        `Date <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date>`_ objects for later dates.

        **This API has not been implemented yet**

        :param date: The Kollavarsham date to be converted to Gregorian.

        :return: Converted date

        :for: Kollavarsham
        :method: toGregorianDate
        :throws: **"When the API is implemented, will convert <date>"**
        '''
        return typing.cast(datetime.datetime, jsii.invoke(self, "toGregorianDate", [date]))

    @jsii.member(jsii_name="toGregorianDateFromSaka")
    def to_gregorian_date_from_saka(self, saka_date: "SakaDate") -> "KollavarshamDate":
        '''Converts a Saka date (an instance of {@link sakaDate}) to its equivalent Gregorian date, respecting the current configuration.

        This method Will return {@link JulianDate} object for any date before 1st January 1583 AD and
        `Date <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date>`_ objects for later dates.

        :param saka_date: The Saka date to be converted to Gregorian.

        :return: Converted date

        :for: Kollavarsham
        :method: toGregorianDateFromSaka
        '''
        return typing.cast("KollavarshamDate", jsii.invoke(self, "toGregorianDateFromSaka", [saka_date]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="settings")
    def settings(self) -> "Settings":
        return typing.cast("Settings", jsii.get(self, "settings"))

    @settings.setter
    def settings(self, value: "Settings") -> None:
        jsii.set(self, "settings", value)


class KollavarshamDate(
    BaseDate,
    metaclass=jsii.JSIIMeta,
    jsii_type="kollavarsham.KollavarshamDate",
):
    '''Represents a Kollavarsham date's year, month and date.

    :class: KollavarshamDate
    :constructor: true
    :extends: BaseDate
    '''

    def __init__(
        self,
        year: typing.Optional[jsii.Number] = None,
        month: typing.Optional[jsii.Number] = None,
        day: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param year: -
        :param month: -
        :param day: -
        '''
        jsii.create(KollavarshamDate, self, [year, month, day])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masaName")
    def masa_name(self) -> builtins.str:
        '''Returns the Kollavarsham month name (in English) for this instance of date.

        :property: masaName
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "masaName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mlMasaName")
    def ml_masa_name(self) -> builtins.str:
        '''Returns the Kollavarsham month name (in Malayalam) for this instance of date.

        :property: mlMasaName
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "mlMasaName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mlNaksatraName")
    def ml_naksatra_name(self) -> builtins.str:
        '''Returns the Kollavarsham Naksatra name (in Malayalam) for this instance of date.

        :property: mlNaksatraName
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "mlNaksatraName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="naksatraName")
    def naksatra_name(self) -> builtins.str:
        '''Returns the Kollavarsham Naksatra name (in English) for this instance date.

        :property: naksatraName
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "naksatraName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sakaDate")
    def saka_date(self) -> "SakaDate":
        return typing.cast("SakaDate", jsii.get(self, "sakaDate"))

    @saka_date.setter
    def saka_date(self, value: "SakaDate") -> None:
        jsii.set(self, "sakaDate", value)


@jsii.data_type(
    jsii_type="kollavarsham.MasaName",
    jsii_struct_bases=[],
    name_mapping={
        "en_malayalam": "enMalayalam",
        "ml_malayalam": "mlMalayalam",
        "saka": "saka",
        "saura": "saura",
    },
)
class MasaName:
    def __init__(
        self,
        *,
        en_malayalam: builtins.str,
        ml_malayalam: builtins.str,
        saka: builtins.str,
        saura: builtins.str,
    ) -> None:
        '''
        :param en_malayalam: 
        :param ml_malayalam: 
        :param saka: 
        :param saura: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "en_malayalam": en_malayalam,
            "ml_malayalam": ml_malayalam,
            "saka": saka,
            "saura": saura,
        }

    @builtins.property
    def en_malayalam(self) -> builtins.str:
        result = self._values.get("en_malayalam")
        assert result is not None, "Required property 'en_malayalam' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ml_malayalam(self) -> builtins.str:
        result = self._values.get("ml_malayalam")
        assert result is not None, "Required property 'ml_malayalam' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def saka(self) -> builtins.str:
        result = self._values.get("saka")
        assert result is not None, "Required property 'saka' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def saura(self) -> builtins.str:
        result = self._values.get("saura")
        assert result is not None, "Required property 'saura' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MasaName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="kollavarsham.Naksatra",
    jsii_struct_bases=[],
    name_mapping={
        "en_malayalam": "enMalayalam",
        "ml_malayalam": "mlMalayalam",
        "saka": "saka",
    },
)
class Naksatra:
    def __init__(
        self,
        *,
        en_malayalam: builtins.str,
        ml_malayalam: builtins.str,
        saka: builtins.str,
    ) -> None:
        '''
        :param en_malayalam: 
        :param ml_malayalam: 
        :param saka: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "en_malayalam": en_malayalam,
            "ml_malayalam": ml_malayalam,
            "saka": saka,
        }

    @builtins.property
    def en_malayalam(self) -> builtins.str:
        result = self._values.get("en_malayalam")
        assert result is not None, "Required property 'en_malayalam' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ml_malayalam(self) -> builtins.str:
        result = self._values.get("ml_malayalam")
        assert result is not None, "Required property 'ml_malayalam' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def saka(self) -> builtins.str:
        result = self._values.get("saka")
        assert result is not None, "Required property 'saka' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Naksatra(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SakaDate(BaseDate, metaclass=jsii.JSIIMeta, jsii_type="kollavarsham.SakaDate"):
    '''Represents an Saka date's year, month and paksa and tithi.

    :class: SakaDate
    :constructor: true
    :extends: BaseDate
    '''

    def __init__(
        self,
        year: typing.Optional[jsii.Number] = None,
        month: typing.Optional[jsii.Number] = None,
        tithi: typing.Optional[jsii.Number] = None,
        paksa: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param year: -
        :param month: -
        :param tithi: -
        :param paksa: -
        '''
        jsii.create(SakaDate, self, [year, month, tithi, paksa])

    @jsii.member(jsii_name="generateKollavarshamDate")
    def generate_kollavarsham_date(self) -> KollavarshamDate:
        '''Generates an instance of {@link KollavarshamDate} from this instance of SakaDate.

        :for: SakaDate
        :method: generateKollavarshamDate
        '''
        return typing.cast(KollavarshamDate, jsii.invoke(self, "generateKollavarshamDate", []))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''Converts the Date to a nicely formatted string with year, month and date.'''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masaName")
    def masa_name(self) -> builtins.str:
        '''Returns the month name for this instance of SakaDate.

        :property: masaName
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "masaName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="naksatraName")
    def naksatra_name(self) -> builtins.str:
        '''Returns the Saka Naksatra name for this instance of SakaDate.

        :property: naksatraName
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "naksatraName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sakaYear")
    def saka_year(self) -> jsii.Number:
        '''Returns the Saka year on this instance of SakaDate (same as the underlyiung ``year`` property from the {@link BaseDate} class).

        :property: sakaYear
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "sakaYear"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tithi")
    def tithi(self) -> jsii.Number:
        '''Returns the Tithi on this instance of SakaDate (same as the underlyiung ``date`` property from the {@link BaseDate} class).

        In Vedic timekeeping, a tithi (also spelled thithi) is a lunar day, or the time it takes for the longitudinal angle between the Moon and the Sun to increase by 12°.
        Tithis begin at varying times of day and vary in duration from approximately 19 to approximately 26 hours.

        *Source*: https://en.wikipedia.org/wiki/Tithi

        :property: tithi
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "tithi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vikramaYear")
    def vikrama_year(self) -> jsii.Number:
        '''Returns the Vikrama year corresponding to the Saka year of this instance.

        :property: vikramaYear
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "vikramaYear"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adhimasa")
    def adhimasa(self) -> builtins.str:
        '''The Adhimasa (``Adhika Masa``) prefix corresponding to this instance of the date.

        **Set separately after an instance is created**

        :property: adhimasa
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "adhimasa"))

    @adhimasa.setter
    def adhimasa(self, value: builtins.str) -> None:
        jsii.set(self, "adhimasa", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fractionalTithi")
    def fractional_tithi(self) -> jsii.Number:
        '''The fractional ``Tithi``corresponding to this instance of the date.

        **Set separately after an instance is created**

        :property: fractionalTithi
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "fractionalTithi"))

    @fractional_tithi.setter
    def fractional_tithi(self, value: jsii.Number) -> None:
        jsii.set(self, "fractionalTithi", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kaliYear")
    def kali_year(self) -> jsii.Number:
        '''The Kali year corresponding to this instance of the date.

        **Set separately after an instance is created**

        :property: kaliYear
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "kaliYear"))

    @kali_year.setter
    def kali_year(self, value: jsii.Number) -> None:
        jsii.set(self, "kaliYear", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originalAhargana")
    def original_ahargana(self) -> jsii.Number:
        '''The original ahargana passed in to the celestial calculations (TODO: Not sure why we need this!?).'''
        return typing.cast(jsii.Number, jsii.get(self, "originalAhargana"))

    @original_ahargana.setter
    def original_ahargana(self, value: jsii.Number) -> None:
        jsii.set(self, "originalAhargana", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="paksa")
    def paksa(self) -> builtins.str:
        '''The Paksha/Paksa corresponding to this instance of the date.

        Paksha (or pakṣa: Sanskrit: पक्ष), refers to a fortnight or a lunar phase in a month of the Hindu lunar calendar.

        *Source*: https://en.wikipedia.org/wiki/Paksha

        :property: paksa
        :type: {string}
        '''
        return typing.cast(builtins.str, jsii.get(self, "paksa"))

    @paksa.setter
    def paksa(self, value: builtins.str) -> None:
        jsii.set(self, "paksa", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sunriseHour")
    def sunrise_hour(self) -> jsii.Number:
        '''The hour part from the sunrise time for this date.

        **Set separately after an instance is created**

        :property: sunriseHour
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "sunriseHour"))

    @sunrise_hour.setter
    def sunrise_hour(self, value: jsii.Number) -> None:
        jsii.set(self, "sunriseHour", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sunriseMinute")
    def sunrise_minute(self) -> jsii.Number:
        '''The minute part from the sunrise time for this date.

        **Set separately after an instance is created**

        :property: sunriseMinute
        :type: {Number}
        '''
        return typing.cast(jsii.Number, jsii.get(self, "sunriseMinute"))

    @sunrise_minute.setter
    def sunrise_minute(self, value: jsii.Number) -> None:
        jsii.set(self, "sunriseMinute", value)


@jsii.data_type(
    jsii_type="kollavarsham.Settings",
    jsii_struct_bases=[],
    name_mapping={
        "latitude": "latitude",
        "longitude": "longitude",
        "system": "system",
    },
)
class Settings:
    def __init__(
        self,
        *,
        latitude: jsii.Number,
        longitude: jsii.Number,
        system: builtins.str,
    ) -> None:
        '''
        :param latitude: 
        :param longitude: 
        :param system: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "latitude": latitude,
            "longitude": longitude,
            "system": system,
        }

    @builtins.property
    def latitude(self) -> jsii.Number:
        result = self._values.get("latitude")
        assert result is not None, "Required property 'latitude' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def longitude(self) -> jsii.Number:
        result = self._values.get("longitude")
        assert result is not None, "Required property 'longitude' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def system(self) -> builtins.str:
        result = self._values.get("system")
        assert result is not None, "Required property 'system' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Settings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BaseDate",
    "JulianDate",
    "Kollavarsham",
    "KollavarshamDate",
    "MasaName",
    "Naksatra",
    "SakaDate",
    "Settings",
]

publication.publish()
