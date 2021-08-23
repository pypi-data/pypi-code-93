from click.testing import CliRunner
from clims.cli.convert_coordinates import real2frac, frac2real
from ase.build import bulk
from ase.io import write
from test.file_comparison import compare_files


GaAs = bulk("GaAs", crystalstructure="zincblende", a=5.65315)

def test_real2frac():
    runner = CliRunner()
    with runner.isolated_filesystem():
        write("geometry.in", GaAs, scaled=False)
        result = runner.invoke(real2frac)
        with open("geometry.out_ref",'w') as f:
            f.write(frac_coordinates)
        compare_files("geometry.out","geometry.out_ref")
        
def test_frac2real():
    runner = CliRunner()
    with runner.isolated_filesystem():
        write("geometry.in", GaAs, scaled=True)
        result = runner.invoke(frac2real)
        with open("geometry.out_ref",'w') as f:
            f.write(real_coords)
        compare_files("geometry.out","geometry.out_ref")


real_coords = """#=======================================================
# FHI-aims file: geometry.in
# Created using the Atomic Simulation Environment (ASE)
# Fri Apr 23 15:44:29 2021
#=======================================================
lattice_vector 0.0000000000000000 2.8265750000000001 2.8265750000000001
lattice_vector 2.8265750000000001 0.0000000000000000 2.8265750000000001
lattice_vector 2.8265750000000001 2.8265750000000001 0.0000000000000000
atom 0.0000000000000000 0.0000000000000000 0.0000000000000000 Ga
atom 1.4132874999999998 1.4132874999999998 1.4132875000000000 As
"""
frac_coordinates = """#=======================================================
# FHI-aims file: geometry.in
# Created using the Atomic Simulation Environment (ASE)
# Fri Apr 23 16:46:57 2021
#=======================================================
lattice_vector 0.0000000000000000 2.8265750000000001 2.8265750000000001
lattice_vector 2.8265750000000001 0.0000000000000000 2.8265750000000001
lattice_vector 2.8265750000000001 2.8265750000000001 0.0000000000000000
atom_frac 0.0000000000000000 0.0000000000000000 -0.0000000000000000 Ga
atom_frac 0.2500000000000000 0.2500000000000000 0.2499999999999999 As
"""
