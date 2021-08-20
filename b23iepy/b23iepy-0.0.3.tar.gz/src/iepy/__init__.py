import json
import datetime
import typing
from typing import Type
import os
import time

try:
    import tweepy
except ImportError:
    pass

__version__ = "0.0.3"
__title__ = 'iepy'
__author__ = 'Bertik23'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021 Bertik23'


class Date(datetime.date):
    """Concrete date type.

    **Constructors**

    __new__()
    fromtimestamp()
    today()
    fromordinal()
    cast()

    **Operators**

    __repr__, __str__
    __eq__, __le__, __lt__, __ge__, __gt__, __hash__
    __add__, __radd__, __sub__ (add/radd only with timedelta arg)

    **Methods**

    timetuple()
    toordinal()
    weekday()
    isoweekday(), isocalendar(), isoformat()
    ctime()
    strftime()

    **Properties (readonly)**

    month, day
    """
    def __new__(self, month, day):
        """Constructor.

        Parameters
        ----------
        month: :class:`int`
            The month
        day: :class:`int`
            The day
        """
        return super().__new__(self, 2020, month, day)

    @classmethod
    def fromtimestamp(self, t):
        y, m, d, hh, mm, ss, weekday, jday, dst = time.localtime(t)
        return self(m, d)

    @classmethod
    def fromisoformat(self, date_string: str):
        a = datetime.datetime.fromisoformat("2020-"+date_string)
        return self.cast(a)

    @classmethod
    def cast(self, other):
        """Constructor to make this class from other datatypes"""
        if type(other) in [datetime.date, datetime.datetime, Date]:
            return Date(other.month, other.day)
        if type(other) is str:
            return Date.fromisoformat(other)

    def isoformat(self):
        return super().isoformat().split("-", 1)[1]


class Event:
    """Event class, for events that happened

    Attributes
    ----------

    date: Union[:class:`datetime.date`, :class:`datetime.datetime`, :class:`Date`]
        The date of the event (day, month)
    year: :class:`int`
        The year when the event happened.
    language: :class:`str`
        The language of the summary and description.
    summary: :class:`str`
        A short summary of the event.
    description: Optional[:class:`str`]
        A optional longer description of the event.
    """
    def __init__(self, date, year, language, summary, description=""):
        self.date = Date.cast(date)
        self.year = year
        self.language = language
        self.summary = summary
        self.description = description

    @classmethod
    def fromJson(self, date, jsonData):
        for lang in jsonData["data"]:
            yield Event(
                date,
                jsonData["year"],
                lang,
                jsonData["data"][lang]["summary"],
                jsonData["data"][lang]["description"]
            )

    def __str__(self):
        return f"Event({self.year}-{self.date.isoformat()})"

    def __repr__(self):
        return str(self)


dateType = typing.Union[datetime.date, datetime.datetime, Date]

with open(os.path.dirname(__file__)+"/data.json", "r", encoding="utf-8") as f:
    data: dict = json.load(f)


def getEvents(date: Type[dateType]):
    """Gets event that happend on ``date``

    :param date: Date of the event, only the day and month are used.
    :type date: Union[:class:`datetime.date`, :class:`datetime.datetime`, :class:`Date`]
    """
    date = Date.cast(date)
    dateIso = date.isoformat()
    if dateIso in data:
        out: list = list(list(Event.fromJson(date, i)) for i in data[dateIso])
        return out
    return []


def getTodayEvents():
    """Gets events that happend today."""
    return getEvents(datetime.date.today())


def tweetEvent(
    event: Event,
    consumerKey: str,
    consumerSecret: str,
    accessToken: str = None,
    accessTokenSecret: str = None
):
    """Tweets the given event

    Parameters
    ----------
    event: :class:`Event`
        Event to be tweeted.
    consumerKey: :class:`str`
        Consumer key of your Twitter app
    consumerSecret: :class:`str`
        Consumer secret of your Twitter app
    accessToken: Optional[:class:`str`]
        Access token for the user you want to tweet
    accessTokenSecret: Optional[:class:`str`]
        Access token secret for the user you want to tweet


    .. note ::
        If ``accessToken`` or ``accessTokenSecret`` is not supplied you will
        be promted with a link to go too and then enter a verifier.
    """
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(
        consumerKey,
        consumerSecret,
        callback="oob"
    )
    if accessToken is None or accessTokenSecret is None:
        print("Go to: " + auth.get_authorization_url())
        verifier = input('Verifier:')
        auth.get_access_token(verifier)
        print(
            "This is your access token: ",
            auth.access_token,
            "\nThis is your access token secret: ",
            auth.access_token_secret,
            "\nSave them for further use"
            )
    auth.set_access_token(
        accessToken if accessToken is not None else auth.access_token,
        accessTokenSecret if (
            accessTokenSecret is not None
        ) else auth.access_token_secret
    )

    # Create API object
    api = tweepy.API(auth)

    # Create a tweet
    if event.description != "":
        api.update_status(event.description)
    else:
        api.update_status(event.summary)
