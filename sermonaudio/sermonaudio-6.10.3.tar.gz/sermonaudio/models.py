"""API data structures"""
import datetime
import enum
import pytz

_model_override = {}

_generic_speaker_names = {"Various Speakers", "Unknown Speaker"}


class MultipleOverrideError(Exception):
    pass


class Model:
    """Base model class.

    This is responsible for some of the magic surrounding model overrides. You really should
    inherit from this.
    """

    def __init__(self, obj: dict):
        super().__init__()

        self.__obj = obj

    @classmethod
    def parse(cls, obj: dict):
        return _model_override.get(cls, cls)(obj)


def override_model(model):
    def wrapper(new_model):
        if model in _model_override:
            raise MultipleOverrideError(
                f"Multiple overrides for {model}. This is almost certainly an error."
                "If you ABSOLUTELY have a good reason for doing this, you should"
                "instead override the existing subclass of this model and let the"
                "resolution chain work deterministically. Any other use is assuredly"
                "going to land you in a world of pain."
            )

        _model_override[model] = new_model

        return new_model

    return wrapper


def isinstance_or_none(obj, t):
    return obj is None or isinstance(obj, t)


class Node(Model):
    """The base node object, which encapsulates all node API responses"""

    def __init__(self, obj: dict):
        super().__init__(obj)

        self.node_type = obj["nodeType"]
        assert isinstance(self.node_type, str)

        self.node_display_name = obj["nodeDisplayName"]
        assert isinstance(self.node_display_name, str)

        self.results = obj["results"]
        assert isinstance(self.results, list) or isinstance(self.results, dict) or self.results is None

        self.total_count = obj["totalCount"]
        assert isinstance_or_none(self.total_count, int)

        self.next = obj["next"]
        assert isinstance_or_none(self.next, str)


