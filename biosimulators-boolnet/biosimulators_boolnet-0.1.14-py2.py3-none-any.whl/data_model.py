""" Data structures for representing the mapping from KISAO terms to
BoolNet methods and their arguments

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-01-08
:Copyright: 2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from biosimulators_utils.data_model import ValueType
from rpy2.robjects.vectors import FloatVector, ListVector  # noqa: F401
import collections


def transform_noise_level(value, model):
    """ Validate a noise level

    Args:
        value (:obj:`float`): value
        model (:obj:`ListVector`): model

    Returns:
        :obj:`float`: value

    Raises:
        :obj:`ValueError`: if the value is not a non-negative float
    """
    if value < 0:
        msg = ("'{}' is not a valid noise level (KISAO_0000572). "
               "Noise level must be a non-negative float.").format(value)
        raise ValueError(msg)
    return value


def transform_gene_probabilities(dict_value, model):
    """ Validate a dictionary that maps the id of each species to its probability to
    be chosen for the next state transition, and transform the dictonary into a vector.

    Args:
        dict_value (:obj:`dict` of :obj:`str` to :obj:`float`): dictionary that maps the id
            of each species to its probability to be chosen for the next state transition
        model (:obj:`ListVector`): model

    Returns:
        :obj:`FloatVector`: species state transition probabilities

    Raises:
        :obj:`ValueError`: if the value is dictionary of the transition probability of each species
    """
    i_genes = list(model.names).index('genes')
    species_ids = list(model[i_genes])

    missing_species = set(species_ids).difference(set(dict_value.keys()))
    extra_species = set(dict_value.keys()).difference(set(species_ids))
    if missing_species:
        msg = (
            'The species state transition probabilities parameter (KISAO_0000574) must define the '
            'transition probability of each species. The value of the parameter does not define transition '
            'probabilities for the following species:\n  - {}'
        ).format('\n  - '.join(sorted(missing_species)))
        raise ValueError(msg)
    if extra_species:
        msg = (
            'The species state transition probabilities parameter (KISAO_0000574) must define the '
            'transition probability of each species. The value of the parameter defines probabilities '
            'which cannot be mapped to species:\n  - {}'
        ).format('\n  - '.join(sorted(extra_species)))
        raise ValueError(msg)

    non_positive_float_values = []
    for species_id, prob in dict_value.items():
        if not isinstance(prob, (int, float)) or prob < 0:
            non_positive_float_values.append(species_id)
    if non_positive_float_values:
        msg = ('Each species state transition probability (KISAO_0000574) must be a float between 0 and 1. '
               'The following species have invalid pstate transition probabilities:\n  - {}'.format(
                   '\n  - '.join('{}: {}'.format(species_id, dict_value[species_id])
                                 for species_id in sorted(non_positive_float_values))))
        raise ValueError(msg)

    sum_values = sum(dict_value.values())
    if abs(sum_values - 1) > 1e-8:
        raise ValueError('The sum of the species state transition probabilities (KISAO_0000574) must be 1 not {}.'.format(
            sum_values))

    return FloatVector([dict_value[species_id] for species_id in species_ids])


KISAO_METHOD_ARGUMENTS_MAP = collections.OrderedDict([
    ('KISAO_0000449', {
        'type': 'synchronous',
        'name': 'synchronous',
        'parameters': {
            'KISAO_0000572': {
                'argument_name': 'noiseLevel',
                'name': 'noise level',
                'type': ValueType.float,
                'transformer': transform_noise_level,
                'invalid_message': 'must be a non-negative float'
            },
        },
        'variable_targets': [
            {
                'variables': 'species levels',
                'targets': r'^/sbml:sbml/sbml:model/qual:listOfQualitativeSpecies/qual:qualitativeSpecies(\[.*?\])?(/@level)?$'
            },
        ],
    }),

    ('KISAO_0000450', {
        'type': 'asynchronous',
        'name': 'asynchronous',
        'parameters': {
            'KISAO_0000574': {
                'argument_name': 'geneProbabilities',
                'name': 'species state transition probabilities',
                'type': ValueType.object,
                'transformer': transform_gene_probabilities,
                'invalid_message': ('must be a dictionary that maps the id of each species to '
                                    'its probability to be chosen for the next state transition'),
            },
            'KISAO_0000572': {
                'argument_name': 'noiseLevel',
                'name': 'noise level',
                'type': ValueType.float,
                'transformer': transform_noise_level,
                'invalid_message': 'must be a non-negative float',
            },
        },
        'variable_targets': [
            {
                'variables': 'species levels',
                'targets': r'^/sbml:sbml/sbml:model/qual:listOfQualitativeSpecies/qual:qualitativeSpecies(\[.*?\])?(/@level)?$'
            },
        ],
    }),

    ('KISAO_0000573', {
        'type': 'probabilistic',
        'name': 'probabilistic',
        'parameters': {
            'KISAO_0000572': {
                'argument_name': 'noiseLevel',
                'name': 'noise level',
                'type': ValueType.float,
                'transformer': transform_noise_level,
                'invalid_message': 'must be a non-negative float'
            },
        },
        'variable_targets': [
            {
                'variables': 'species levels',
                'targets': r'^/sbml:sbml/sbml:model/qual:listOfQualitativeSpecies/qual:qualitativeSpecies(\[.*?\])?(/@level)?$'
            },
        ],
    }),
])
