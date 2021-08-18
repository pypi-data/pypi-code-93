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

import base64
import numpy
import uuid

from majormode.perseus.constant.contact import ContactName
from majormode.perseus.model.geolocation import GeoPoint
from majormode.perseus.model.locale import DEFAULT_LOCALE
from majormode.perseus.utils import cast

from majormode.mercurius.constant.place import AddressComponentName


class Place:
    def __eq__(self, other):
        """
        Compare the current place object to another passed to the comparison
        method.  The two place objects must have the same identification, even
        if some of their attributes might be different.

        @param other: a ``Place`` instance to compare with the current place
            object.

        @return: ``True`` if the given place corresponds to the current place;
            ``False`` otherwise.
        """
        return self.place_id and other.place_id \
            and self.place_id == other.place_id

    def __init__(
            self,
            location,
            address=None,
            area_id=None,
            category_id=None,
            contacts=None,
            cover_photo_id=None,
            cover_photo_url=None,
            locale=DEFAULT_LOCALE,
            object_status=None,
            place_id=None,
            place_ref=None,
            timezone=None):
        """
        Build a new instance ``Place``.


        @param location: either an instance ``GeoPoint`` corresponding to the
            geographic coordinates of the location, either a polygon
            specifying the boundaries's region of the place as an array of
            vertices.  There must be at least three vertices.  Each vertex
            is a tuple composed of a longitude, a latitude, and a altitude::

                [ longitude, latitude, altitude ]

            where:

            * ``altitude`` (optional): altitude in meters of the place.

            * ``latitude`` (required): latitude-angular distance, expressed
              in decimal degrees (WGS84 datum), measured from the center of
              the Earth, of a point north or south of the Equator
              corresponding to the place's location.

            * ``longitude`` (required): longitude-angular distance, expressed
              in decimal degrees (WGS84 datum), measured from the center of
              the Earth, of a point east or west of the Prime Meridian
              corresponding to the place's location.

            Note that the first and last vertices must not be identical; a
            polygon is "auto-closed" between the first and last vertices.

            When specifying the boundaries of the place, the function
            automatically computes the coordinates of the geometric center
            (centroid) of the polygon representing the boundaries of the
            place.  It corresponds to the arithmetic mean ("average") position
            of all the points in the shape.

        @param address: postal address of the place, composed of one or more
            address components, which textual information is written in the
            specified locale.  An address component is defined with a
            component type and its value.  A component type is an item of the
            enumeration ``AddressComponentName``.

        @param area_id: identification of the geographic area where the place
            is located in.  This parameter is optional if the argument
            ``address`` is passed.  Both ``area_id`` and ``address`` can be
            passed to the constructor.  If this argument is passed to the
            constructor, it takes precedence over any administrative division
            of the same level or larger that would be defined as part of the
            address components.

        @param category_id: identification of the category that qualifies
            this place.

        @param contacts: list of properties such as e-mail addresses, phone
            numbers, etc., in respect of the electronic business card
            specification (vCard).  The contact information is represented by
            a list of tuples of the following form::

                [
                  (name:ContactPropertyName,
                   value:string[,
                   is_primary:boolean[,
                   is_verified:boolean] ]),
                   ...
                ]

            where:

            * ``name`` (required): type of this contact information, which
              can be one of these standard names in respect of the electronic
              business card specification (vCard).  This type is an item of
              the enumeration ``ContactPropertyName``.

            * ``value`` (required): value of this contact information
              representing by a string, such as ``+84.01272170781``, the
              formatted value for a telephone number property.

            * ``is_primary`` (optional): indicate whether this contact
              information is the primary for this place.  By default, the
              first contact information of a given type is the primary of this
              place.

            * ``is_verified`` (optional): indicate whether this contact
              information has been verified, whether it has been grabbed from
              a trusted Social Networking Service (SNS), or whether through a
              challenge/response process.

        @param ``cover_photo_id``: identification of the cover photo of the place,
            if any defined.

        @param ``cover_photo_url``: Uniform Resource Locator (URL) that specifies
            the location of the cover photo of the place, if any defined.  The
            client application can use this URL and append the query parameter
            ``size`` to specify a given pixel resolution of this photo, such as
            ``thumbnail``, ``small``, ``medium``, ``large``.

        @param locale: an instance ``Locale`` of the textual information that
            describes this place.

        @param place_id: the identification of the place when this place is
            already registered against the server platform.

        @param place_ref: reference of the place has given by the client
            application. This reference is used for a new place that has no
            identification yet.

        @param timezone: time zone at the place's location.  It is the
            difference between the time at this location and UTC (Coordinated
            Universal Time).  UTC is also known as GMT or Greenwich Mean Time
            or Zulu Time.
        """
        if isinstance(location, GeoPoint):
            self.location = location
            self.boundaries = None
        else:
            if len(location) < 3:
                raise ValueError("The polygon of the place's boundaries MUST be defined with at least three vertices")

            # Compute the coordinates of the geometric center (centroid) of the
            # polygon representing the boundaries of the place.  It corresponds to
            # the arithmetic mean ("average") position of all the points in the
            # shape.
            (longitude, latitude, altitude) = numpy.mean(location, axis=0)
            self.location = GeoPoint(latitude, longitude, altitude=altitude)
            self.boundaries = location

        self.place_id = place_id and (place_id if isinstance(place_id, uuid.UUID) else uuid.UUID(place_id))
        if place_id is None:
            place_ref = place_ref and place_ref.strip()
            self.place_ref = place_ref \
                or base64.b64encode(uuid.uuid1().hex.encode())[:-1]  # Remove final "=" character

        self.category_id = category_id and (category_id if isinstance(category_id, uuid.UUID) else uuid.UUID(category_id))
        self.cover_photo_id = cover_photo_id and (cover_photo_id if isinstance(cover_photo_id, uuid.UUID) else uuid.UUID(cover_photo_id))
        self.cover_photo_url = cover_photo_url

        self.object_status = object_status

        self.area_id = area_id

        if address is None:
            self.address = None
        elif isinstance(address, dict):
            self.address = self.__parse_address(address)
        else:
            self.address = [self.__parse_address(localized__address) for localized__address in address]

        if contacts and len([
            contact
            for contact in contacts
            if not isinstance(contact, tuple)
               or not 2 <= len(contact) <= 4
        ]) > 0:
            raise ValueError("One or more contact information have not a valid format")

        self.contacts = contacts

        self.locale = locale
        self.timezone = timezone

    @staticmethod
    def __parse_address(components):
        return dict([
            (component_name if not isinstance(component_name, str)
             else cast.string_to_enum(component_name, AddressComponentName),
             component_value.strip())
            for component_name, component_value in components.items()
            if component_value and component_value.strip()
        ])

    @staticmethod
    def from_json(payload):
        """
        Build a ``Place`` instance from the specified JSON object.


        @param payload: JSON representation of a place::

                {
                  "area_id": string,
                  "address": {
                    component_name: string,
                    ...
                  } | [
                    {
                      "locale": string,
                      component_name: string,
                      ...
                    },
                    ...
                  ],
                  "category": string,
                  "contacts": [
                    [ name:string, value:string, is_primary:boolean ],
                    ...
                  ],
                  "cover_photo_id": string,
                  "cover_photo_url": string,
                  "boundaries": [ vertex, ... ],
                  "locale": string,
                  "location": coordinates,
                  "timezone": integer
                }

            where:

            * ``area_id`` (optional): identification of the geographic area
              where the place is located in.  This parameter is optional if the
              parameter ``address`` is passed.  Both ``area_id`` and ``address``
              can be passed to the function.  If this parameter is passed to the
              function, it takes precedence over any administrative division of
              the same level or larger that would be defined as part of the
              address components.

            * ``address`` (required): postal address of the place, composed of one
              or more address components, which textual information is written in
              the specified locale.  An address component is defined with a
              component type and its value.  The component type is a string
              representation of an item of the enumeration
              ``AddressComponentName``.

            * ``category_id`` (optional): category qualifying this place.

            * ``contacts`` (optional): list of properties such as e-mail
              addresses, phone numbers, etc., in respect of the electronic
              business card specification (vCard).  The contact information is
              represented by a list of tuples of the following form::

                  [ [ name:ContantPropertyName, value:string[, is_primary:boolean] ], ... ]

              where:

              * ``name`` (required): type of this contact information, which
                can be one of these standard names in respect of the electronic
                business card specification (vCard).

              * ``value`` (required): value of this contact information
                representing by a string, such as ``+84.01272170781``, the
                formatted value for a telephone number property.

              * ``is_primary`` (optional): indicate whether this contact
                information is the primary for this place.  By default, the first
                contact information of a given type is the primary of this place.


              * ``cover_photo_id``: identification of the cover photo of the place,
                if any defined.

              * ``cover_photo_url``: Uniform Resource Locator (URL) that specifies
                the location of the cover photo of the place, if any defined.  The
                client application can use this URL and append the query parameter
                ``size`` to specify a given pixel resolution of this photo, such as
                ``thumbnail``, ``small``, ``medium``, ``large``.

            * ``boundaries`` (optional): a collection of one or more polygons that
              delimit the topological space of the place.  All of the polygons are
              within the spatial reference system.  It corresponds to an array of
              vertices.  There must be at least three vertices. Each vertex is a
              tuple composed of a longitude, a latitude, and a altitude::

                [ longitude, latitude, altitude ]

              Note that the first and last vertices must not be identical; a
              polygon is "auto-closed" between the first and last vertices.

            * ``locale`` (required): locale of the textual information that
              describes this place.  A locale corresponds to a tag respecting RFC
              4646, i.e., a ISO 639-3 alpha-3 code element optionally followed by
              a dash character ``-`` and a ISO 3166-1 alpha-2 code (referencing
              the country that this language might be specific to).  For example:
              ``eng`` (which denotes a standard English), ``eng-US`` (which
              denotes an American English).

            * ``location`` (optional): geographic coordinates of the location of
              the place represented with the following JSON structure::

                  {
                    "accuracy": decimal
                    "altitude": decimal,
                    "latitude": decimal,
                    "longitude": decimal,
                  }

              where:

              * ``accuracy`` (optional): accuracy of the place's position in
                meters.

              * ``altitude`` (optional): altitude in meters of the place.

              * ``latitude`` (required): latitude-angular distance, expressed
                in decimal degrees (WGS84 datum), measured from the center of the
                Earth, of a point north or south of the Equator corresponding to
                the place's location.

              * ``longitude`` (required): longitude-angular distance,
                expressed in decimal degrees (WGS84 datum), measured from the
                center of the Earth, of a point east or west of the Prime
                Meridian corresponding to the place's location.

                .. note::

                   The parameter ``location`` is ignored when the parameter
                   ``boundaries`` is provided.  The platform computes the coordinates of
                   the geometric center (centroid) of the polygon representing the
                   boundaries of the place.  It corresponds to the arithmetic mean
                   ("average") position of all the points in the shape.

            * ``timezone`` (required): time zone at the place's location.  It is
              the difference between the time at this location and UTC
              (Coordinated Universal Time).  UTC is also known as GMT or
              Greenwich Mean Time or Zulu Time.

        @note: the name of the place corresponds to the address component
            ``recipient_name``.

        @return: a ``Place`` instance or ``None`` if the JSON payload is
            nil.
        """
        return payload \
            and Place(
                [
                    (float(lat), float(lon), float(alt))
                    for lat, lon, alt in payload['boundaries']
                ]
                if payload.get('boundaries')
                else GeoPoint.from_json(payload['location']),
                address=payload.get('address') and (
                    Place.__parse_address(payload['address'])
                    if isinstance(payload['address'], dict)
                    else [
                        Place.__parse_address(address)
                        for address in payload['address']
                    ]
                ),
                category_id=cast.string_to_uuid(payload.get('category_id')),
                area_id=cast.string_to_uuid(payload.get('area_id')),
                contacts=payload.get('contacts') and [
                    (
                        cast.string_to_enum(contact[0], ContactName),  # name
                        contact[1],                                    # value
                        contact[2] if len(contact) >= 3 else None,     # is_primary
                        contact[3] if len(contact) == 4 else None      # is_verified
                    )
                    for contact in payload['contacts']
                ],
                cover_photo_id=cast.string_to_uuid(payload.get('cover_photo_id')),
                cover_photo_url=payload.get('cover_photo_url'),
                locale=cast.string_to_locale(payload.get('locale')) and DEFAULT_LOCALE,
                object_status=payload.get("object_status"),
                place_id=cast.string_to_uuid(payload.get('place_id')),
                timezone=payload.get('timezone')
            )

    def is_info_complete(self):
        """
        Indicate if the information of the place could be considered complete
        or not, i.e., whether it has a name.

        @return: ``True`` if the place's information is complete, ``False``
            otherwise.
        """
        return self.address is not None \
            and self.address.get(AddressComponentName.recipient_name) is not None