class Broadcaster(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.broadcaster_id = obj["broadcasterID"]
        assert isinstance(self.broadcaster_id, str)

        self.id_code = obj["idCode"]
        assert isinstance(self.id_code, str)

        self.service_times_are_preformatted = obj["serviceTimesArePreformatted"]
        assert isinstance_or_none(self.service_times_are_preformatted, bool)

        self.service_times = obj["serviceTimes"]
        assert isinstance_or_none(self.service_times, str)

        self.denomination = obj["denomination"]
        assert isinstance_or_none(self.denomination, str)

        self.address = obj["address"]
        assert isinstance_or_none(self.address, str)

        self.display_name = obj["displayName"]
        assert isinstance(self.display_name, str)

        self.short_name = obj["shortName"]
        assert isinstance(self.short_name, str)

        self.location = obj["location"]
        assert isinstance(self.location, str)

        self.latitude = obj["latitude"]
        assert isinstance_or_none(self.latitude, float)

        self.longitude = obj["longitude"]
        assert isinstance_or_none(self.longitude, float)

        self.image_url = obj["imageURL"]
        assert isinstance(self.image_url, str)

        self.album_art_url_format = obj["albumArtURL"]
        assert isinstance(self.album_art_url_format, str)

        self.minister = obj["minister"]
        assert isinstance_or_none(self.minister, str)

        self.phone = obj["phone"]
        assert isinstance_or_none(self.phone, str)

        self.listen_line_number = obj["listenLineNumber"]
        assert isinstance_or_none(self.listen_line_number, str)

        self.home_page_url = obj["homePageURL"]
        assert isinstance_or_none(self.home_page_url, str)

        self.bible_version = obj["bibleVersion"]
        assert isinstance_or_none(self.bible_version, str)

        self.facebook_username = obj["facebookUsername"]
        assert isinstance_or_none(self.facebook_username, str)

        self.twitter_username = obj["twitterUsername"]
        assert isinstance_or_none(self.twitter_username, str)

        self.about_us = obj["aboutUs"]
        assert isinstance_or_none(self.about_us, str)

        self.can_webcast = obj["canWebcast"]
        assert isinstance(self.can_webcast, bool)

        self.webcast_in_progress = obj["webcastInProgress"]
        assert isinstance(self.webcast_in_progress, bool)

        self.vacant_pulpit = obj["vacantPulpit"]
        assert isinstance(self.vacant_pulpit, bool)

        self.welcome_video_id = obj["welcomeVideoID"]
        assert isinstance_or_none(self.welcome_video_id, str)

        self.country_iso_code = obj["countryISOCode"]
        assert isinstance_or_none(self.country_iso_code, str)

        self.language_code = obj["languageCode"]
        assert isinstance_or_none(self.language_code, str)

        # Regular RSS feed of latest sermons.
        self.rss_feed_url = obj["rssFeedURL"]
        assert isinstance(self.rss_feed_url, str)

        # Feed of latest sermons in Atom format (https://validator.w3.org/feed/docs/rfc4287.html).
        self.rss_feed_atom_url = obj["rssFeedAtomURL"]
        assert isinstance(self.rss_feed_atom_url, str)

    def get_album_art_url(self, size: int):  # pragma: no cover
        """Returns a URL for the square album art with a with and height equal to the provided size argument"""
        return self.album_art_url_format.replace("{size}", str(size))

    def __str__(self):  # pragma: no cover
        return f'<Broadcaster {self.broadcaster_id} "{self.display_name}">'


class Speaker(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.display_name = obj["displayName"]
        assert isinstance(self.display_name, str)

        self.sort_name = obj.get("sortName")
        assert isinstance(self.sort_name, str)

        self.bio = obj["bio"]
        assert isinstance_or_none(self.bio, str)

        self.portrait_url = obj["portraitURL"]
        assert isinstance(self.portrait_url, str)

        self.rounded_thumbnail_image_url = obj["roundedThumbnailImageURL"]
        assert isinstance(self.rounded_thumbnail_image_url, str)

        self.album_art_url_format = obj["albumArtURL"]
        assert isinstance(self.album_art_url_format, str)

        # The following are present on certain endpoints, such as filter_options
        if obj.get("mostRecentPreachDate"):
            self.most_recent_preach_date = datetime.datetime.strptime(obj["mostRecentPreachDate"], "%Y-%m-%d").date()
        else:
            self.most_recent_preach_date = None

        self.sermon_count = obj.get("sermonCount")
        assert isinstance_or_none(self.sermon_count, int)

    def get_album_art_url(self, size: int):  # pragma: no cover
        """Returns a URL for the square album art with a with and height equal to the provided size argument"""
        return self.album_art_url_format.replace("{size}", str(size))

    @property
    def is_generic(self) -> bool:
        return self.display_name in _generic_speaker_names


@enum.unique
class MediaClass(enum.Enum):
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"

    ALL = "all"


@enum.unique
class MediaType(enum.Enum):
    MP3 = "mp3"
    AAC = "aac"

    MP4 = "mp4"

    PDF = "pdf"
    WORD = "doc"
    TRANSCRIPT = "transcript"

    JPEG = "jpg"

    ORIGINAL_AUDIO = "orig-audio"
    ORIGINAL_VIDEO = "orig-video"


class Media(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        try:
            self.media_type = MediaType(obj["mediaType"])
        except ValueError:
            self.media_type = None

        self.is_live = obj["live"]
        assert isinstance(self.is_live, bool)

        self.is_adaptive = obj["adaptiveBitrate"]
        assert isinstance(self.is_adaptive, bool)

        self.stream_url = obj["streamURL"]
        assert isinstance_or_none(self.stream_url, str)

        self.event_stream_url = obj["eventStreamURL"]
        assert isinstance_or_none(self.event_stream_url, str)

        self.download_url = obj.get("downloadURL")
        assert isinstance_or_none(self.download_url, str)

        self.bitrate = obj["bitrate"]
        assert isinstance_or_none(self.bitrate, int)

        try:
            self.file_size_bytes = obj["fileSizeBytes"]
        except ValueError:
            self.file_size_bytes = None

        self.duration = obj["duration"]
        assert isinstance_or_none(self.duration, int)

        self.audio_codec = obj["audioCodec"]
        assert isinstance_or_none(self.audio_codec, str)

        self.video_codec = obj["videoCodec"]
        assert isinstance_or_none(self.video_codec, str)

        self.thumbnail_image_url = obj["thumbnailImageURL"]
        assert isinstance_or_none(self.thumbnail_image_url, str)

        self.raw_url = obj.get("rawURL")
        assert isinstance_or_none(self.raw_url, str)


class MediaSet(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        def is_valid(rec: Media):  # Silently ignore parse errors
            return rec.media_type is not None

        self.audio = list(filter(is_valid, [Media.parse(rec) for rec in obj["audio"]]))
        self.video = list(filter(is_valid, [Media.parse(rec) for rec in obj["video"]]))
        self.text = list(filter(is_valid, [Media.parse(rec) for rec in obj["text"]]))


class Sermon(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.sermon_id = obj["sermonID"]
        assert isinstance(self.sermon_id, str)

        self.broadcaster = Broadcaster.parse(obj["broadcaster"])
        self.speaker = Speaker.parse(obj["speaker"])

        self.full_title = obj["fullTitle"]
        assert isinstance(self.full_title, str)

        self.display_title = obj["displayTitle"]
        assert isinstance(self.display_title, str)

        self.subtitle = obj["subtitle"]
        assert isinstance_or_none(self.subtitle, str)

        self.series = SermonSeries.parse(obj["series"]) if obj.get("series") else None

        self.preach_date = datetime.datetime.strptime(obj["preachDate"], "%Y-%m-%d").date()
        assert isinstance(self.preach_date, datetime.date)

        # A sermon may be picked as a staff pick by SermonAudio.
        try:
            self.staff_pick_date = datetime.datetime.strptime(obj["pickDate"], "%Y-%m-%d").date()
            assert isinstance_or_none(self.staff_pick_date, datetime.date)
        except (TypeError, ValueError):
            self.staff_pick_date = None

        # A sermon may be featured by a broadcaster by going to a sermon's page
        # and selecting the option to feature it. This given the sermon a high
        # level of visibility at SermonAudio. The last feature date is reported
        # by the API, since a sermon can be featured more than once.
        try:
            self.last_feature_date = datetime.datetime.strptime(obj["lastFeatureDate"], "%Y-%m-%d").date()
            assert isinstance_or_none(self.last_feature_date, datetime.date)
        except (TypeError, ValueError):
            self.last_feature_date = None

        timestamp = obj["publishTimestamp"]
        self.publish_timestamp = datetime.datetime.fromtimestamp(timestamp, pytz.utc) if timestamp is not None else None

        update_date = obj["updateDate"]
        self.update_date = datetime.datetime.fromtimestamp(update_date, pytz.utc)

        self.language_code = obj["languageCode"]
        assert isinstance(self.language_code, str)

        self.bible_text = obj["bibleText"]
        assert isinstance_or_none(self.bible_text, str)

        self.more_info_text = obj["moreInfoText"]
        assert isinstance_or_none(self.more_info_text, str)

        try:
            self.event_type = SermonEventType(obj["eventType"])
        except ValueError:
            self.event_type = None

        # Localized event type as a display string.
        self.display_event_type = obj["displayEventType"]
        assert isinstance_or_none(self.display_event_type, str)

        self.download_count = obj["downloadCount"]  # audio download count
        assert isinstance(self.download_count, int)

        self.video_download_count = obj["videoDownloadCount"]
        assert isinstance(self.video_download_count, int)

        self.document_download_count = obj["documentDownloadCount"]
        assert isinstance(self.document_download_count, int)

        self.external_link = obj["externalLink"]
        assert isinstance_or_none(self.external_link, str)

        self.keywords = obj.get("keywords", [])

        self.media = MediaSet.parse(obj["media"])

        self.archived_webcast_id = obj["archivedWebcastID"]
        assert isinstance_or_none(self.archived_webcast_id, int)

    def __str__(self):  # pragma: no cover
        return f"<Speaker {self.speaker.display_name} - {self.display_title}>"


class Webcast(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.display_name = obj["displayName"]
        assert isinstance_or_none(self.display_name, str)

        self.webcast_id = obj["webcastID"]
        assert isinstance(self.webcast_id, int)

        self.broadcaster_id = obj["broadcasterID"]
        assert isinstance(self.broadcaster_id, str)

        self.source_location = obj["broadcasterLocation"]
        assert isinstance_or_none(self.source_location, str)

        self.start_time = datetime.datetime.fromtimestamp(obj["startTime"], tz=pytz.utc)
        assert isinstance(self.start_time, datetime.datetime)

        try:
            self.end_time = datetime.datetime.fromtimestamp(obj["endTime"], tz=pytz.utc)
            assert isinstance_or_none(self.start_time, datetime.datetime)
        except TypeError:
            # live webcasts do not have an end time
            self.end_time = None

        self.preview_image_url = obj["previewImageURL"]
        assert isinstance_or_none(self.preview_image_url, str)

        self.resizable_preview_image_url = obj["resizablePreviewImageURL"]
        assert isinstance_or_none(self.resizable_preview_image_url, str)

        self.peak_listener_count = obj["peakListenerCount"]
        assert isinstance(self.peak_listener_count, int)

        self.total_tune_in_count = obj["totalTuneInCount"]
        assert isinstance(self.total_tune_in_count, int)

        self.total_listen_line_count = obj["totalListenLineCount"]
        assert isinstance(self.total_listen_line_count, int)

        self.media = MediaSet.parse(obj["media"])

        # The field archived_sermon_id has been deprecated. Originally, one
        # webcast could be archived to one sermon. By popular demand, we
        # relaxed this requirement so one webcast could be archived to multiple
        # sermons. If your webcast is linked to one sermon, this field will
        # have the sermon ID of that sermon for backwards
        # compatibility. Otherwise, it will be None. We recommend that you use
        # the archived_sermons field, which is a list of sermon IDs that have
        # been created from this webcast.
        self.archived_sermon_id = obj["archivedSermonID"]
        assert isinstance_or_none(self.archived_sermon_id, str)

        self.archived_sermons = obj["archivedSermons"]
        assert isinstance_or_none(self.archived_sermons, list)

    def __str__(self):  # pragma: no cover
        return f'<WebcastInfo {self.broadcaster_id} "{self.display_name}"">'


class RelativeBroadcasterLocation(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.broadcaster = Broadcaster.parse(obj["broadcaster"])
        assert isinstance(self.broadcaster, Broadcaster)

        self.meters = obj["meters"]
        assert isinstance(self.meters, int)

    def __str__(self):  # pragma: no cover
        return f"<RelativeBroadcasterLocation {self.broadcaster.broadcaster_id} - ~{round(self.meters/1000, 1)}km away>"


@enum.unique
class SeriesPodcastLinkType(enum.Enum):
    """The type of a series podcast link.

    The podcast type is a general category for identifying and grouping
    podcast links. The podcast type and label form a unique podcast feed
    link, so porcast types may be reused (particularly OTHER) as long as
    the labels are different.
    """

    TUNEIN = "tunein"
    APPLE = "apple"
    GOOGLE = "google-play"
    SPOTIFY = "spotify"
    STITCHER = "stitcher"

    OTHER = "other"


class SermonSeriesFeedLink(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)
        self.feed_link_id = obj["feedLinkID"]
        self.series_id = obj["seriesID"]
        self.podcast_type = SeriesPodcastLinkType(obj["podcastType"]) if obj["podcastType"] else None
        self.label = obj["label"]
        self.link = obj["link"]


class SermonSeries(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.series_id = obj["seriesID"]
        self.title = obj["title"]
        self.broadcaster_id = obj["broadcasterID"]
        self.latest = datetime.datetime.strptime(obj["latest"][:10], "%Y-%m-%d") if obj["latest"] else None
        self.earliest = datetime.datetime.strptime(obj["earliest"][:10], "%Y-%m-%d") if obj["earliest"] else None
        self.updated = datetime.datetime.fromtimestamp(obj["updated"], pytz.utc)
        self.count = obj["count"]
        self.description = obj["description"]
        self.podcast_enabled = obj["podcastEnabled"]
        self.podcast_speaker = obj["podcastSpeaker"]
        self.image = obj["image"]
        self.image_resizable = obj["imageResizable"]
        self.rss_url = obj["rssURL"]  # Regular RSS feed of latest sermons in this series.
        self.rss_atom_url = obj["rssAtomURL"]  # Feed in Atom format (https://validator.w3.org/feed/docs/rfc4287.html).

        if obj["feedLinks"]:
            self.feed_links = [SermonSeriesFeedLink(f) for f in obj["feedLinks"]]
        else:
            self.feed_links = None

    def __str__(self):  # pragma: no cover
        return f"<SermonSeries {self.title} ({self.count} sermons)>"


class SermonEventType(enum.Enum):
    AUDIO_BOOK = "Audio Book"
    BIBLE_STUDY = "Bible Study"
    CAMP_MEETING = "Camp Meeting"
    CHAPEL_SERVICE = "Chapel Service"
    CHILDREN = "Children"
    CLASSIC_AUDIO = "Classic Audio"
    CONFERENCE = "Conference"
    CURRENT_EVENTS = "Current Events"
    DEBATE = "Debate"
    DEVOTIONAL = "Devotional"
    FUNERAL_SERVICE = "Funeral Service"
    MIDWEEK_SERVICE = "Midweek Service"
    PODCAST = "Podcast"
    PRAYER_MEETING = "Prayer Meeting"
    Q_AND_A = "Question & Answer"
    RADIO_BROADCAST = "Radio Broadcast"
    SERMON_CLIP = "Sermon Clip"
    SPECIAL_MEETING = "Special Meeting"
    SUNDAY_AFTERNOON = "Sunday Afternoon"
    SUNDAY_AM = "Sunday - AM"
    SUNDAY_PM = "Sunday - PM"
    SUNDAY_SCHOOL = "Sunday School"
    SUNDAY_SERVICE = "Sunday Service"
    TEACHING = "Teaching"
    TESTIMONY = "Testimony"
    TV_BROADCAST = "TV Broadcast"
    VIDEO_DVD = "Video DVD"
    WEDDING = "Wedding"
    YOUTH = "Youth"


class SermonEventTypeDetail(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.type = obj.get("type")
        self.description = obj.get("description")
        self.display_event_type = obj.get("displayEventType")
        self.number_of_sermons = obj.get("numberOfSermons")
        self.roku_image_url = obj.get("rokuImageURL")
        self.fire_tv_image_url = obj.get("fireTVImageURL")
        self.number_of_sermons = obj.get("numberOfSermons")


@enum.unique
class SpurgeonDevotionalType(enum.Enum):
    AM = "AM"  # Morning Devotional
    PM = "PM"  # Evening Devotional
    CHECKBOOK = "CHECKBOOK"  # Faith's Checkbook (note American spelling)


class SpurgeonDevotional(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.type = SpurgeonDevotionalType(obj["type"])
        self.month = obj["month"]
        self.day = obj["day"]
        self.quote = obj["quote"]
        self.reference = obj["reference"]
        self.content = obj["content"]
        self.audio = Sermon.parse(obj["sermon"])

    def __str__(self):  # pragma: no cover
        return f"<SpurgeonDevotional for {self.month}/{self.day}>"


@enum.unique
class SermonSortOption(enum.Enum):
    DOWNLOADS = "downloads"
    EVENT = "event"
    LANGUAGE = "language"
    LAST_PLAYED = "lastplayed"
    NEWEST = "newest"
    NEWEST_PUBLISHED = "newest-published"
    OLDEST = "oldest"
    PICK_DATE = "pickdate"
    SERIES = "series"
    SPEAKER = "speaker"
    UPDATED = "updated"
    RANDOM = "random"
    ADDED = "added"
    TITLE = "title"


class Book(Model):
    """A book of the bible, and associated chapters that you can use to filter a broadcaster's content"""

    def __init__(self, obj: dict):
        super().__init__(obj)

        self.name = obj["bookName"]
        self.display_name = obj["displayBookName"]
        self.chapters = obj["chapters"]
        self.osis_pa = obj["osisPA"]


class Language(Model):
    """A language that you can use to filter a broadcaster's content"""

    def __init__(self, obj: dict):
        super().__init__(obj)

        self.name = obj["languageName"]
        self.iso_code = obj["languageCode"]


class SermonCountForSpeaker(Model):
    """A speaker name, and how many sermons they preached at a broadcaster (used for filtering)"""

    def __init__(self, obj: dict):
        super().__init__(obj)

        self.count = obj["count"]
        self.speaker_name = obj["speaker"]


class FilterOptions(Model):
    """A set of various things that you can filter by.

    For example, which books and chapters of the Bible have content, which speakers
    have spoken at a given church/ministry, etc.
    """

    def __init__(self, obj: dict):
        super().__init__(obj)

        self.books = [Book.parse(rec) for rec in obj["bibleBooks"]]
        self.languages = [Language.parse(rec) for rec in obj["languages"]]
        self.series = [SermonSeries.parse(rec) for rec in obj["series"]]
        self.speakers = [Speaker.parse(rec) for rec in obj["speakers"]]
        self.sermon_counts_for_speakers = [SermonCountForSpeaker.parse(rec) for rec in obj["sermonCountsForSpeakers"]]
        self.sermon_event_types = [SermonEventTypeDetail.parse(rec) for rec in obj["sermonEventTypes"]]
        self.years: [int] = [rec["year"] for rec in obj["years"]]  # This structure is simple enough to reduce


@enum.unique
class SeriesFilter(enum.Enum):
    DEFAULT = "all"
    PODCAST_ENABLED = "podcast-enabled"
    PODCAST_DISABLED = "podcast-disabled"


@enum.unique
class SeriesSortOrder(enum.Enum):
    # The last date that the series was "touched" (never goes back in time)
    LAST_UPDATED = "last_updated"

    # The *create* date of the latest sermon in the series (may go back in time)
    NEWEST_SERMON_CREATE_DATE = "newest_sermon_create_date"

    # Title sort ascending
    TITLE = "title"

    # Sermon count DESC
    SERMON_COUNT_HIGHEST = "sermon_count_highest"

    # Sermon count DESC
    SERMON_COUNT_LOWEST = "sermon_count_lowest"


@enum.unique
class HighlightedAudioInputTypes(enum.Enum):
    """Input values to select the type of highlighted audio.

    You may set the highlighted sermon to a specific sermon, or to the
    most recent sermon from a specific event type. Otherwise, you may
    select the most recent sermon a broadcaster has uploaded, or a
    random sermon from the broadcaster's archive. Random and newest pick
    are reserved for future use, but not currently used.
    """

    RANDOM_SERMON = "randomsource"
    NEWEST_SERMON = "newest"
    RANDOM_PICK = "randompick"
    NEWEST_PICK = "newestpick"
    SERMON_ID = "sermon_id"
    EVENT_TYPE = "event_type"


class HighlightedSortOrders(enum.Enum):
    """Input values to select the order of highlighted sermons.

    Broadcasters have a short list sermons on their home pages, and this
    setting selects the order in which the list is sorted. As with
    HighlightedAudioInputTypes, random and newest picks are reserved but
    not currenly used.

    Note that the use of "pick" here as an enum value is retained for
    historical compatibility. These picks are listener recommendations
    ("listener picks"), not staff picks.
    """

    PREACHED = "preached"
    POPULAR = "popular"
    ADDED = "added"
    NEWEST_PICKS = "picklistnewest"
    RANDOM_PICKS = "picklistrandom"
    NEWEST_CLIPS = "clipsnewest"
    RANDOM_CLIPS = "clipsrandom"
    DEFAULT = "added"

    @property
    def sermon_parameters(self):
        """Get dict of sermon parameters for current sort order.

        The sort order value, by itself, is not particularly useful, so
        this method translates it into a dict of parameters you can pass
        to Node.get_sermons() to retrieve sermons sorted in that order.

        You can directly pass a HighlightedSortOrders value as the
        sort_by parameter to Node.get_sermons().

        For more control over the Node.get_sermons() parameters, you may
        retrieve this property as a dict, update it as necessary, and
        pass it to Node.get_sermons().

        Example:
            highlighted_sermons  = Node.get_highlighted_sermons()
            params = highlighted_sermons.sort_order.sermon_parameters
            # ... update params...
            sermons = Node.get_sermons(**params)
        """

        if self is self.ADDED:
            return {"sort_by": SermonSortOption.ADDED}
        elif self is self.NEWEST_PICKS:
            return {"listener_recommended": True, "sort_by": SermonSortOption.NEWEST}
        elif self is self.RANDOM_PICKS:
            return {"listener_recommended": True, "sort_by": SermonSortOption.RANDOM}
        elif self is self.NEWEST_CLIPS:
            return {"event_type": SermonEventType.SERMON_CLIP, "sort_by": SermonSortOption.NEWEST}
        elif self is self.RANDOM_CLIPS:
            return {"event_type": SermonEventType.SERMON_CLIP, "sort_by": SermonSortOption.RANDOM}
        elif self is self.POPULAR:
            return {"sort_by": SermonSortOption.DOWNLOADS}
        else:
            return {"sort_by": SermonSortOption.NEWEST}


class HighlightedSermons(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        if obj["sortOrder"]:
            self.sort_order = HighlightedSortOrders(obj["sortOrder"])
            assert isinstance(self.sort_order, HighlightedSortOrders)
        else:
            self.sort_order = None

        self.sort_title = obj["sortTitle"]
        assert isinstance_or_none(self.sort_title, str)

        self.audio_title = obj["audioTitle"]
        assert isinstance_or_none(self.audio_title, str)

        if obj["audioSermon"]:
            self.audio_sermon = Sermon.parse(obj["audioSermon"])
            assert isinstance(self.audio_sermon, Sermon)
        else:
            self.audio_sermon = None


@enum.unique
class ListSortOrder(enum.Enum):
    DATE = "date"
    REVERSE_DATE = "reverse-date"


class WebcastStats(Model):
    def __init__(self, obj: dict):

        # The webcast_id can be None because this class is used for cumulative
        # stats, where no specific webcast_id exists, as well as individual
        # webcasts.
        self.webcast_id = obj["webcastID"]
        assert isinstance_or_none(self.webcast_id, int)

        self.total_countries = obj["totalCountries"]
        assert isinstance(self.total_countries, int)

        self.locations = obj["locations"]
        assert isinstance(self.locations, dict)


class WebcastRangeTotals(Model):
    def __init__(self, obj: dict):
        self.broadcaster_id = obj["broadcasterID"]

        self.start_time = datetime.datetime.fromtimestamp(obj["startTime"], tz=pytz.utc)
        assert isinstance(self.start_time, datetime.datetime)

        self.end_time = datetime.datetime.fromtimestamp(obj["endTime"], tz=pytz.utc)
        assert isinstance(self.end_time, datetime.datetime)

        self.max_peak_listener_count = obj["maxPeakListenerCount"]
        assert isinstance(self.max_peak_listener_count, int)

        self.avg_total_tune_in_count = obj["averageTotalTuneInCount"]
        assert isinstance(self.avg_total_tune_in_count, int)

        self.total_webcast_views = obj["totalWebcastViews"]
        assert isinstance(self.total_webcast_views, int)

        self.total_listen_line_count = obj["totalListenLineCount"]
        assert isinstance(self.total_listen_line_count, int)

        self.cumulative_stats = WebcastStats.parse(obj["cumulativeStats"])
