import itertools
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from scipy.spatial import Voronoi


def draw_bound_box(ax, Z):
    # Work around to do axis 'equal'
    max_range = np.amax(np.amax(Z, axis=0) - np.amin(Z, axis=0)) * 1.1
    print(np.amax(Z, axis=0) - np.amin(Z, axis=0))
    center = (np.amax(Z, axis=0) + np.amin(Z, axis=0)) * 0.5
    # print(center)
    # print(max_range)
    box = max_range * np.array(list(itertools.product([0, 1], repeat=3)))
    box -= max_range * 0.5 + center
    # Comment or uncomment following both lines to test the fake bounding box:
    for xb, yb, zb in zip(*box.T):
        ax.plot([xb], [yb], [zb], "w")


def draw_unit_cell(ax, cell):
    uc_corners = np.array(list(itertools.product([0, 1], repeat=3)))
    Z = np.dot(uc_corners, cell)
    verts = [
        [Z[0], Z[1], Z[3], Z[2]],
        [Z[0], Z[1], Z[5], Z[4]],
        [Z[0], Z[2], Z[6], Z[4]],
        [Z[2], Z[3], Z[7], Z[6]],
        [Z[1], Z[3], Z[7], Z[5]],
        [Z[4], Z[5], Z[7], Z[6]],
    ]

    ax.add_collection3d(
        Poly3DCollection(
            verts, facecolors="red", linewidths=1, edgecolors="r", alpha=0.25
        )
    )


def calculate_ws_vertices_from_cell(cell, points):
    """Calculates the Brillouin Zone vertices and path of high-symmetry points.

    Parameters:

    cell: numpy array
        Three lattice vectors arranged as [[lat_v1],[lat_v2],[lat_v3]]
    """

    vor = Voronoi(points)
    bz_vertices = []
    for r in vor.ridge_dict:
        # This is not the general solution. It might happen that for very skewed cells
        # that next-next-nearest neighbors are building the faces of the BZ.
        if r[0] == 62 or r[1] == 62:
            bz_vertices.append([list(vor.vertices[i]) for i in vor.ridge_dict[r]])

    return bz_vertices


def get_equation_of_plane(vertex_list):
    p = np.array(vertex_list)
    n = np.cross(p[1] - p[0], p[2] - p[0])
    n = n / np.linalg.norm(n)
    d = -np.dot(p[0], n)
    return np.array([*n, d])


def get_face_center(p):
    return np.array(p).sum(axis=0) / 4


def plot_plane_normal(abcd, onpoint, ax):
    n = abcd[:3]
    ax.quiver(*onpoint, *n, length=5, normalize=True)


def get_shortest_vector_to_plane(plane, point):
    k = (np.dot(plane[:3], point) + plane[3]) / np.linalg.norm(plane[:3]) ** 2.0
    c_point = point - k * plane[:3]
    d_vec = -c_point + point
    # ax.quiver(*c_point, *d_vec)
    # ax.quiver(*c_point, *plane[:3])
    return d_vec


def check_if_point_in_polyhedron(point, planes):
    is_in = []
    # print(len(planes))
    for plane in planes:
        d_vec = get_shortest_vector_to_plane(plane, point)
        if np.linalg.norm(d_vec) < 1e-8:
            is_in.append(True)
        else:
            unit_d_vec = d_vec / np.linalg.norm(d_vec)
            # print(np.linalg.norm(-plane[:3] - unit_d_vec),d_vec)
            if np.linalg.norm(-plane[:3] - unit_d_vec) < 1e-8:
                is_in.append(True)
            else:
                # print('No',plane[:3] - unit_d_vec)
                assert np.linalg.norm(plane[:3] - unit_d_vec) < 1e-8
                is_in.append(False)
    return all(is_in)


def move_atom_in_ws(pos, planes, points):
    for p in points:
        new_pos = pos + p
        # print("Suggest new position:",new_pos, pos, p)
        is_in = check_if_point_in_polyhedron(new_pos, planes)
        if is_in:
            # print('New position found')
            return new_pos
    raise


def get_ws_planes(ws_vertices):
    planes = []
    for vertex in ws_vertices:
        abcd = get_equation_of_plane(vertex)
        onpoint = get_face_center(vertex)
        # print(np.linalg.norm(abcd[:3] - onpoint/np.linalg.norm(onpoint)))
        if not np.linalg.norm(abcd[:3] - onpoint / np.linalg.norm(onpoint)) < 1e-8:
            abcd *= -1.0
        # print(np.linalg.norm(abcd[:3] - onpoint/np.linalg.norm(onpoint)))
        assert np.linalg.norm(abcd[:3] - onpoint / np.linalg.norm(onpoint)) < 1e-8
        planes.append(abcd)
        # plot_plane_normal(abcd,onpoint,ax)
    return planes


def create_ws_cell(structure):
    cell = structure.get_cell()[:]
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    corners = np.array(list(itertools.product([-2.0, -1.0, 0.0, 1.0, 2.0], repeat=3)))
    points = np.dot(corners, cell)

    # draw_unit_cell(ax,cell)
    ws_vertices = calculate_ws_vertices_from_cell(cell, points)

    # ax.add_collection3d(Poly3DCollection(
    #    ws_vertices, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25)
    # )

    planes = get_ws_planes(ws_vertices)

    for i, pos in enumerate(structure.get_positions()):
        # print('--Atom', i, pos)
        is_in = check_if_point_in_polyhedron(pos, planes)
        # print(is_in)
        if not is_in:
            new_pos = move_atom_in_ws(pos, planes, points)
            structure[i].position = new_pos

    # ax.scatter3D(*crystal.get_positions().T)
    # draw_bound_box(ax,points)

    # plt.show()
