"""This module provide geometry functionality utils"""
from shapely.geometry import Polygon


def get_polygon_area(coordinates):
    """
    This method calculate area
    :param coordinates: list of points represented as list [x.y]
    :return: float in meters
    """
    polygon = process_polygon(coordinates)
    area = polygon.area
    return area


def get_polygon_perimeter(coordinates):
    """
    This method calculate perimeter
    :param coordinates: list of points represented as list [x.y]
    :return: float in meters
    """
    polygon = process_polygon(coordinates)
    perimeter = polygon.length
    return perimeter


def process_polygon(coordinates):
    """Pass list of co-ordinates to Shapely Polygon function and get polygon object"""

    return Polygon(coordinates)

