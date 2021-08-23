from click.testing import CliRunner
from clims.cli.wigner_seitz_cluster import construct
from ase.build import bulk
from ase.io import write, read
import numpy as np

GaAs = bulk("GaAs", crystalstructure="zincblende", a=5.65315)
GaAs.set_initial_magnetic_moments([2,0])

GaAs_WS_positions = [
    [ 0.1,        0.1,        0.1      ],
    [ 1.5132875,  1.5132875,  1.5132875],
    [-2.726575,  -2.726575,   0.1      ],
    [-1.3132875, -1.3132875,  1.5132875],
    [-2.726575,   0.1,       -2.726575 ],
    [-1.3132875,  1.5132875, -1.3132875],
    [ 0.1,        2.926575,  -2.726575 ],
    [-4.1398625, -1.3132875, -1.3132875],
    [ 0.1,       -2.726575,  -2.726575 ],
    [ 1.5132875, -1.3132875, -1.3132875],
    [ 2.926575,   0.1,       -2.726575 ],
    [-1.3132875, -4.1398625, -1.3132875],
    [ 2.926575,  -2.726575,   0.1      ],
    [-1.3132875, -1.3132875, -4.1398625],
    [ 0.1,        0.1,       -5.55315  ],
    [ 1.5132875,  1.5132875, -4.1398625],
]
 
GaAs_WS_moments = [2., 0., 2., 0., 2., 0., 2., 0., 2., 0., 2., 0., 2., 0., 2., 0.]
 
GaAs_WS_symbols = [
    'Ga', 'As', 'Ga', 'As', 'Ga', 'As', 'Ga', 'As', 'Ga', 'As', 'Ga', 'As', 'Ga', 'As', 'Ga', 'As'
]

def test_wigner_seitz_cluster():
    runner = CliRunner()
    with runner.isolated_filesystem():
        write("geometry.in", GaAs, scaled=True)
        result = runner.invoke(construct,['--translate-basis','0.1','0.1','0.1','2','2','2'])
        assert result.exit_code == 0
        ws = read('geometry-ws-cluster.in')
        np.testing.assert_allclose(ws.positions, GaAs_WS_positions, atol=1e-12)
        assert ws.get_chemical_symbols() == GaAs_WS_symbols
        assert list(ws.get_initial_magnetic_moments()) == GaAs_WS_moments
