"""Handlers for honeybee simulation parameters."""
import os
import json

from honeybee_energy.simulation.parameter import SimulationParameter

from .helper import get_tempfile


def energy_sim_par_to_json(sim_par_obj):
    """Translate a honeybee-energy SimulationParameter to a JSON file.

        Args:
            sim_par_obj: Either a honeybee-energy SimulationParameter or the path
                to the JSON file. In case the sim_par_obj is a path, it will be
                returned as is. For an object it will be saved to a HBJSON file
                in a temp folder.

        Returns:
            str -- Path to HBJSON file.
    """
    if isinstance(sim_par_obj, str):
        if not os.path.isfile(sim_par_obj):
            raise ValueError('Invalid file path: %s' % sim_par_obj)
        sp_file = sim_par_obj
    elif isinstance(sim_par_obj, SimulationParameter):
        sp_file = get_tempfile('json', 'simulation_parameter')
        obj_dict = sim_par_obj.to_dict()
        # write the dictionary into a file
        with open(sp_file, 'w') as fp:
            json.dump(obj_dict, fp)
    else:
        raise ValueError(
            'Simulation Parameter input should be a string or an object. '
            'Not {}.'.format(type(sim_par_obj))
        )
    return sp_file
