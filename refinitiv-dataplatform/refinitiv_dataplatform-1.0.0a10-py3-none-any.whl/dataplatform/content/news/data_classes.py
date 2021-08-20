from refinitiv.dataplatform.legacy.tools import to_datetime
from .urgency import Urgency


class NewsData(object):
    def __init__(
        self,
        title,
        creator,
        source,
        language,
        subject,
        item_codes,
        urgency,
        creation_date,
        update_date,
        raw,
    ):
        self.title = title
        self.creator = creator
        self.source = source
        self.language = language
        self.subject = subject
        self.item_codes = item_codes
        self.urgency = Urgency(urgency)
        self.creation_date = to_datetime(creation_date)
        self.update_date = to_datetime(update_date)
        self.raw = raw


class Headline(NewsData):
    @staticmethod
    def create(datum):
        news_item = datum.get("newsItem")
        content_meta = news_item.get("contentMeta")
        item_meta = news_item.get("itemMeta")
        subject = content_meta.get("subject")
        headline = Headline(
            title=item_meta.get("title")[0].get("$"),
            creator=content_meta.get("creator")[0].get("_qcode"),
            source=content_meta.get("infoSource"),
            language=content_meta.get("language"),
            subject=subject,
            item_codes=[item.get("_qcode") for item in subject],
            urgency=content_meta.get("urgency").get("$"),
            creation_date=item_meta.get("firstCreated").get("$"),
            update_date=item_meta.get("versionCreated").get("$"),
            raw=datum,
        )
        return headline


class Story(NewsData):
    @staticmethod
    def create(datum):
        news_item = datum.get("newsItem")
        content_meta = news_item.get("contentMeta")
        item_meta = news_item.get("itemMeta")
        subject = content_meta.get("subject")
        headline = Headline(
            title=item_meta.get("title")[0].get("$"),
            creator=content_meta.get("creator")[0].get("_qcode"),
            source=content_meta.get("infoSource"),
            language=content_meta.get("language"),
            subject=subject,
            item_codes=[item.get("_qcode") for item in subject],
            urgency=content_meta.get("urgency").get("$"),
            creation_date=item_meta.get("firstCreated").get("$"),
            update_date=item_meta.get("versionCreated").get("$"),
            raw=datum,
        )
        return headline
