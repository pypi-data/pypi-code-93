import random

from mopidy import models

import factory


class ArtistJSONFactory(factory.Factory):
    id = factory.Sequence(int)
    mbid = factory.Faker("uuid4")
    name = factory.Faker("name")

    class Meta:
        model = dict


class CoverJSONFactory(factory.Factory):
    original = factory.Faker("url")

    class Meta:
        model = dict


class AlbumJSONFactory(factory.Factory):
    id = factory.Sequence(int)
    mbid = factory.Faker("uuid4")
    title = factory.Faker("name")
    tracks = factory.Iterator([list(range(i)) for i in range(1, 30)])
    artist = factory.SubFactory(ArtistJSONFactory)
    release_date = factory.Faker("date")
    cover = factory.SubFactory(CoverJSONFactory)

    class Meta:
        model = dict


class UploadJSONFactory(factory.Factory):
    uuid = factory.Faker("uuid4")
    bitrate = factory.Iterator([i * 1000 for i in (128, 256, 360)])

    class Meta:
        model = dict


class TrackJSONFactory(factory.Factory):
    id = factory.Sequence(int)
    mbid = factory.Faker("uuid4")
    title = factory.Faker("name")
    position = factory.Faker("pyint")
    duration = factory.Faker("pyint")
    creation_date = factory.Faker("date")
    artist = factory.SubFactory(ArtistJSONFactory)
    album = factory.SubFactory(AlbumJSONFactory)
    uploads = factory.LazyAttribute(lambda o: [UploadJSONFactory()])

    class Meta:
        model = dict


class ArtistFactory(factory.Factory):
    class Meta:
        model = models.Artist
