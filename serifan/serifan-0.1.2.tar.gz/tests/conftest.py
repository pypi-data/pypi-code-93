import datetime

import pytest


@pytest.fixture(scope="session")
def comic_list_response():
    return {
        "comics": [
            {
                "publisher": "IMAGE COMICS",
                "description": '"LEGACY," Part Five-The third arc of the Eisner Award-winning BITTER ROOT comes to an epic conclusion that will decide the fate of humanity. For the Sangerye family, it means making another sacrifice while searching for hope during hopeless times.',
                "title": "BITTER ROOT #15 CVR A GREENE (MR)",
                "price": "$3.99",
                "creators": "(W) David Walker, Chuck Brown (A/CA) Sanford Greene",
                "release_date": "2021-08-11",
                "diamond_id": "MAY210139",
            },
            {
                "publisher": "IMAGE COMICS",
                "description": '"LEGACY," Part Five-The third arc of the Eisner Award-winning BITTER ROOT comes to an epic conclusion that will decide the fate of humanity. For the Sangerye family, it means making another sacrifice while searching for hope during hopeless times.',
                "title": "BITTER ROOT #15 CVR B CONLEY CURIEL (MR)",
                "price": "$3.99",
                "creators": "(W) David Walker, Chuck Brown (A) Sanford Greene (CA) Chase Conley, Charissa Curiel",
                "release_date": "2021-08-11",
                "diamond_id": "MAY210140",
            },
        ]
    }


@pytest.fixture(scope="session")
def sb_dates_response():
    return {
        "dates": [
            "2021-07-29.",
            "2021-08-04",
            "2021-08-11",
            "2021-08-18",
            "2021-08-25",
        ]
    }


@pytest.fixture(scope="session")
def sb_cleaned_dates():
    return [
        datetime.date(2021, 8, 4),
        datetime.date(2021, 8, 11),
        datetime.date(2021, 8, 18),
        datetime.date(2021, 8, 25),
    ]
