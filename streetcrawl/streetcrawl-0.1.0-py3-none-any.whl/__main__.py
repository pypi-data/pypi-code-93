import logging
import os
from pathlib import Path
from typing import cast, Tuple

import click
import requests
from geopy import Point
from loguru import logger

from streetcrawl.catalogue import Catalogue, IndexContinuable
from streetcrawl.pano import Pano
from streetcrawl.pano_folder_glued import PanoFolderGlued
from streetcrawl.pano_folder_simple import PanoFolderSimple
from streetcrawl.pano_id import PanoIdClosestTo
from streetcrawl.panos import PanosSimple
from streetcrawl.points_in_square import PointsInSquare
from streetcrawl.saver import Saver


def parsed_centre(p: str) -> Point:
    lat, lng = p.split(",")
    return Point(float(lat), float(lng))


def parsed_resolution(p: str) -> Tuple[int, int]:
    h, w = p.split("x")
    return int(h), int(w)


@click.command()
@click.argument("centre")
@click.argument("output_folder")
@click.option("--glue", is_flag=True, help="Glue together pics of the panoramic view.")
@click.option("--fov", default=90, help="field of view. Defaults to 90 degrees")
@click.option(
    "--square-side",
    default=1500,
    help="Side of the square to be crawler. Defaults to 1500 meters",
)
@click.option("--step", default=10, help="Crawling step in meters. Defaults to 10")
@click.option(
    "--resolution", default="600x600", help="Crawling step in meters. Defaults to 10"
)
def main(
    centre: str,
    output_folder: str,
    glue: bool,
    fov: int,
    square_side: int,
    step: int,
    resolution: str,
):
    api_key = os.environ["STREETVIEW_API_KEY"]
    session = requests.session()
    Catalogue(
        IndexContinuable(
            Path(output_folder),
            Saver(
                fov,
                parsed_resolution(resolution),
                session,
                Path(output_folder),
                PanoFolderSimple if not glue else PanoFolderGlued,
                cast(logging.Logger, logger),
            ),
        ),
        cast(logging.Logger, logger),
    ).add(
        PanosSimple(
            PointsInSquare(
                centre=parsed_centre(centre),
                square_side=square_side,
                step=step,
            ),
            pano_id=lambda coords: PanoIdClosestTo(coords, api_key, session),
            pano=lambda pano_id, location: Pano(pano_id, location, api_key),
        )
    )


if __name__ == "__main__":
    main()
