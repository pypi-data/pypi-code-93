from ase.io import read, write
from ase import Atoms
from phonopy.structure.atoms import PhonopyAtoms
from phonopy import Phonopy
from pathlib import Path
import numpy as np


def write_phonopy_disp_yaml(phonon, calculator, supercell_matrix):

    from phonopy.interface.calculator import get_default_physical_units
    from phonopy.interface.phonopy_yaml import PhonopyYaml

    filename = "phonopy_disp.yaml"
    yaml_settings = {
        "force_sets": False,
        "force_constants": False,
        "born_effective_charge": False,
        "dielectric_constant": False,
        "displacements": True,
    }
    adim = [str(x) for x in np.array(supercell_matrix).flatten()]
    print(adim)
    dim = " ".join(adim)

    phonopy_confs = {
        "dim": dim,
        "calculator": calculator,
        "create_displacements": ".true.",
    }

    units = get_default_physical_units(calculator)

    phpy_yaml = PhonopyYaml(
        configuration=phonopy_confs, physical_units=units, settings=yaml_settings
    )
    phpy_yaml.set_phonon_info(phonon)
    with open(filename, "w") as w:
        w.write(str(phpy_yaml))


def initialize_phonopy(
    structure,
    structure_file="geometry.in",
    structure_format="aims",
    supercell_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    primitive_matrix="auto",
):

    atoms = PhonopyAtoms(
        symbols=structure.get_chemical_symbols(),
        cell=structure.get_cell(),
        scaled_positions=structure.get_scaled_positions(),
    )

    phonon = Phonopy(atoms, supercell_matrix, primitive_matrix=primitive_matrix)
    phonon.generate_displacements(distance=0.01)
    supercells = phonon.get_supercells_with_displacements()

    n_digits = len(str(len(supercells))) + 1
    p = Path(".")
    for i, supercell in enumerate(supercells):
        atoms = Atoms(
            symbols=supercell.get_chemical_symbols(),
            scaled_positions=supercell.get_scaled_positions(),
            cell=supercell.get_cell(),
            pbc=True,
        )
        displacement = p / f"displacement-{str(i).zfill(n_digits)}"
        displacement.mkdir(exist_ok=True)
        write(displacement / structure_file, atoms, format=structure_format)

    write_phonopy_disp_yaml(phonon, structure_format, supercell_matrix)
    # phonon.save()


def parse_forces(num_atoms, outfile):
    from phonopy.interface.aims import parse_set_of_forces

    p = Path(".")
    output_files = [str(s) for s in p.glob(f"**/{outfile}")]
    print("Found following output files:")
    for output_file in output_files:
        print(output_file)
    forces = parse_set_of_forces(num_atoms, output_files)
    # print(force_sets)
    return forces

    #  displacement_dataset =
    # {'natom': number_of_atoms_in_supercell,
    #  'first_atoms': [
    #    {'number': atom index of displaced atom (starting with 0),
    #     'displacement': displacement in Cartesian coordinates,
    #     'forces': forces on atoms in supercell},
    #    {...}, ...]}


def post_process_phonopy(mesh=[20, 20, 20], outfile="aims.out"):
    from phonopy import load

    phonon = load(phonopy_yaml="phonopy_disp.yaml", produce_fc=False)
    n_atoms = phonon.supercell.get_number_of_atoms()
    forces = parse_forces(n_atoms, outfile)
    print(forces)
    n_atoms_supercell = len(forces[0])
    assert n_atoms == n_atoms_supercell

    first_atoms = []
    for fs, disp in zip(forces, phonon.get_displacements()):
        first_atoms.append({"number": disp[0], "displacement": disp[1:], "forces": fs})
    displacement_dataset = {"natom": n_atoms_supercell, "first_atoms": first_atoms}
    phonon.dataset = displacement_dataset
    phonon.produce_force_constants()
    phonon.run_mesh(mesh)
    phonon.run_total_dos()
    phonon.plot_total_dos().show()
    phonon.save()


# Input parameters needed from form
# structure_format = "aims"
# supercell_matrix = [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
#
# structure_file = "geometry.in"
# structure = read(structure_file, format=structure_format)
# num_atoms = 64
# initialize_phonopy(structure, structure_file, structure_format, supercell_matrix)
# forces = parse_forces(num_atoms)
# post_process_phonopy(forces)
