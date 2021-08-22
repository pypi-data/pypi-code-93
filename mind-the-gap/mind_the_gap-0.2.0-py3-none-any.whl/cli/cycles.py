from typing import List

import typer

from tfl.api import bike_point
from tfl.api.presentation.entities.place import Place

app = typer.Typer()


def print_places(places: List[Place]):
    for place in places:
        print(place.commonName)


@app.command()
def radius(lat: float, lon: float, radius: int = 200) -> None:
    places = bike_point.by_radius(lat, lon, radius)
    print_places(places.places)


@app.command()
def search(query: str):
    places = bike_point.search(query)
    print_places(places)
