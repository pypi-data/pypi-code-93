import datetime
import functools

from http import HTTPStatus
from typing import Optional, List, Dict

from sermonaudio import API, APIException, _session, models
from sermonaudio.models import Sermon, SermonEventType, SermonSeries, SeriesPodcastLinkType
from sermonaudio.utils import update_kwargs_for_key, join_url_path


class BroadcasterAPIError(APIException):  # pragma: no cover
    pass


def parse_sermon(response) -> Sermon:  # pragma: no cover
    if response.ok:
        return Sermon.parse(response.json())
    else:
        raise BroadcasterAPIError(response.json())


def check_response_code_or_throw(response) -> bool:  # pragma: no cover
    """Returns true if response is successful from an endpoint that returns nothing."""
    if response.ok:
        return True
    else:
        if response.json():
            raise BroadcasterAPIError(response.json())
        else:
            # If no error message was returned, use the status code.
            raise BroadcasterAPIError({"errors": {"status_code": response.status_code}})


def check_response_code_or_throw_return_dict(response) -> Dict:  # pragma: no cover
    if response.ok:
        return response.json()
    else:
        raise BroadcasterAPIError(response.json())


class Broadcaster(API):  # pragma: no cover. Unfortunately we can't test this w/o a test account...
    @classmethod
    def create_or_update_sermon(
        cls,
        sermon_id: Optional[str],
        accept_copyright: bool,
        full_title: str,
        speaker_name: str,
        preach_date: datetime.date,
        publish_timestamp: Optional[datetime.datetime],
        event_type: SermonEventType,
        display_title: Optional[str],
        subtitle: Optional[str],
        bible_text: Optional[str],  # TODO: structure this data
        more_info_text: Optional[str],
        language_code: str,
        keywords: Optional[List[str]],
        **kwargs,
    ) -> Sermon:
        """Creates a new sermon record or updates an existing one (media uploaded separately).

        :param sermon_id: The sermon ID, if you are updating an existing sermon. Otherwise, None.
        :param accept_copyright: A boolean value indicating that you agree that you are allowed to upload this content.
        :param full_title: The full sermon title.
        :param speaker_name: The speaker name (please be consistent; speakers will be created if they don't exist).
        :param preach_date: The date the sermon was preached.
        :param publish_timestamp: The time that the sermon should be visible on the site. You must submit this in order
        for the sermon to be visible to the public. Callers are encouraged to use timezone aware objects to ensure
        that the correct timestamp is generated.
        :param event_type: The type of event that this sermon was preached at.
        :param display_title: An alternate, shorter version of the title to be displayed in ID3v1 tags and parts of
        the legacy site (30 char limit)
        :param subtitle: The subtitle of the sermon (or the series, if multiple sermons use the same subtitle; this
        will likely be reworked in the future)
        :param bible_text: The scripture passage(s) that this sermon was derived from
        :param more_info_text: Additional info about the sermon that you wish to share
        :param language_code: The ISO 639 language code for the sermon.
        :param keywords: A list of keywords for this sermon.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: The created sermon
        """
        update_kwargs_for_key(
            kwargs,
            "params",
            {
                "acceptCopyright": accept_copyright,
                "fullTitle": full_title,
                "speakerName": speaker_name,
                "preachDate": preach_date.isoformat(),
                "publishTimestamp": int(publish_timestamp.timestamp()) if publish_timestamp else None,
                "eventType": event_type.value,
                "displayTitle": display_title,
                "subtitle": subtitle,
                "bibleText": bible_text,
                "moreInfoText": more_info_text,
                "languageCode": language_code,
                "newsInFocus": "false",
                "keywords": " ".join(keywords) if keywords else None,
            },
        )

        if sermon_id:
            path = join_url_path("node", "sermons", sermon_id)
            method = "put"
        else:
            path = join_url_path("node", "sermons")
            method = "post"

        return cls._request(path, method, json=kwargs["params"], parse_func=parse_sermon, **kwargs)

    @classmethod
    def publish_sermon(cls, sermon_id: str):  # pragma: no cover
        path = join_url_path("node", "sermons", sermon_id)
        params = {"publishNow": True}
        return cls.patch(path, params)

    @classmethod
    def move_sermon_to_series(cls, sermon_id: str, series_id: str):  # pragma: no cover
        path = join_url_path("node", "sermons", sermon_id)
        params = {"series_id": series_id}
        return cls.patch(path, params)

    @classmethod
    def delete_sermon(cls, sermon_id: str):  # pragma: no cover
        path = join_url_path("node", "sermons", sermon_id)
        return cls.delete(path)

    @classmethod
    def duplicate_sermon(cls, sermon_id: str, **kwargs) -> Sermon:  # pragma: no cover
        path = join_url_path("node", "sermons", sermon_id, "duplicate")
        return cls.post(path, parse_func=parse_sermon, **kwargs)

    @classmethod
    def _upload_media(cls, upload_type: str, sermon_id: str, path: str, **kwargs):  # pragma: no cover
        """Uploads media for a sermon.
        :param upload_type: The type of media to upload.
        :param sermon_id: The Sermon ID you are uploading media for.
        :param path: The path to the file on disk.
        :param kwargs: Additional arguments to pass to the underlying post method.
        :return: No return value. Throws a BroadcasterAPIError with details on failure.
        """
        update_kwargs_for_key(kwargs, "params", {"uploadType": upload_type, "sermonID": sermon_id})

        response = cls.post("media", **kwargs)

        if response.status_code != HTTPStatus.CREATED:
            raise BroadcasterAPIError({"error": "Unable to create media upload", "json": response.json()})

        upload_url = response.json()["uploadURL"]

        with open(path, "rb") as fp:
            response = _session.post(upload_url, data=fp, stream=True, **kwargs)
            if not response.ok:
                raise BroadcasterAPIError(
                    {
                        "error": f"Received unexpected HTTP status code {response.status_code} when uploading data.",
                        "response": response.content,
                    }
                )

    upload_audio = functools.partialmethod(_upload_media, "original-audio")
    upload_video = functools.partialmethod(_upload_media, "original-video")

    #
    # Series
    #
    @classmethod
    def create_series(
        cls,
        title: str,
        broadcaster_id: str,
        description: Optional[str] = None,
        podcast_enabled: Optional[bool] = False,
        podcast_email: Optional[str] = None,
        podcast_speaker: Optional[str] = None,
    ) -> Optional[SermonSeries]:  # pragma: no cover
        """Creates an empty series.

        The new series can't already exist.

        :param title: The title for the new series.
        :param broadcaster_id: The ID of the broadcaster that will own the series.
        :param description: Text description of the series.
        :param podcast_enabled: If set, the series will show up as a podcast.
        :param podcast_email: Added to RSS feed for validation.
        :param podcast_speaker: If set, the speaker name in the "author" field of the RSS feed.
        :return: The series, if it was created successfully.
        """

        params = {
            "series_name": title,
            "description": description,
            "podcast_enabled": podcast_enabled,
            "podcast_email": podcast_email,
            "podcast_speaker": podcast_speaker,
        }

        path = join_url_path("node", "broadcasters", broadcaster_id, "series")
        return cls.post(path, data=params, parse_func=lambda res: SermonSeries(res.json()) if res.ok else None)

    @classmethod
    def update_series_description(
        cls, id_or_current_title: str, description: str, broadcaster_id: str, **kwargs
    ) -> bool:  # pragma: no cover
        """Updates the description for a series.

        :param id_or_current_title: The ID or current title of the series.
        :param description: The new title for the series.
        :param broadcaster_id: The ID of the broadcaster that owns the series.
        :return: Boolean indicating success.
        """
        path = join_url_path("node", "broadcasters", broadcaster_id, "series", "metadata", id_or_current_title)
        return cls.patch(path, json={"description": description}, parse_func=check_response_code_or_throw, **kwargs)

    @classmethod
    def update_series_podcast_speaker(
        cls, id_or_current_title: str, podcast_speaker: str, broadcaster_id: str, **kwargs
    ) -> bool:  # pragma: no cover
        """Updates the podcast speaker for a series.

        This speaker name appears as the "author" in the RSS feed for a
        series. It does not have to be a valid SermonAudio speaker.

        :param id_or_current_title: The ID or current title of the series.
        :param description: The speaker.
        :param broadcaster_id: The ID of the broadcaster that owns the series.
        :return: Boolean indicating success.
        """
        path = join_url_path("node", "broadcasters", broadcaster_id, "series", "metadata", id_or_current_title)
        return cls.patch(
            path, json={"podcastSpeaker": podcast_speaker}, parse_func=check_response_code_or_throw, **kwargs
        )

    @classmethod
    def update_series_podcast_enabled(
        cls, id_or_current_title: str, podcast_enabled: bool, broadcaster_id: str, **kwargs
    ) -> bool:  # pragma: no cover
        """Updates the podcast enabled flag for a series.

        A series which has podcast enabled set will show up as a
        podcast. Otherwise, it will be a normal series.

        :param id_or_current_title: The ID or current title of the series.
        :param podcast_enabled: Flag (True=podcast enabled; False=not enabled.)
        :param broadcaster_id: The ID of the broadcaster that owns the series.
        :return: Boolean indicating success.
        """
        path = join_url_path("node", "broadcasters", broadcaster_id, "series", "metadata", id_or_current_title)
        return cls.patch(
            path, data={"podcastEnabled": podcast_enabled}, parse_func=check_response_code_or_throw, **kwargs
        )

    @classmethod
    def create_or_update_feed_link(
        cls,
        id_or_current_title: str,
        broadcaster_id: str,
        podcast_type: SeriesPodcastLinkType,
        feed_link_id: Optional[int] = 0,
        label: Optional[str] = "",
        link: Optional[str] = "",
        **kwargs,
    ) -> Dict:  # pragma: no cover
        """Add a feed link to a series.

        A series must have the podcast flag set for this call to
        work. The operation is an "upsert" which will update the URL for
        a podcast type and label if it already exists.
        """

        params = {
            "podcast_type": podcast_type.value,
            "feed_link_id": feed_link_id,
            "label": label,
            "link": link,
        }

        path = join_url_path("node", "broadcasters", broadcaster_id, "series", id_or_current_title, "podcast_link")
        return cls.post(path, data=params, parse_func=check_response_code_or_throw_return_dict, **kwargs)

    @classmethod
    def delete_feed_link_from_series(
        cls, id_or_current_title: str, broadcaster_id: str, feed_link_id: int, **kwargs
    ) -> bool:  # pragma: no cover
        """Deletes a feed link from a series.

        A series must have the podcast flag set for this call to
        work. The feed link ID is in the feed_link_id member of the
        elements in the Series.feed_links list.

        :param id_or_title: The ID or title of the series to delete.
        :param broadcaster_id: The ID of the broadcaster that owns the series.
        :param feed_link_id: The feed link to be deleted.
        :return:  Boolean indicating success.
        """
        path = join_url_path(
            "node", "broadcasters", broadcaster_id, "series", id_or_current_title, "podcast_link", str(feed_link_id)
        )
        return cls.delete(path, parse_func=check_response_code_or_throw, **kwargs)

    @classmethod
    def rename_series(cls, id_or_current_title: str, new_title: str, broadcaster_id: str) -> bool:  # pragma: no cover
        """Renames a series.

        If the new series name already exists, all sermons from the
        original series will be merged in.

        :param id_or_current_title: The ID or current title of the series.
        :param new_title: The new title for the series.
        :param broadcaster_id: The ID of the broadcaster that owns the series.
        :return: Boolean indicating success.
        """
        path = join_url_path("node", "broadcasters", broadcaster_id, "series", id_or_current_title)
        return cls.patch(path, data={"new_series_name": new_title}, parse_func=check_response_code_or_throw)

    @classmethod
    def delete_series(cls, id_or_title: str, broadcaster_id: str) -> bool:  # pragma: no cover
        """Deletes a series.

        Deleting a series does not delete the sermons in the series.

        :param id_or_title: The ID or title of the series to delete.
        :param broadcaster_id: The ID of the broadcaster that owns the series.
        :return:  Boolean indicating success.
        """
        path = join_url_path("node", "broadcasters", broadcaster_id, "series", id_or_title)
        return cls.delete(path, parse_func=check_response_code_or_throw)

    #
    # Podcasting
    #
    @classmethod
    def set_podcast_description(
        cls, broadcaster_id: str, description: str = None, **kwargs
    ) -> bool:  # pragma: no cover
        """Set a broadcaster's podcast description.

        If you set the description to None, you will clear it and resume
        using the default description. All feeds must have a title, so
        the description can't be disabled.

        :param description: Text of description or None to use default.
        :param broadcaster_id: The ID of the broadcaster to disable or enable.
        :return: Boolean indicating success.
        """
        path = join_url_path("node", "broadcasters", broadcaster_id)
        return cls.patch(
            path, json={"podcastDescription": description}, parse_func=check_response_code_or_throw, **kwargs
        )

    @classmethod
    def set_podcast_feed_visibility(
        cls, broadcaster_id: str, disabled: bool = True, **kwargs
    ) -> bool:  # pragma: no cover
        """Set a broadcaster's podcast feed visibility.

        Most broadcasters will want their RSS feeds enabled, but for the
        ones who don't, all RSS feeds for a broadcaster can be
        disabled. Note that RSS links are generated automatically by the
        API (regarless of this setting). They will return 404 not found.

        :param disabled: If true, all RSS feeds will be disabled.
        :param broadcaster_id: The ID of the broadcaster to disable or enable.
        :return: Boolean indicating success.
        """
        path = join_url_path("node", "broadcasters", broadcaster_id)
        return cls.patch(path, data={"disablePodcast": disabled}, parse_func=check_response_code_or_throw, **kwargs)

    @classmethod
    def include_email_in_podcast_feed(
        cls, broadcaster_id: str, included: bool = True, **kwargs
    ) -> bool:  # pragma: no cover
        """Include an e-mail address in the main RSS feed.

        This functionality is provided for broadcasters who need their
        e-mail address included in fields during feed validation at a
        podcasting service, but who do not want the address included
        permanently in the RSS feed.

        The address included is the broadcaster's public e-mail address.

        :param broadcaster_id: The ID of the broadcaster.
        :param included: If true, the broadcaster's public e-mail will be included in the main RSS feed,
        :return: Boolean indicating success.
        """
        path = join_url_path("node", "broadcasters", broadcaster_id)
        return cls.patch(
            path, data={"includeEmailInPodcast": included}, parse_func=check_response_code_or_throw, **kwargs
        )

    #
    # Welcome video
    #
    @classmethod
    def set_welcome_video(cls, sermon_id: Optional[str], broadcaster_id: str) -> bool:  # pragma: no cover
        """Sets the welcome video for a broadcaster.

        The welcome video is the video you see on your SermonAudio home
        page, and typically has information about your church or
        organization. The sermon_id of this video is available in the
        welcome_video field of the Broadcaster object.

        :param sermon_id: The sermon to use as the welcome video,
        which must have video available. Clear the setting by passing None.
        :param broadcaster_id: The ID of the broadcaster that owns the sermon.
        :return:  Boolean indicating success.
        """
        path = join_url_path("node", "broadcasters", broadcaster_id)
        return cls.patch(path, json={"welcomeVideoID": sermon_id}, parse_func=check_response_code_or_throw)

    #
    # Highlighted Sermons
    #
    @classmethod
    def set_highlighted_audio_sermon(
        cls,
        broadcaster_id: str,
        audio_type: models.HighlightedAudioInputTypes,
        sermon_id: Optional[str] = None,
        event_type: Optional[models.SermonEventType] = None,
    ) -> bool:  # pragma: no cover
        """Sets the highlighted audio sermon for a broadcaster.

        Each broadcaster can highlight a sermon on their home page for
        visitors to see first. The sermon can be a specific sermon_id,
        the most recent sermon in a specific event type, or one of the
        other HighlightedAudioInputTypes values.

        See the HighlightedAudioInputTypes enum for more documentation
        on the audio types you can set. If you use SERMON_ID or
        EVENT_TYPE, you must supply a corresponding sermon_id or
        event_type parameter.

        :param broadcaster_id: The ID of the broadcaster to update.
        :param audio_type: The type of audio highlighted sermon.
        :param sermon_id: Must be supplied with audio_type SERMON_ID.
        :param event_type: Must be supplied with audio_type EVENT_TYPE.
        :return:  Boolean indicating success.
        """
        if sermon_id is not None and event_type is not None:
            raise BroadcasterAPIError("Supply only one of sermon_id or event_type.")

        if audio_type is models.HighlightedAudioInputTypes.SERMON_ID and sermon_id is None:
            raise BroadcasterAPIError("No sermon_id supplied.")

        if audio_type is models.HighlightedAudioInputTypes.EVENT_TYPE and event_type is None:
            raise BroadcasterAPIError("No event_type supplied.")

        path = join_url_path("node", "broadcasters", broadcaster_id, "highlighted_sermons")

        params = {"audioType": audio_type.value}

        if sermon_id:
            params["audioSermonID"] = sermon_id

        if event_type:
            params["audioEventType"] = event_type.value

        return cls.patch(path, data=params, parse_func=check_response_code_or_throw)

    @classmethod
    def set_highlighted_sort_order(
        cls,
        broadcaster_id: str,
        sort_order: models.HighlightedSortOrders,
    ) -> bool:  # pragma: no cover
        """Sets a broadcaster's highlighted sort order.

        Broadcasters have a short list of sermons on their home page,
        and this sort order controls how they are sorted. See the
        HighlightedSortOrders enum for more details.

        :param broadcaster_id: The ID of the broadcaster to update.
        :param sort_order: The new sort order.
        :return: Boolean indicating success.
        """
        path = join_url_path("node", "broadcasters", broadcaster_id, "highlighted_sermons")
        return cls.patch(path, data={"sortOrder": sort_order.value}, parse_func=check_response_code_or_throw)
