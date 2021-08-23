from click.testing import CliRunner
from clims.cli.prepare_run import prepare_run
from ase.build import bulk
from ase.io import write
from test.file_comparison import compare_files
from pathlib import Path
from clims.cli.configure import get_config_value, clims_configure

GaAs = bulk("GaAs", crystalstructure="zincblende", a=5.65315)

def test_prepare_run_default():
    runner = CliRunner()
    try:
        get_config_value('species_path')
    except:
        species_path = Path.cwd() / 'test' / 'species_defaults'
        runner.invoke(clims_configure,['--species-path', species_path.as_posix()])
    
    with runner.isolated_filesystem():
        with open("control.in_ref","w") as f:
            f.write(control_in)
        write("geometry.in", GaAs, scaled=True, format="aims")
        result = runner.invoke(prepare_run,['--bands','--relax'])
        assert result.exit_code == 0
        compare_files("control.in","control.in_ref")
        
        
control_in = """#===============================================================================
# FHI-aims file: control.in
# Created using the Atomic Simulation Environment (ASE)
# Fri Apr 23 17:56:41 2021
#===============================================================================
xc                                 pbe
relativistic                       atomic_zora scalar
k_grid                             12 12 12
relax_geometry                     trm 5e-3
relax_unit_cell                    full
output                             band   0.00000  0.00000  0.00000   0.50000  0.00000  0.50000   33 G  X
output                             band   0.50000  0.00000  0.50000   0.50000  0.25000  0.75000   17 X  W
output                             band   0.50000  0.25000  0.75000   0.37500  0.37500  0.75000   12 W  K
output                             band   0.37500  0.37500  0.75000   0.00000  0.00000  0.00000   35 K  G
output                             band   0.00000  0.00000  0.00000   0.50000  0.50000  0.50000   29 G  L
output                             band   0.50000  0.50000  0.50000   0.62500  0.25000  0.62500   20 L  U
output                             band   0.62500  0.25000  0.62500   0.50000  0.25000  0.75000   12 U  W
output                             band   0.50000  0.25000  0.75000   0.50000  0.50000  0.50000   24 W  L
output                             band   0.50000  0.50000  0.50000   0.37500  0.37500  0.75000   20 L  K
output                             band   0.62500  0.25000  0.62500   0.50000  0.00000  0.50000   12 U  X
#===============================================================================

################################################################################
#
#  FHI-aims code project
#  VB, Fritz-Haber Institut, 2009
#
#  Suggested "light" defaults for Ga atom (to be pasted into control.in file)
#  Be sure to double-check any results obtained with these settings for post-processing,
#  e.g., with the "tight" defaults and larger basis sets.
#
################################################################################
  species        Ga
#     global species definitions
    nucleus             31
    mass                69.723
#
    l_hartree           4
#
    cut_pot             3.5          1.5  1.0
    basis_dep_cutoff    1e-4
#
    radial_base         54 5.0
    radial_multiplier   1
    angular_grids       specified
      division   0.5103   50
      division   0.8880  110
      division   1.2009  194
      division   1.5000  302
#      division   1.7093  434
#      division   1.8791  590
#      division   1.9525  770
#      division   2.3801 1202
#      outer_grid  1202
      outer_grid  302
################################################################################
#
#  Definition of "minimal" basis
#
################################################################################
#     valence basis states
    valence      4  s   2.
    valence      4  p   1.
    valence      3  d  10.
#     ion occupancy
    ion_occ      4  s   1.
    ion_occ      3  p   6.
    ion_occ      3  d  10.
################################################################################
#
#  Suggested additional basis functions. For production calculations, 
#  uncomment them one after another (the most important basis functions are
#  listed first).
#
#  Constructed for dimers: 1.85 A, 2.10 A, 2.45 A, 3.00 A, 4.00 A
#
################################################################################
#  "First tier" - improvements: -222.33 meV to -26.19 meV 
     hydro 2 p 1.2
     hydro 3 d 3.8
#     hydro 4 f 6.8
     ionic 4 s auto
#  "Second tier" - improvements: -11.68 meV to -1.61 meV
#     hydro 5 g 10
#     hydro 4 p 3.6
#     hydro 4 f 13.2
#     hydro 6 h 14.4
#     hydro 4 d 5.2
#     hydro 1 s 0.45
#  "Third tier" - improvements: -0.64 meV to -0.15 meV
#     hydro 3 p 3.4
#     hydro 3 s 2.2
#     hydro 5 g 14
#     hydro 4 f 6.2
#     hydro 5 d 7.2
#  "Fourth tier"  -improvements: -0.12 meV and below
#     hydro 3 s 3.8
#     hydro 5 f 27.2
#     hydro 6 h 16
#     hydro 5 g 9.2
#     hydro 4 d 8.6
#     hydro 2 p 3.6  

################################################################################
#
#  FHI-aims code project
#  VB, Fritz-Haber Institut, 2009
#
#  Suggested "light" defaults for As atom (to be pasted into control.in file)
#  Be sure to double-check any results obtained with these settings for post-processing,
#  e.g., with the "tight" defaults and larger basis sets.
#
################################################################################
  species        As
#
    nucleus             33
    mass                74.92160
#
    l_hartree           4
#
    cut_pot             3.5          1.5  1.0
    basis_dep_cutoff    1e-4
#
    radial_base         55 5.0
    radial_multiplier   1
    angular_grids       specified
      division   0.4982   50
      division   0.9113  110
      division   1.1593  194
      division   1.4959  302
#      division   1.6697  434
#      division   1.8319  590
#      division   1.9752  770
#      division   2.0131  974
#      division   2.4015 1202
#      outer_grid  1202
      outer_grid  302
################################################################################
#
#  Definition of "minimal" basis
#
################################################################################
#     valence basis states
    valence      4  s   2.
    valence      4  p   3.
    valence      3  d  10.
#     ion occupancy
    ion_occ      4  s   1.
    ion_occ      4  p   2.
    ion_occ      3  d  10.
################################################################################
#
#  Suggested additional basis functions. For production calculations, 
#  uncomment them one after another (the most important basis functions are
#  listed first).
#
#  Constructed for dimers: 1.75 A, 2.10 A, 2.50 A, 3.00 A, 4.00 A
#
################################################################################
#  "First tier" - improvements: -385.12 meV to -54.94 meV 
     hydro 3 d 4
     hydro 2 p 1.5
#     hydro 4 f 6.8
     ionic 4 s auto
#  "Second tier" - improvements: -22.14 meV to -3.21 meV
#     hydro 5 g 10
#     hydro 6 h 13.6
#     hydro 4 p 4.3
#     hydro 4 f 15.6
#     hydro 4 d 5.4
#     hydro 1 s 0.6
#  "Third tier" - improvements: -0.57 meV to -0.13 meV
#     hydro 5 g 16.4
#     hydro 4 f 7.4
#     hydro 5 d 7.4
#     ionic 4 p auto
#     hydro 3 s 2.6     
#  "Fourth tier" - improvements: -0.30 meV and below
#     hydro 3 p 3
#     hydro 6 h 18.4
#     hydro 5 d 11.2
#     hydro 5 f 15.2
#     hydro 5 g 13.6
#     hydro 5 s 6.2   
"""
