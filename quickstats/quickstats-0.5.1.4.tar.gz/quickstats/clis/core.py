import click

@click.command(name='run_pulls')
@click.option('-i', '--input_file', required=True, help='Path to the input workspace file')
@click.option('-w', '--workspace', default=None, help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', default=None, help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', default='combData', help='Name of dataset')
@click.option('-p', '--parameter', default='', help='Nuisance parameter(s) to run pulls on.'+\
                                                    'Multiple parameters are separated by commas.'+\
                                                    'Wildcards are accepted.')
@click.option('-x', '--poi', default="", help='POIs to measure')
@click.option('-r', '--profile', default="", help='Parameters to profile')
@click.option('-f', '--fix', default="", help='Parameters to fix')
@click.option('-s', '--snapshot', default="nominalNuis", help='Name of initial snapshot')
@click.option('-o', '--outdir', default="pulls", help='Output directory')
@click.option('-t', '--minimizer_type', default="Minuit2", help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", help='Minimizer algorithm')
@click.option('-c', '--num_cpu', type=int, default=1, help='Number of CPUs to use per parameter')
@click.option('--binned/--unbinned', default=True, help='Binned likelihood')
@click.option('-q', '--precision', type=float, default=0.001, help='Precision for scan')
@click.option('-e', '--eps', type=float, default=1.0, help='Convergence criterium')
@click.option('-l', '--log_level', default="INFO", help='Log level')
@click.option('--eigen/--no-eigen', default=False, help='Compute eigenvalues and vectors')
@click.option('--strategy', type=int, default=0, help='Default strategy')
@click.option('--fix-cache/--no-fix-cache', default=True, help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-multi', default=True, help='Fix MultiPdf level 2')
@click.option('--offset/--no-offset', default=True, help='Offset likelihood')
@click.option('--optimize', type=int, default=2, help='Optimize constant terms')
@click.option('--max_calls', type=int, default=-1, help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, help='Maximum number of Minuit iterations')
@click.option('--batch_mode/--no-batch', default=False, help='Batch mode when evaluating likelihood')
@click.option('--int_bin_precision', type=float, default=-1., help='Integrate the PDF over the bins '
                                                                   'instead of using the probability '
                                                                   'density at the bin centre')
@click.option('--parallel', type=int, default=0, help='Parallelize job across different nuisance'+\
                                                      'parameters using N workers.'+\
                                                      'Use -1 for N_CPU workers.')
@click.option('--cache/--no-cache', default=True, help='Cache existing result')
@click.option('--exclude', default="", help='Exclude NPs (wildcard is accepted)')
def run_pulls(**kwargs):
    """
    Tool for computing NP pulls and impacts
    """
    from quickstats.components import NuisanceParameterPull
    NuisanceParameterPull().run_pulls(**kwargs)
    
@click.command(name='plot_pulls')
@click.option('-i', '--inputdir', required=True, help='Path to directory containing pull results')
@click.option('-p', '--poi', default=None, help='Parameter of interest for plotting impact')
@click.option('-n', '--n_rank', type=int, default=None, help='Total number of NP to rank')
@click.option('-m', '--rank_per_plot', type=int, default=20, help='Number of NP to show in a single plot')
@click.option('--ranking/--no_ranking', default=True, help='Rank NP by impact')
@click.option('--threshold', type=float, default=0., help='Filter NP by postfit impact threshold')
@click.option('--show_sigma/--hide_sigma', default=True, help='Show one standard deviation pull')
@click.option('--show_prefit/--hide_prefit', default=True, help='Show prefit impact')
@click.option('--show_postfit/--hide_postfit', default=True, help='Show postfit impact')
@click.option('--sigma_bands/--no_sigma_bands', default=False, help='Draw +-1, +-2 sigma bands')
@click.option('--sigma_lines/--no_sigma_lines', default=True, help='Draw +-1 sigma lines')
@click.option('--shade/--no_shade', default=True, help='Draw shade')
@click.option('--correlation/--no_correlation', default=True, help='Show correlation impact')
@click.option('--onesided/--overlap', default=True, help='Show onesided impact')
@click.option('--theta_max', type=float, default=2, help='Pull range')
@click.option('-y', '--padding', type=int, default=7, help='Padding below plot for texts and legends.' +\
                                                           'NP column height is 1 unit.')
@click.option('-h', '--height', type=float, default=1.0, help='NP column height')
@click.option('-s', '--spacing', type=float, default=0., help='Spacing between impact box')
@click.option('-d', '--display_poi', default=r"$\mu$", help='POI name to be shown in the plot')
@click.option('-t', '--extra_text', default=None, help='Extra texts below the ATLAS label. '+\
                                                       'Use "//" as newline delimiter')
@click.option('--elumi_label/--no_elumi_label', default=True, help='Show energy and luminosity labels')
@click.option('--ranking_label/--no_ranking_label', default=True, help='Show ranking label')
@click.option('--energy', type=float, default=13, help='Beam energy')
@click.option('--lumi', type=float, default=139, help='Luminosity')
@click.option('--combine_pdf/--split_pdf', default=True, help='Combine all ranking plots into a single pdf')
@click.option('--outdir', default='ranking_plots', help='Output directory')
@click.option('-o', '--outname', default='ranking', help='Output file name prefix')
@click.option('--style', default='default', help='Plotting style. Built-in styles are "default" and "trex".'+\
                                                 'Specify path to yaml file to set custom plotting style.')
@click.option('--fix_axis_scale/--free_axis_scale', default=True, help='Fix the axis scale across all ranking plots')
def plot_pulls(**kwargs):
    """
    Tool for plotting NP pulls and impact rankings
    """    
    from quickstats.plots.np_ranking_plot import NPRankingPlot
    inputdir, poi = kwargs.pop('inputdir'), kwargs.pop('poi')
    ranking_plot = NPRankingPlot(inputdir, poi)
    ranking_plot.plot(**kwargs)
    
    
@click.command(name='likelihood_scan')
@click.option('-i', '--input_file', required=True, help='Path to the input workspace file.')
@click.option('--min', 'poi_min', type=float, required=True, help='Minimum POI value to scan.')
@click.option('--max', 'poi_max', type=float, required=True, help='Maximum POI value to scan.')
@click.option('--step', 'poi_step', type=float, required=True, help='Scan interval.')
@click.option('-p', '--poi', default="", help='POI to scan. If not specified, the first POI from the workspace is used.')
@click.option('--cache/--no-cache', default=True, help='Cache existing result')
@click.option('-o', '--outname', default='{poi}', help='Name of output.')
@click.option('--outdir', default='likelihood_scan', help='Output directory.')
@click.option('--vmin', type=float, default=10, help='Minimum range of POI relative to the central value during likelihood calculation.')
@click.option('--vmax', type=float, default=10, help='Maximum range of POI relative to the central value during likelihood calculation.')
@click.option('-w', '--workspace', default=None, help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', default=None, help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', default='combData', help='Name of dataset.')
@click.option('-s', '--snapshot', default=None, help='Name of initial snapshot')
@click.option('-r', '--profile', default="", help='Parameters to profile')
@click.option('-f', '--fix', default="", help='Parameters to fix')
@click.option('--hesse/--no-hesse', default=False, help='Use Hesse error calculation')
@click.option('--minos/--no-minos', default=True, help='Use Minos error calculation')
@click.option('--constrain/--no-constrain', default=True, help='Use constrained NLL (i.e. include systematics)')
@click.option('-t', '--minimizer_type', default="Minuit2", help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", help='Minimizer algorithm')
@click.option('-c', '--num_cpu', type=int, default=1, help='Number of CPUs to use per parameter')
@click.option('--binned/--unbinned', default=True, help='Binned likelihood')
@click.option('-e', '--eps', type=float, default=1.0, help='Convergence criterium')
@click.option('--strategy', type=int, default=0, help='Default minimization strategy')
@click.option('--fix-cache/--no-fix-cache', default=True, help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-cache',  default=True, help='Fix MultiPdf level 2')
@click.option('--mpsplit',  default=3, help='MP split mode')
@click.option('-v', '--verbose',  default=0, help='verbosity')
@click.option('--max_calls', type=int, default=-1, help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, help='Maximum number of Minuit iterations')
@click.option('--optimize', type=int, default=2, help='Optimize constant terms')
@click.option('--offset/--no-offset', default=False, help='Offset likelihood')
@click.option('--parallel', type=int, default=-1, help='Parallelize job across different scan values.'+\
                                                       'Use -1 for N_CPU workers.')
def likelihood_scan(**kwargs):
    """
    Tool for likelihood scan
    """
    from quickstats.components.likelihood import scan_nll
    scan_nll(**kwargs)

@click.command(name='cls_limit')
@click.option('-i', '--input_file', 'filename', required=True, help='Path to the input workspace file')
@click.option('-p', '--poi', 'poi_name', default=None, help='POI to scan. If not specified, the first POI from the workspace is used.')
@click.option('-d', '--data', 'data_name', default='combData', help='Name of dataset')
@click.option('-o', '--outname', default='limits.json', help='Name of output')
@click.option('--blind/--unblind', 'do_blind', default=True, help='Blind/unblind analysis')
@click.option('--CL', 'CL', default=0.95, help='CL value to use')
@click.option('--precision', default=0.005, help='precision in mu that defines iterative cutoff')
@click.option('--do_tilde/--no_tilde', default=True, help='bound mu at zero if true and do the \tilde{q}_{mu} asymptotics')
@click.option('--predictive_fit/--no_predictive_fit', default=True, help='extrapolate best fit nuisance parameters based on previous fit results')
@click.option('--do_better_bands/--skip_better_bands', default=True, help='evaluate asymptotic CLs limit for various sigma bands')
@click.option('--better_negative_bands/--skip_better_negative_bands', default=False, 
              help='evaluate asymptotic CLs limit for negative sigma bands')
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, help='Binned likelihood')
@click.option('--save_summary/--skip_summary', default=True, help='Save summary information')
@click.option('-f', '--fix', 'fix_param', default="", help='Parameters to fix')
@click.option('-r', '--profile', 'profile_param', default="", help='Parameters to profile')
@click.option('-w', '--workspace', 'ws_name', default=None, help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, help='Name of model config. Auto-detect by default.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, help='Name of initial snapshot')
@click.option('-t', '--minimizer_type', default="Minuit2", help='Minimizer type')
@click.option('-a', '--minimizer_algo', default="Migrad", help='Minimizer algorithm')
@click.option('-e', '--eps', type=float, default=1.0, help='Convergence criterium')
@click.option('--strategy', type=int, default=1, help='Default minimization strategy')
@click.option('--print_level', type=int, default=-1, help='Minimizer print level')
@click.option('--timer/--no_timer', default=False, help='Enable minimizer timer')
@click.option('-c', '--num_cpu', type=int, default=1, help='Number of CPUs to use per parameter')
@click.option('--offset/--no-offset', default=True, help='Offset likelihood')
@click.option('--optimize', type=int, default=2, help='Optimize constant terms')
@click.option('--fix-cache/--no-fix-cache', default=True, help='Fix StarMomentMorph cache')
@click.option('--fix-multi/--no-fix-cache',  default=True, help='Fix MultiPdf level 2')
@click.option('--max_calls', type=int, default=-1, help='Maximum number of function calls')
@click.option('--max_iters', type=int, default=-1, help='Maximum number of Minuit iterations')
@click.option('--batch_mode/--no-batch', default=False, help='Batch mode when evaluating likelihood')
@click.option('--int_bin_precision', type=float, default=-1., help='Integrate the PDF over the bins '
                                                                   'instead of using the probability '
                                                                   'density at the bin centre')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, help='Use constrained NLL')
def cls_limit(**kwargs):
    """
    Tool for evaluating Asymptotic CLs limit
    """
    from quickstats.components import AsymptoticCLs
    outname = kwargs.pop('outname')
    save_summary = kwargs.pop('save_summary')
    asymptotic_cls = AsymptoticCLs(**kwargs)
    asymptotic_cls.evaluate_limits()
    asymptotic_cls.save(outname, summary=save_summary)

@click.command(name='compile')
@click.option('-m', '--macros', default=None, help='Macros to compile (separated by commas)')
def compile_macros(macros):
    """
    Compile ROOT macros
    """
    from quickstats.utils.root_utils import compile_macro
    if macros is None:
        macros = ["RooTwoSidedCBShape", "AsymptoticCLsTool", "RooFitObjects"]
    else:
        macros = macros.split(',')
    for macro in macros:
        compile_macro(macro)
    
@click.command(name='harmonize_np')
@click.argument('ws_files', nargs=-1)
@click.option('-r', '--reference', required=True, help='Path to reference json file containing renaming scheme')
@click.option('-i', '--input_config_path', default=None, help='Path to json file containing input workspace paths')
@click.option('-b', '--base_path', default='./', help='Base path for input config')
@click.option('-o', '--outfile', default='renamed_np.json', help='Output filename')
def harmonize_np(ws_files, reference, input_config_path, base_path, outfile):
    """
    Harmonize NP names across different workspaces
    """
    from quickstats.components import NuisanceParameterHarmonizer
    harmonizer = NuisanceParameterHarmonizer(reference)
    if (len(ws_files) > 0) and input_config_path is not None:
        raise RuntimeError('either workspace paths or json file containing workspace paths should be given')
    if len(ws_files) > 0:
        harmonizer.harmonize(ws_files, outfile=outfile)
    elif (input_config_path is not None):
        harmonizer.harmonize_multi_input(input_config_path, base_path, outfile=outfile) 