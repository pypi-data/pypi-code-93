"""Test suite for base.py"""
from datetime import date

from sqlalchemy.orm import Session  # type: ignore

from schema import DatabaseDateTest, DatabaseDatetimeTest


def test_get_dates_to_process(test_class):
    """Test get_dates_to_process"""

    # Test with datetime
    dates = test_class.get_dates_to_process(date(2021, 5, 1), date(2021, 5, 4),
                                            DatabaseDatetimeTest.datetime, force=False)
    assert len(dates) == 0

    dates = test_class.get_dates_to_process(date(2021, 5, 1), date(2021, 5, 4),
                                            DatabaseDatetimeTest.datetime, force=True)
    assert len(dates) == 4

    # Test with date
    dates = test_class.get_dates_to_process(date(2021, 5, 1), date(2021, 5, 4),
                                            DatabaseDateTest.date, force=False)
    assert len(dates) == 0

    dates = test_class.get_dates_to_process(date(2021, 5, 1), date(2021, 5, 4),
                                            DatabaseDateTest.date, force=True)
    assert len(dates) == 4


def test_insert_or_update(test_class):
    """Tests _insert_or_update"""
    with Session(bind=test_class.engine) as session:
        # make sure we only have the four entries from the test setup
        ret = session.query(DatabaseDateTest.primary_key)
        assert ret.count() == 4
        keys = [x[0] for x in ret.all()]
        keys.sort()
        assert [1, 2, 3, 4] == keys

        # add elements that require an update
        test_class._insert_or_update(
            DatabaseDateTest(
                date=date(2021, 5, 1),
                primary_key=1))
        test_class._insert_or_update(DatabaseDateTest(
            date=date(2021, 5, 2),
            primary_key=2))
        test_class._insert_or_update(DatabaseDateTest(
            date=date(2021, 5, 3),
            primary_key=3))
        test_class._insert_or_update(DatabaseDateTest(
            date=date(2021, 5, 4),
            primary_key=4))

    assert ret.count() == 4
    keys = [x[0] for x in ret.all()]
    keys.sort()
    assert [1, 2, 3, 4] == keys

    # add new elements
    test_class._insert_or_update(DatabaseDateTest(
        date=date(2021, 5, 1),
        primary_key=5))

    test_class._insert_or_update(DatabaseDateTest(
        date=date(2021, 5, 2),
        primary_key=6))
    test_class._insert_or_update(DatabaseDateTest(
        date=date(2021, 5, 3),
        primary_key=7))
    test_class._insert_or_update(DatabaseDateTest(
        date=date(2021, 5, 4),
        primary_key=8))
    assert ret.count() == 8
    keys = [x[0] for x in ret.all()]
    keys.sort()
    assert [1, 2, 3, 4, 5, 6, 7, 8] == keys
