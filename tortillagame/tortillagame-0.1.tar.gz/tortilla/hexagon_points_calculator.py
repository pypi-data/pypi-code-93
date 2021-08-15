import math
from tortilla.coordinate_converter import CoordinateConverter


class HexagonPointsCalculator:
    def __init__(self):
        pass

    @staticmethod
    def calculate_hexes_points(hexes, hex_size, field_offset):
        # hexes_centers = []
        hexes_corners = []
        for row in hexes:
            for hexagon in row:
                hexes_corners.append(HexagonPointsCalculator.calculate_hex_points(hexagon, hex_size, field_offset))

        return hexes_corners

    @staticmethod
    def calculate_hex_points(axial_coordinates, hex_size, field_offset):
        hex_corners = []
        hex_center = CoordinateConverter.axial_to_pixel(axial_coordinates, hex_size)
        hex_center = hex_center[0] + field_offset[0], hex_center[1] + field_offset[1]
        for i in range(6):
            hex_corners.append(HexagonPointsCalculator.calculate_hex_corner(hex_center, i, hex_size))
        hex_corners = tuple(hex_corners)
        hex_center = round(hex_center[0]), round(hex_center[1])
        return hex_center, hex_corners

    @staticmethod
    def calculate_hex_corner(center, i, hex_size):
        angle_deg = 60 * i - 30
        angle_rad = math.pi / 180 * angle_deg
        x = round(center[0] + hex_size * math.cos(angle_rad))
        y = round(center[1] + hex_size * math.sin(angle_rad))
        return x, y
