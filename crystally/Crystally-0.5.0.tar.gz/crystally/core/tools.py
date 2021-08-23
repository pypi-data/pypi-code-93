from .lattice import *


def grid_atoms(lattice, grid_step):
    def to_grid(lattice, position, round_func):
        position = lattice.vectors @ position
        return tuple(int(x) for x in round_func(np.round(position / grid_step, 10)))

    grid_size = to_grid(lattice, np.array([1, 1, 1]), np.ceil)

    grid = [[[[] for _ in range(grid_size[2])]
             for _ in range(grid_size[1])]
            for _ in range(grid_size[0])]

    for atom in lattice:
        x, y, z = to_grid(lattice, atom.position, np.floor)
        grid[x][y][z].append(atom)
    return grid