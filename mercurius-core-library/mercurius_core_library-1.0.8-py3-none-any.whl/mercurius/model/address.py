# Copyright (C) 2019 Majormode.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from majormode.perseus.model.enum import Enum
from majormode.perseus.model.locale import DEFAULT_LOCALE
from majormode.perseus.model.locale import Locale
from majormode.perseus.utils import cast

from majormode.mercurius.constant.place import AddressComponentName


class AddressComponent:
    def __init__(self, property_name, property_value, locale=None):
        if isinstance(property_name, str):
            property_name = cast.string_to_enum(property_name, AddressComponentName)

        if not isinstance(property_value, str):
            raise ValueError("The argument `value` MUST be a string")

        if locale is None:
            locale = DEFAULT_LOCALE
        elif not isinstance(locale, Locale):
            raise ValueError("The argument `locale` MUST be an object `Locale`")

        self.__property_name = property_name
        self.__property_value = property_value
        self.__locale = locale

    @property
    def locale(self):
        return self.__locale

    @property
    def property_name(self):
        return self.__property_name

    @property
    def property_value(self):
        return self.__property_value


class Address:
    """
    Represent the address information of a place
    """
    @staticmethod
    def __build_from_dictionary(dct, locale):
        components = {}
        for property_name_str, property_value in dct.items():
            property_name = cast.string_to_enum(property_name_str, AddressComponentName)
            components[property_name] = AddressComponent(
                property_name,
                property_value,
                locale=locale)
        return components

    @staticmethod
    def __build_from_list(lst, locale):
        components = {}
        for component in lst:
            if not isinstance(component, AddressComponent):
                raise TypeError(f"Invalid type of item {component}")
            components[component.property_name] = component
        return components

    def __init__(self, components, locale=None):
        """
        Build a new instance `Address`.


        :param components: A dictionary `{k: v}` or an iterable (list, set, or
           tuple) of two elements `{k, v}` where `k` corresponds to an item of
           the enumeration `AddressComponentName` and `v` the string value.

        :param locale: An object `Locale` representing the language which the
            address information is written in, or `None` for the default
            language.
        """
        if locale is None:
            locale = DEFAULT_LOCALE
        elif not isinstance(locale, Locale):
            raise TypeError("The argument 'locale' MUST be an object 'Locale'")

        self.__locale = locale

        if isinstance(components, dict):
            self.__components = self.__build_from_dictionary(components, locale)
        elif isinstance(components, (list, set, tuple)):
            self.__components = self.__build_from_list(components, locale)
        else:
            raise TypeError("The argument `components` MUST be a dictionary, a list, a set, or a tuple")

    @property
    def components(self):
        """
        Return a dictionary of address components


        :return: A dictionary where the key corresponds to an item of the
            enumeration `AddressComponentName` and the value is an object
            `AddressComponent`.
        """
        return self.__components

    @property
    def locale(self):
        return self.__locale

    @staticmethod
    def from_json(payload, locale=None):
        return payload and Address(payload, locale=locale)


class LocalizedAddress:
    """
    Address written in multiple languages
    """
    def __init__(self, addresses, is_default_locale_required=False):
        """
        Build a new object `LocalizedAddress`


        :param addresses: A dictionary of `Address` objects where the key
            corresponds to an object `Locale`.

        :param is_default_locale_required: Indicate whether the address needs
            to be at least written in the default locale.


        :raise ValueError: If the argument `addresses` is not a dictionary of
            `Address` objects, of if the keys of this dictionary are not
            `Locale` objects, or if no address is given in the default locale
            while the argument `is_default_locale_required` is `True`.
        """
        if not isinstance(addresses, dict):
            raise ValueError("The argument 'addresses' MUST be a dictionary")

        if any([not isinstance(locale, Locale) for locale in addresses.keys()]):
            raise ValueError("The keys of the dictionary 'address' MUST be objects `Locale`")

        if any([not isinstance(address, Address) for address in addresses.values()]):
            raise ValueError("The values of the dictionary 'address' MUST be objects `Address`")

        if is_default_locale_required and DEFAULT_LOCALE not in addresses:
            raise ValueError(f'Missing address written in the default locale "{DEFAULT_LOCALE}"')

        self.__addresses = addresses

    @property
    def addresses(self):
        """
        Return the localized versions of the address


        :return: A dictionary of `Address` objects where the keys are objects
            `Locale`.
        """
        return self.__addresses

    def get_address(
            self,
            locale=None,
            strict=True,
            use_default_locale=False):
        """
        Return the address written in the specified locale


        :param locale: An object `Locale`.  If not defined, the function will
            return the address in the default locale.

        :param strict: Indicate whether the caller expects the address to be
            written in the specified locale.  If `True`, the function will
            the exception `KeyError` if the address is not written in the
            specified locale.  If `False`, the function will return `None`  if
            the address is not written in the specified locale.

        :param use_default_locale: Indicate whether to return the address in
            the default locale if it was not available in the specified locale.


        :return: An object `Address` corresponding to the specified or the
            default locale, or `None` if no address is written in required
            locale.
        """
        if locale is None:
            locale = DEFAULT_LOCALE
        elif not isinstance(locale, Locale):
            raise ValueError("The argument 'locale' MUST be an object `Locale`")

        address = self.__addresses.get(locale)

        if address is None and locale != DEFAULT_LOCALE and use_default_locale:
            address = self.__addresses.get(DEFAULT_LOCALE)

        if address is None and strict:
            raise KeyError(f'Unavailable address for the locale "{locale}')

        return address

    @classmethod
    def from_json(cls, payload, is_default_locale_required=False):
        if payload is None:
            return None

        if not isinstance(payload, dict):
            raise ValueError("The argument 'payload' MUST be a dictionary")

        addresses = {}
        for key, value in payload.items():
            locale = Locale.from_string(key)
            addresses[locale] = Address.from_json(value, locale=locale)  # No duplicate possible

        return LocalizedAddress(
            addresses,
            is_default_locale_required=is_default_locale_required)
