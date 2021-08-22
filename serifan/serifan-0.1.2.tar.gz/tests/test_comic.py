import datetime

import pytest
from serifan import api, comics_list, exceptions, session, utils


def test_comics_list(comic_list_response):
    res = comics_list.ComicsList(comic_list_response)
    comic_iter = iter(res)
    assert next(comic_iter).title == "BITTER ROOT #15 CVR A GREENE (MR)"
    assert next(comic_iter).title == "BITTER ROOT #15 CVR B CONLEY CURIEL (MR)"
    assert len(res) == 2
    assert res[0].publisher == "IMAGE COMICS"
    assert res[1].title == "BITTER ROOT #15 CVR B CONLEY CURIEL (MR)"
    assert res[1].price == "$3.99"
    assert res[1].release_date == datetime.date(2021, 8, 11)
    assert res[1].diamond_id == "MAY210140"


def test_available_dates(sb_dates_response, mocker):
    mocker.patch.object(session.Session, "call", return_value=sb_dates_response)
    sb = api()
    result = sb.available_release_dates()
    assert len(result) == 5
    assert result[0] == datetime.date(2021, 7, 29)


def test_new_releases(comic_list_response, mocker):
    mocker.patch.object(session.Session, "call", return_value=comic_list_response)
    sb = api()
    result = sb.new_releases()
    assert len(result) == 2
    assert result[0].title == "BITTER ROOT #15 CVR A GREENE (MR)"


def test_previous_releases(comic_list_response, mocker):
    mocker.patch.object(session.Session, "call", return_value=comic_list_response)
    sb = api()
    result = sb.previous_releases()
    assert len(result) == 2
    assert result[0].title == "BITTER ROOT #15 CVR A GREENE (MR)"


def test_future_releases(comic_list_response, mocker):
    mocker.patch.object(session.Session, "call", return_value=comic_list_response)
    sb = api()
    result = sb.future_releases()
    assert len(result) == 2
    assert result[0].title == "BITTER ROOT #15 CVR A GREENE (MR)"


def test_query(comic_list_response, mocker):
    mocker.patch.object(session.Session, "call", return_value=comic_list_response)
    sb = api()
    result = sb.query("Image", "WildC.A.T.S.", None, None)
    assert len(result) == 2
    assert result[0].title == "BITTER ROOT #15 CVR A GREENE (MR)"


def test_bad_response():
    with pytest.raises(exceptions.ApiError):
        comics_list.ComicsList({"comics": {"name": 1}})


def test_list_string_to_date(sb_dates_response):
    results = utils.list_strings_to_dates(sb_dates_response)
    assert len(results) == 5
    assert results[0] == datetime.date(2021, 7, 29)
