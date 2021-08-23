from click.testing import CliRunner
from clims.cli.supercell import supercell
from ase.build import bulk
from ase.io import write, read
import numpy as np


GaAs = bulk("GaAs", crystalstructure="zincblende", a=5.65315)
GaAs_positions_222 = [
    [0.0, 0.0, 0.0],
    [1.4132875, 1.4132875, 1.4132875],
    [2.826575, 2.826575, 0.0],
    [4.2398625, 4.2398625, 1.4132875],
    [2.826575, 0.0, 2.826575],
    [4.2398625, 1.4132875, 4.2398625],
    [5.65315, 2.826575, 2.826575],
    [7.0664375, 4.2398625, 4.2398625],
    [0.0, 2.826575, 2.826575],
    [1.4132875, 4.2398625, 4.2398625],
    [2.826575, 5.65315, 2.826575],
    [4.2398625, 7.0664375, 4.2398625],
    [2.826575, 2.826575, 5.65315],
    [4.2398625, 4.2398625, 7.0664375],
    [5.65315, 5.65315, 5.65315],
    [7.0664375, 7.0664375, 7.0664375],
]
GaAs_cell_222 = [
    [0.0, 5.65315, 5.65315],
    [5.65315, 0.0, 5.65315],
    [5.65315, 5.65315, 0.0],
]
GaAs_positions_cubic = [
    [0.0, 0.0, 0.0],
    [1.4132875, 1.4132875, 1.4132875],
    [2.826575, 2.826575, 0.0],
    [4.2398625, 4.2398625, 1.4132875],
    [2.826575, 0.0, 2.826575],
    [4.2398625, 1.4132875, 4.2398625],
    [0.0, 2.826575, 2.826575],
    [1.4132875, 4.2398625, 4.2398625],
]

clims_supercell_output = """
Read structure from:               : geometry.in
Chemical formula                   : AsGa
Number of atoms in original cell   : 2
Number of atoms in supercell       : 16
Supercell written to file          : geometry-supercell.in

"""

clims_supercell_format_error = """
***ERROR***: Could not identify format of input file "geometry.out"
-- Please specify the format of input file by "--format".
-- For available formats c.f.: https://wiki.fysik.dtu.dk/ase/ase/io/io.html
"""


def test_supercell_3_default():
    runner = CliRunner()
    with runner.isolated_filesystem():
        write("geometry.in", GaAs, scaled=True)
        result = runner.invoke(supercell, ["2", "2", "2"])
        assert result.exit_code == 0
        sc = read("geometry-supercell.in")
        np.testing.assert_allclose(sc.positions, GaAs_positions_222, atol=1e-12)
        assert result.output == clims_supercell_output


def test_supercell_9_default():
    runner = CliRunner()
    with runner.isolated_filesystem():
        write("geometry.in", GaAs, scaled=True)
        result = runner.invoke(supercell, ["2", "0", "0", "0", "2", "0", "0", "0", "2"])
        assert result.exit_code == 0
        sc = read("geometry-supercell.in")
        np.testing.assert_allclose(sc.positions, GaAs_positions_222, atol=1e-12)
        assert result.output == clims_supercell_output


def test_supercell_to_cubic():
    runner = CliRunner()
    with runner.isolated_filesystem():
        write("geometry.in", GaAs, scaled=True)
        result = runner.invoke(supercell, ["--to-cubic-with-natoms", "8"])
        assert result.exit_code == 0
        sc = read("geometry-supercell.in")
        np.testing.assert_allclose(sc.positions, GaAs_positions_cubic, atol=1e-12)


def test_supercell_format_error():
    runner = CliRunner()
    with runner.isolated_filesystem():
        write("geometry.out", GaAs, scaled=True, format="aims")
        result = runner.invoke(supercell, ["--filein", "geometry.out", "2", "2", "2"])
        assert result.exit_code == 0
        assert result.output == clims_supercell_format_error
