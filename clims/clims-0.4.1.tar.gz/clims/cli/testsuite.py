import click
import json
from clims.testsuite_tools import generate_testsuite, get_directory_info


@click.group()
def testsuite():
    """
    Create a set of folders based on combinations of different 'control.in' settings.
    """
    pass

@testsuite.command()
@click.argument("calculator_json",type=click.File())
def create(calculator_json):
    """Create all possible combinations from the CALCULATOR_JSON file."""

    calc_set = json.load(calculator_json)
    generate_testsuite(calc_set)


@testsuite.command()
def example():
    """Get example JSON file containing the calculator"""

    calc_set = {
        "xc": ["pbe", "pz-lda"],
        "k_grid": [(2, 2, 2), (3, 3, 3)],
        "aims_command": ["orterun aims_1.x", "orterun aims_2.x"],
        "outfilename": "aims.out",
        "species_dir": [
            "/Users/sebastian/software/FHIaims/species_defaults/light",
            "/Users/sebastian/software/FHIaims/species_defaults/tight",
        ],
    }
    with open('calculator.json','w') as calculator_json:
        json.dump(calc_set, calculator_json, indent=4)


@testsuite.command()
def info():
    get_directory_info()
