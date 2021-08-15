import math


class CoordinateConverter:
    @staticmethod
    def axial_to_pixel(axial_coordinates, hex_size, offset=(0, 0)):
        x = hex_size * (math.sqrt(3) * axial_coordinates[0] + math.sqrt(3) / 2 * axial_coordinates[1]) + offset[0]
        y = hex_size * (3 / 2 * axial_coordinates[1]) + offset[1]
        return x, y

    @staticmethod
    def pixel_to_axial(point, hex_size):
        q = (math.sqrt(3) / 3 * point[0] - 1 / 3 * point[1]) / hex_size
        r = (2 / 3 * point[1]) / hex_size
        return CoordinateConverter.axial_round((q, r))

    @staticmethod
    def axial_to_cube(axial_coordinates):
        x = axial_coordinates[0]
        z = axial_coordinates[1]
        y = -x - z
        return x, y, z

    @staticmethod
    def cube_to_axial(cube_coordinates):
        q = cube_coordinates[0]
        r = cube_coordinates[2]
        return q, r

    @staticmethod
    def axial_round(axial_coordinates):
        return CoordinateConverter.cube_to_axial(CoordinateConverter.cube_round(CoordinateConverter.axial_to_cube(axial_coordinates)))

    @staticmethod
    def cube_round(cube_coordinates):
        rx = round(cube_coordinates[0])
        ry = round(cube_coordinates[1])
        rz = round(cube_coordinates[2])

        x_diff = abs(rx - cube_coordinates[0])
        y_diff = abs(ry - cube_coordinates[1])
        z_diff = abs(rz - cube_coordinates[2])

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

        return rx, ry, rz
