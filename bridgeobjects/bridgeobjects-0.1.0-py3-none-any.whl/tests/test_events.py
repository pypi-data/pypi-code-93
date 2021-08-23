"""A set of tests for the bridgeobjects Event class."""
import datetime
import pytest

from ..source.event import Event


def test_event_instantiate_no_parameters():
    """Ensure that a event is created correctly: no parameters."""
    event = Event()
    assert event.name == ""
    now = datetime.datetime.now()
    assert event.date == datetime.date(now.year, now.month, now.day)
    assert event.time == datetime.time(now.hour, now.minute)


def test_event_instantiate_name_only():
    """Ensure that a event is created correctly: name only."""
    event = Event("abc")
    assert event.name == "abc"
    now = datetime.datetime.now()
    assert event.date == datetime.date(now.year, now.month, now.day)
    assert event.time == datetime.time(now.hour, now.minute)


def test_event_instantiate_date_only():
    """Ensure that a event is created correctly: date_only."""
    event = Event(date_time=datetime.datetime(2001, 1, 31))
    assert event.date.year == 2001
    assert event.time.hour == 0


def test_event_instantiate_date_and_time():
    """Ensure that a event is created correctly: date and time."""
    event = Event(date_time=datetime.datetime(2012, 3, 1, 17, 30))
    assert event.date.day == 1
    assert event.time.hour == 17
    assert event.time.minute == 30


def test_event_instantiate_date_and_time_invalid():
    """Ensure that a event is created correctly: date and time."""
    with pytest.raises(TypeError) as exec_info:
        event = Event(date_time="28/02/1982")


def test_event_set_date():
    """Ensure that a date is set correctly"""
    event = Event()
    event.date = datetime.datetime(2012, 8, 19)
    assert event.date.day == 19
    assert event.date.month == 8
    assert event.date.year == 2012


def test_event_repr():
    """"Ensure the repr string is correct."""
    event = Event("abc")
    assert repr(event) == "Event('abc')"


def test_event_str():
    """"Ensure the str string is correct."""
    event = Event("abc")
    event.date = datetime.datetime(2012, 8, 19)
    assert str(event) == "Event. Description: abc, date: 19 Aug 2012."
