""" Data model

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-08-07
:Copyright: 2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from biosimulators_utils.data_model import ValueType
import collections

__all__ = [
    'KISAO_ALGORITHM_MAP',
]


KISAO_ALGORITHM_MAP = collections.OrderedDict([
    ('KISAO_0000032', {
        'kisao_id': 'KISAO_0000032',
        'id': 'rungekutta',
        'name': "4th order Runge-Kutta method",
        'parameters': {
        },
    }),
    ('KISAO_0000029', {
        'kisao_id': 'KISAO_0000029',
        'id': 'discrete',
        'name': "Gillepie's method",
        'parameters': {
            'KISAO_0000488': {
                'kisao_id': 'KISAO_0000488',
                'id': 'seed',
                'name': 'random number generator seed',
                'type': ValueType.integer,
                'default': None,
                'enabled': True,
            },
        },
    }),
    ('KISAO_0000030', {
        'kisao_id': 'KISAO_0000030',
        'id': 'euler',
        'name': "Forward Euler one step method",
        'parameters': {
        },
    }),
    ('KISAO_0000031', {
        'kisao_id': 'KISAO_0000031',
        'id': 'backeul',
        'name': "Backward Euler method",
        'parameters': {
            'KISAO_0000597': {
                'kisao_id': 'KISAO_0000597',
                'id': None,
                'name': 'tolerance',
                'type': ValueType.float,
                'default': 1e-7,
                'enabled': False,
            },
            'KISAO_0000486': {
                'kisao_id': 'KISAO_0000486',
                'id': None,
                'name': 'Maximum number of iterates for each step',
                'type': ValueType.integer,
                'default': 10,
                'enabled': False,
            },
        },
    }),
    ('KISAO_0000279', {
        'kisao_id': 'KISAO_0000279',
        'id': 'adams',
        'name': "Adams-Bashforth fourth order predictor-corrector method",
        'parameters': {
        },
    }),
    ('KISAO_0000288', {
        'kisao_id': 'KISAO_0000288',
        'id': 'gear',
        'name': "Gear method",
        'parameters': {
            'KISAO_0000485': {
                'kisao_id': 'KISAO_0000485',
                'id': 'dtmin',
                'name': 'minimum allowable timestep',
                'type': ValueType.float,
                'default': 1e-12,
                'enabled': True,
            },
            'KISAO_0000467': {
                'kisao_id': 'KISAO_0000467',
                'id': 'dtmax',
                'name': 'maximum allowable timestep',
                'type': ValueType.float,
                'default': 1,
                'enabled': True,
            },
            'KISAO_0000597': {
                'kisao_id': 'KISAO_0000597',
                'id': 'toler',
                'name': 'tolerance',
                'type': ValueType.float,
                'default': 0.001,
                'enabled': True,
            },
        },
    }),
    ('KISAO_0000087', {
        'kisao_id': 'KISAO_0000087',
        'id': '5dp',
        'name': "Dormand-Prince method",
        'parameters': {
            'KISAO_0000209': {
                'kisao_id': 'KISAO_0000209',
                'id': 'toler',
                'name': 'relative tolerance',
                'type': ValueType.float,
                'default': 1e-3,
                'enabled': True,
            },
            'KISAO_0000211': {
                'kisao_id': 'KISAO_0000211',
                'id': 'atoler',
                'name': 'absolute tolerance',
                'type': ValueType.float,
                'default': 1e-3,
                'enabled': True,
            },
        },
    }),
    ('KISAO_0000436', {
        'kisao_id': 'KISAO_0000436',
        'id': '83dp',
        'name': "Dormand-Prince 8(5,3) method",
        'parameters': {
            'KISAO_0000209': {
                'kisao_id': 'KISAO_0000209',
                'id': 'toler',
                'name': 'relative tolerance',
                'type': ValueType.float,
                'default': 1e-3,
                'enabled': True,
            },
            'KISAO_0000211': {
                'kisao_id': 'KISAO_0000211',
                'id': 'atoler',
                'name': 'absolute tolerance',
                'type': ValueType.float,
                'default': 1e-3,
                'enabled': True,
            },
        },
    }),
    ('KISAO_0000033', {
        'kisao_id': 'KISAO_0000033',
        'id': '2rb',
        'name': "Two step Rosenbrock method",
        'parameters': {
            'KISAO_0000209': {
                'kisao_id': 'KISAO_0000209',
                'id': 'toler',
                'name': 'relative tolerance',
                'type': ValueType.float,
                'default': 1e-3,
                'enabled': True,
            },
            'KISAO_0000211': {
                'kisao_id': 'KISAO_0000211',
                'id': 'atoler',
                'name': 'absolute tolerance',
                'type': ValueType.float,
                'default': 1e-3,
                'enabled': True,
            },
            'KISAO_0000480': {
                'kisao_id': 'KISAO_0000480',
                'id': 'bandlo',
                'name': 'lower half-bandwidth',
                'type': ValueType.integer,
                'default': 0,
                'enabled': True,
            },
            'KISAO_0000479': {
                'kisao_id': 'KISAO_0000479',
                'id': 'bandup',
                'name': 'upper half-bandwidth',
                'type': ValueType.integer,
                'default': 0,
                'enabled': True,
            },
        },
    }),
    ('KISAO_0000019', {
        'kisao_id': 'KISAO_0000019',
        'id': 'cvode',
        'name': "CVODE",
        'parameters': {
            'KISAO_0000209': {
                'kisao_id': 'KISAO_0000209',
                'id': 'toler',
                'name': 'relative tolerance',
                'type': ValueType.float,
                'default': 1e-3,
                'enabled': True,
            },
            'KISAO_0000211': {
                'kisao_id': 'KISAO_0000211',
                'id': 'atoler',
                'name': 'absolute tolerance',
                'type': ValueType.float,
                'default': 1e-3,
                'enabled': True,
            },
            'KISAO_0000480': {
                'kisao_id': 'KISAO_0000480',
                'id': 'bandlo',
                'name': 'lower half-bandwidth',
                'type': ValueType.integer,
                'default': 0,
                'enabled': True,
            },
            'KISAO_0000479': {
                'kisao_id': 'KISAO_0000479',
                'id': 'bandup',
                'name': 'upper half-bandwidth',
                'type': ValueType.integer,
                'default': 0,
                'enabled': True,
            },
        },
    }),
    ('KISAO_0000086', {
        'kisao_id': 'KISAO_0000086',
        'id': 'qualrk',
        'name': " Quality 4th order Runge-Kutta method",
        'parameters': {
            'KISAO_0000597': {
                'kisao_id': 'KISAO_0000597',
                'id': 'toler',
                'name': 'tolerance',
                'type': ValueType.float,
                'default': 1e-3,
                'enabled': True,
            },
            'KISAO_0000485': {
                'kisao_id': 'KISAO_0000485',
                'id': 'dtmin',
                'name': 'minimum allowable timestep',
                'type': ValueType.float,
                'default': 1e-12,
                'enabled': True,
            },
            'KISAO_0000467': {
                'kisao_id': 'KISAO_0000467',
                'id': 'dtmax',
                'name': 'maximum allowable timestep',
                'type': ValueType.float,
                'default': 1,
                'enabled': True,
            },
            'KISAO_0000665': {
                'kisao_id': 'KISAO_0000665',
                'id': 'newt_iter',
                'name': 'Maximum number of iterates per root finding step',
                'type': ValueType.integer,
                'default': 1000,
                'enabled': True,
            },
            'KISAO_0000565': {
                'kisao_id': 'KISAO_0000565',
                'id': 'newt_tol',
                'name': 'Newton tolerance',
                'type': ValueType.float,
                'default': 1e-3,
                'enabled': True,
            },
            'KISAO_0000666': {
                'kisao_id': 'KISAO_0000666',
                'id': 'jac_eps',
                'name': 'Jacobian epsilon',
                'type': ValueType.float,
                'default': 1e-5,
                'enabled': True,
            },
        },
    }),
    ('KISAO_0000301', {
        'kisao_id': 'KISAO_0000301',
        'id': 'modeuler',
        'name': "Two step modified Euler method",
        'parameters': {
        },
    }),
    ('KISAO_0000367', {
        'kisao_id': 'KISAO_0000367',
        'id': 'ymp',
        'name': "Symplectic method",
        'parameters': {
        },
    }),
    ('KISAO_0000664', {
        'kisao_id': 'KISAO_0000664',
        'id': 'volterra',
        'name': "Second order backward method for Volterra equations",
        'parameters': {
            'KISAO_0000597': {
                'kisao_id': 'KISAO_0000597',
                'id': None,
                'name': 'tolerance',
                'type': ValueType.float,
                'default': 1e-7,
                'enabled': False,
            },
            'KISAO_0000486': {
                'kisao_id': 'KISAO_0000486',
                'id': None,
                'name': 'Maximum number of iterates for each step',
                'type': ValueType.integer,
                'default': 10,
                'enabled': False,
            },
            'KISAO_0000667': {
                'kisao_id': 'KISAO_0000667',
                'id': 'vmaxpts',
                'name': 'maximum number of points',
                'type': ValueType.integer,
                'default': 4000,
                'enabled': True,
            },
        },
    }),
    ('KISAO_0000668', {
        'kisao_id': 'KISAO_0000668',
        'id': 'stiff',
        'name': "Gear-like method for stiff ODE systems",
        'parameters': {
            'KISAO_0000485': {
                'kisao_id': 'KISAO_0000485',
                'id': 'dtmin',
                'name': 'minimum allowable timestep',
                'type': ValueType.float,
                'default': 1e-12,
                'enabled': True,
            },
            'KISAO_0000467': {
                'kisao_id': 'KISAO_0000467',
                'id': 'dtmax',
                'name': 'maximum allowable timestep',
                'type': ValueType.float,
                'default': 1,
                'enabled': True,
            },
            'KISAO_0000597': {
                'kisao_id': 'KISAO_0000597',
                'id': 'toler',
                'name': 'tolerance',
                'type': ValueType.float,
                'default': 0.001,
                'enabled': True,
            },
        },
    }),
])
