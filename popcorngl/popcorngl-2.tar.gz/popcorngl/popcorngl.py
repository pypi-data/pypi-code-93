from operator import itemgetter
from math import sin, cos, sqrt
from copy import deepcopy


def multiply_matrix(a, b):
    rowsA = len(a)
    colsA = len(a[0])
    rowsB = len(b)
    colsB = len(b[0])

    c = [[0 for row in range(colsB)] for col in range(rowsA)]

    for x in range(rowsA):
        for y in range(colsB):
            for z in range(colsA):
                c[x][y] += a[x][z] * b[z][y]

    return c

# WORK IN PROGRESS
'''def load_obj(file):
    try:
        content = open(file, 'r').read()
    except TypeError:
        print("An error has occured.")
        exit()
    content_lines = content.split('\n')
    verticies = []
    faces = []

    for line in content_lines:
        if line.startswith('f '):
            line = line.split(' ')
            line.pop(0)
            line_list = []
            for index, face in enumerate(line):
                if face == '':
                    line.remove(face)
                else:
                    face = face.replace('//', '/')
                    line[index] = list(map(int, face.split('/')))[0] - 1
                    line_list.append(line[index])

            faces.append(line_list)

        elif line.startswith('v '):
            line = line.replace('  ', ' ')
            line = line.split(' ')
            line.pop(0)
            line = list(map(float, line))
            for index, item in enumerate(line):
                line[index] = [item]
            verticies.append(line)

    return (verticies, faces)'''

def in_range(position_1, position_2, radius):
    if position_1[0][0] > position_2[0][0] - radius and position_1[0][0] < position_2[0][0] + radius:
        if position_1[1][0] > position_2[1][0] - radius and position_1[1][0] < position_2[1][0] + radius:
            if position_1[2][0] > position_2[2][0] - radius and position_1[2][0] < position_2[2][0] + radius:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


class Light():
    def __init__(self, position, radius, intensity):
        self.position = position
        self.radius = radius
        self.intensity = intensity

class Camera():
    def __init__(self, x_rotation, y_rotation, z_rotation, fov, center, distance):
        self.x_rotation = x_rotation
        self.y_rotation = y_rotation
        self.z_rotation = z_rotation

        self.fov = fov
        self.center = center
        self.distance = distance


    def rotate_x(self, amount):
        self.x_rotation += amount
    
    def rotate_y(self, amount):
        self.y_rotation += amount

    def rotate_z(self, amount):
        self.z_rotation += amount

    def change_distance(self, amount):
        self.distance += amount

class Engine():
    def __init__(self):
        self.pointsZ = []

    def do_3d_math(self, points, camera):
        rotation_x_matrix = [[1, 0, 0], [0, cos(camera.x_rotation), -sin(camera.x_rotation)], [0, sin(camera.x_rotation), cos(camera.x_rotation)]]
        rotation_y_matrix = [[cos(camera.y_rotation), 0, -sin(camera.y_rotation)], [0, 1, 0], [sin(camera.y_rotation), 0, cos(camera.y_rotation)]]
        rotation_z_matrix = [[cos(camera.z_rotation), -sin(camera.z_rotation), 0], [sin(camera.z_rotation), cos(camera.z_rotation), 0], [0, 0, 1]]

        return_list = [p for p in range(len(points))]
        self.pointsZ = [0 for p in range(len(points))]
        for index, point in enumerate(points):
            rotated = multiply_matrix(rotation_x_matrix, point)
            rotated = multiply_matrix(rotation_y_matrix, rotated)
            rotated = multiply_matrix(rotation_z_matrix, rotated)
            if camera.distance != 0:
                z = 1/(camera.distance - rotated[2][0])
            else:
                z = 0
            projection = [[z, 0, 0], [0, z, 0]]

            projected = multiply_matrix(projection, rotated)

            x = projected[0][0] * camera.fov + camera.center[0]
            y = projected[1][0] * camera.fov + camera.center[1]

            return_list[index] = [x, y]

            self.pointsZ[index] = z

        return return_list

    def do_light_math(self, faces, points, light):
        new_faces = deepcopy(faces)
        for index, face in enumerate(new_faces):
            face_point_list = []
            for point in face:
                if type(point) == int:
                    face_point_list.append(points[point])

            x_list = []
            y_list = []
            z_list = []

            for point in face_point_list:
                x_list.append(point[0][0])
                y_list.append(point[1][0])
                z_list.append(point[2][0])

            if len(x_list) == 4:
                face_point_average = [[(x_list[0] + x_list[1] + x_list[2] + x_list[3]) / 4], [(y_list[0] + y_list[1] + y_list[2] + y_list[3]) / 4], [(z_list[0] + z_list[1] + z_list[2] + z_list[3]) / 4]]
            elif len(x_list) == 3:
                face_point_average = [[(x_list[0] + x_list[1] + x_list[2]) / 3], [(y_list[0] + y_list[1] + y_list[2]) / 3], [(z_list[0] + z_list[1] + z_list[2]) / 3]]

            change = 0

            if in_range(face_point_average, light.position, light.radius) == True:
                distance_between = sqrt((light.position[0][0] - face_point_average[0][0]) ** 2 + (light.position[1][0] - face_point_average[1][0]) ** 2 + (light.position[2][0] - face_point_average[2][0]) ** 2)
                if distance_between == 0:
                    distance_between = 0.01
                change = round(light.intensity / distance_between)

            if len(x_list) == 4:
                new_faces[index][4] = (face[4][0] + change, face[4][1] + change, face[4][2] + change)
            elif len(x_list) == 3:
                new_faces[index][3] = (face[3][0] + change, face[3][1] + change, face[3][2] + change)

            if len(x_list) == 4:
                temp_list = list(new_faces[index][4])
                if temp_list[0] > 255:
                    temp_list[0] = 255
                elif temp_list[0] < 0:
                    temp_list[0] = 0
                if temp_list[1] > 255:
                    temp_list[1] = 255
                elif temp_list[1] < 0:
                    temp_list[1] = 0
                if temp_list[2] > 255:
                    temp_list[2] = 255
                elif temp_list[2] < 0:
                    temp_list[2] = 0
                new_faces[index][4] = tuple(temp_list)
            elif len(x_list) == 3:
                temp_list = list(new_faces[index][3])
                if temp_list[0] > 255:
                    temp_list[0] = 255
                elif temp_list[0] < 0:
                    temp_list[0] = 0
                if temp_list[1] > 255:
                    temp_list[1] = 255
                elif temp_list[1] < 0:
                    temp_list[1] = 0
                if temp_list[2] > 255:
                    temp_list[2] = 255
                elif temp_list[2] < 0:
                    temp_list[2] = 0
                new_faces[index][3] = tuple(temp_list)
                
        return new_faces

    def sort_faces(self, faces):
        return_list = deepcopy(faces)
        for face in return_list:
            faceZ = []
            for value in face:
                if isinstance(value, int) == True:
                    faceZ.append(self.pointsZ[value])

            face.append(faceZ)

            if len(face) == 6:
                face.append(sum([face[5][0], face[5][1], face[5][2], face[5][3]]) / 4)
            elif len(face) == 5:
                face.append("placeholder")
                face.append(sum([face[4][0], face[4][1], face[4][2]]) / 3)

        return_list.sort(key=itemgetter(6))

        for face in return_list:
            if "placeholder" in face:
                face.remove("placeholder")

            face.pop()
            face.pop()

        return return_list
