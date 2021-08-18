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


AddressComponentName = Enum(
    'building_name',

    # Human-readable address, also known as the postal address of a place.
    # A formatted address is logically composed of one or more address
    # components (e.g., house number, street name, district, city, country,
    # etc.)
    #
    # @warning: Do not parse the formatted address programmatically. Instead
    #     you should use the individual address components, which the API
    #     response includes in addition to the formatted address field.
    'formatted_address',

    # Human-readable address as determined by a geocoder, either from a
    # geographical location, either an incomplete formatted address.
    'geocoded_address',

    'city',

    'country',

    # District in rural areas and precincts in urban areas.
    'district',

    'floor_number',

    # Small settlement, with a small population, in a rural area, or a
    # component of a larger settlement or municipality.
    'hamlet',

    # Unique number of the place in the street or area, which eases to
    # locate this particular place.  House numbering schemes vary by
    # place, and in many cases even within cities.  In some areas of the
    # world, including many remote areas, houses are not numbered at all,
    # instead simply being named.  In some other areas, this numbering can
    # be composed of a first number along the street followed by a second
    # the number along intersecting street, or they would adopt a system
    # where the city is divided into small sections each with its own
    # numeric code.  The houses within that zone are then labeled based on
    # the order in which they were constructed, or clockwise around the
    # block.
    'house_number',

    # # locale of the textual information of the address component.  A locale
    # # corresponds to a tag respecting RFC 4646, i.e., a ISO 639-3 alpha-3
    # # code element optionally followed by a dash character - and a ISO
    # # 3166-1 alpha-2 code (referencing the country that this language might
    # # be specific to).  For example: eng (which denotes a standard English),
    # # eng-US (which denotes an American English).
    # 'locale',

    # A geographically localised community within a larger city, town,
    # suburb or rural area.  Neighborhoods are often social communities
    # with considerable face-to-face interaction among members.
    # Researchers have not agreed on an exact definition.  Neighborhood is
    # generally defined spatially as a specific geographic area and
    # functionally as a set of social networks.
    'neighborhood',

    # Postal code as used to address postal mail within the country.
    'postal_code',

    'province',

    # Street name or hodonym, i.e., an identifying name, given to the
    # street where the place is located in.  The street name usually forms
    # part of the address (though addresses in some parts of the world,
    # notably most of Japan, make no reference to street names).
    #
    # Street names SHOULD begiven in a two-part form: an individual name
    # known as the _specific_, and an indicator of the type of street
    # (e.g., "road", "street", "avenue", "boulevard", etc.), known as the
    # _generic_.
    'street_name',

    # Intended recipients name or other designation, which can be an
    # individual, a business, a place, an organization.
    'recipient_name',

    # Rural commune, commune-level town, urban ward.
    'ward',
)


# Intent in performing the search for places.
SearchIntent = Enum(
    # Find places within a given geographic area, instead of only finding
    # places closest to a point.  The search area is a spherical cap if a
    # radius is provided, or a bounding quadrangle if South-West and
    # North-East points are given.
    'browse',

    # Find places that the current user is likely to check-in to nearby
    # the specified location at the current moment in time.  This intent
    # should be used by a client application that needs to determine very
    # precisely a shortlist of places, ideally only one, ordered by the
    # evidence-based scoring system of the server platform.
    'checkin',

    # Find places nearby a given location, taking into account the social
    # graph of the person on behalf of whom the search query is initiated.
    # Social preferences and personal information are used to predict what
    # places will be of interest to the user.
    'social'
)
