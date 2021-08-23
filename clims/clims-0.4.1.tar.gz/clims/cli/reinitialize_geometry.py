from ase.io import read, write
import click


@click.command()
@click.argument("init_geo_name")
@click.argument("uninit_geo_name")
@click.option("--fileout", default="geometry-reinitialized.in", type=str)
def reinitialize_geometry(init_geo_name, uninit_geo_name, fileout):
    init_geo = read(init_geo_name)
    uninit_geo = read(uninit_geo_name, format="aims")
    assert len(init_geo) == len(uninit_geo)
    initial_moments = init_geo.get_initial_magnetic_moments()
    initial_charges = init_geo.get_initial_charges()
    print("-- Re-initializing with the following initial_moments:")
    print(initial_moments)
    print("-- Re-initializing with the following initial_charges:")
    print(initial_charges)
    uninit_geo.set_initial_magnetic_moments(initial_moments)
    uninit_geo.set_initial_charges(initial_charges)
    write(fileout, uninit_geo)

    restart_geo_footer = """#
# What follows is the current estimated Hessian matrix constructed by the BFGS algorithm.
# This is NOT the true Hessian matrix of the system.
# If you do not want this information here, switch it off using the "hessian_to_restart_geometry" keyword.
#
"""
    restart_geo = ''
    with open(uninit_geo_name) as f:
        lines = f.readlines()
    for line in lines:
        if line.strip().startswith("trust_radius"):
            restart_geo += line
        elif line.strip().startswith("hessian_file"):
            restart_geo += line
    if restart_geo:
        print(f'Appending geometry restart info to {fileout}')
        with open(fileout, "a") as f:
            f.write(restart_geo_footer+restart_geo)
