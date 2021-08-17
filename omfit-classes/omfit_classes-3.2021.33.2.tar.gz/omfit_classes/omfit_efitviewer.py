# -*-Python-*-
# Created by eldond at 2019-12-23 08:56

"""
Contains supporting functions to back the efitviewer GUI
"""

try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

import omas
from omas import ODS
from omfit_classes.omfit_base import OMFITtmp, OMFITmodule, OMFITtree
from omfit_classes.omfit_json import OMFITjson, OMFITsettings, SettingsName
from omfit_classes.omfit_omas_utils import setup_hardware_overlay_cx, add_hardware_to_ods
from omfit_classes.omfit_formatter import omfit_formatter
from omfit_classes.utils_fusion import is_device

__all__ = ['efitviewer']

# Provide better plot limits than autoscale, which might cut off some external hardware like magnetic probes
default_plot_limits = {'DIII-D': {'x': [0.75, 2.75], 'y': [-1.75, 1.75]}, 'EAST': {'x': [0.55, 3.4], 'y': [-2.1, 2.1]}}

# List of features and the OMAS version required to use them
omas_features = {
    'contour_quantity': '0.50.0',
    'allow_fallback': '0.50.0',
    'sf': '0.50.0',
    'label_contours': '0.50.0',
    'show_wall': '0.55.2',
    'xkw': '0.52.2',
}


# Shortcuts and utilities for defining key information, data structure, and shortcuts -----------------------------
def efitviewer():
    """Shortcut for launching efitviewer"""
    OMFIT['scratch']['__efitviewer_gui__'].run()
    return


def pick_output_location():
    """
    Selects efitviewer output folder for storing ODSs and settings

    :return (string, string, dict-like, dict-like, dict-like, dict-like)
        Location in the tree of the output folder
        Location in the tree of the settings dictionary
        Reference to output folder in the tree
        Reference to efitviewer settings
        Reference to settings in the local parent module or main OMFIT settings
        Reference to main scratch area
    """
    default_out_loc = "OMFIT['efitviewer']"
    scratch = OMFIT['scratch']
    override_loc = scratch.get('efitviewer_out_loc', None)

    # Resolve output location
    if override_loc is None:
        out_loc = default_out_loc
        printd('No output_loc supplied; using default')
    elif not (is_string(evalExpr(override_loc))):
        out_loc = default_out_loc
        printd('output_loc is not a string; using default loc instead')
    else:
        out_loc = output_loc
        printd('assuming user-supplied output_loc is valid')

    # Make sure the output loc exists
    the_split = out_loc.split('[')
    locations = ['['.join(the_split[:i]) for i in range(1, len(the_split) + 1)]
    for i in range(1, len(locations)):
        key = locations[i].split('[')[-1].split(']')[0]
        key = key.split(key[0])[1]  # Remove quotes, regardless of whether ' or " is used
        the_parent = eval(locations[i - 1])
        if key not in the_parent:
            if isinstance(the_parent, OMFITtmp):
                # Items added under OMFITtmp should be OMFITtree
                key_type = OMFITtree
            elif isinstance(the_parent, OMFITjson):
                # Items under OMFITjson should be SortedDict
                key_type = SortedDict
            elif isinstance(the_parent, OMFITsettings):
                # Items under OMFITsettings should be SettingsName
                key_type = SettingsName
            elif type(the_parent).__name__ in ['OMFITmaintree']:
                # OMFITmaintree might not be defined in this context
                key_type = OMFITtree
            elif type(the_parent).__name__ in ['OMFITtree', 'dict', 'SettingsName', 'SortedDict']:
                # Copy class of parent if parent's class is appropriate
                key_type = type(the_parent)
                printd('pick_output_location(): copy parent type', topic='efitviewer')
            else:
                # Otherwise, default to SortedDict
                key_type = SortedDict
                printd('pick_output_location(): we do not like this type; just use SortedDict', topic='efitviewer')

            printd(f'pick_output_location(): type(parent)={type(the_parent)}&type(key)={key_type}', topic='efitviewer')
            the_parent[key] = key_type()

    out = eval(out_loc)

    # Make sure settings are defined and load defaults if needed
    if 'SETTINGS' not in out:
        out['SETTINGS'] = OMFITsettings(os.sep.join([OMFITsrc, 'framework_guis', 'efitviewer_settings.txt']))
    settings_loc = out_loc + "['SETTINGS']"
    settings = eval(settings_loc)

    # Also get a reference to parent module or main OMFIT settings
    for loc in locations[::-1]:
        ppm = eval(loc)
        if (isinstance(ppm, OMFITmodule) and ('SETTINGS' in ppm)) or ('MainSettings' in ppm):
            parent_settings = ppm['SETTINGS'] if 'SETTINGS' in ppm else ppm['MainSettings']
            break
    else:
        parent_settings = MainSettings

    return out_loc, settings_loc, out, settings, parent_settings, scratch


def add_command_box_tab():
    """
    Adds a tab to the command box. Useful if the user wants output dumped to a new tab.

    :return: int
        Index of the new command box tab that has been added
    """
    number = len(OMFITaux['GUI'].command)
    OMFITaux['GUI'].commandAdd(number)
    OMFITaux['GUI'].commandNotebook.select(OMFITaux['GUI'].commandNotebook.tabs().index(OMFITaux['GUI'].commandNotebook.select()))
    return number


# Data loading and related helpers --------------------------------------------------------------------------------
def load_cx_ods(gfile=None, device=None, shot=None, t=None, efitid=None, index=0):
    """
    Puts an ODS with CX info in the tree

    :param gfile: OMFITgeqdsk instance [optional if shot, t, and efitid are supplied]

    :param device: string

    :param shot: int [ignored if gfile is supplied]

    :param t: int [ignored if gfile is supplied]
        Leave it as None to load minimal data for all slices,
        or specify a single time to load just one complete slice

    :param efitid: string [ignored if gfile is supplied]

    :param index: int
        Index of the ODS, for managing multi-shot overlays

    :return: ODS instance
    """
    printd(f'  loading cx ods for index {index}', topic='omfit_efitviewer')
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    the_case = settings['cases'][index]
    def_def_gfile = settings['cases'][0]['gfile']
    def_def_device = tokamak(settings['cases'][0]['device'])
    def_def_shot = evalExpr(settings['cases'][0]['shot'])
    if index == 0:
        ods_tag = 'efitviewer_ods'
        def_device = def_def_device
        def_shot = def_def_shot
        def_gfile = def_def_gfile
    else:
        ods_tag = 'efitviewer_ods_{}'.format(index)
        def_device = the_case.setdefault('device', def_def_device)
        def_shot = the_case.setdefault('shot', def_def_shot)
        def_gfile = the_case.setdefault('gfile', def_def_gfile)

    if gfile is None:
        gfile = def_gfile
    if device is None:
        device = def_device
    if shot is None:
        shot = def_shot
    if efitid is None:
        efitid = the_case.setdefault('efit_tree', None)

    if isinstance(gfile, str):
        gfile_str = gfile
        gfile = eval(gfile)
    elif gfile is not None:
        gfile_str = '<<YOUR G-FILE FOR {device:}:{gfilename:}>>'.format(device=device, gfilename=gfile.filename)
    else:
        gfile_str = None

    if gfile is None:
        load_cmd = "setup_hardware_overlay_cx({}, {}, {}, efitid={}, default_load=False)".format(
            repr(device), repr(shot), repr(t), repr(efitid)
        )
        ods = out[ods_tag] = setup_hardware_overlay_cx(device, shot, t, efitid=efitid, default_load=False, quiet=True)
    else:
        ods = out[ods_tag] = setup_hardware_overlay_cx(device, geqdsk=gfile, default_load=False, quiet=True)
        load_cmd = "setup_hardware_overlay_cx({}, geqdsk={}, default_load=False)".format(repr(device), gfile_str)

    settings['cases'][index]['instructions_for_loading_ods'] = load_cmd
    assert 'equilibrium' in ods, 'Equilibrium data should have been added to the ODS, but they are missing.'
    assert 'time' in ods['equilibrium'], 'No time in equilibrium. It should have been added. This ODS is not okay.'

    return ods


def list_available_hardware_descriptors(device):
    """
    Determines which hardware systems have descriptor functions available.

    That is, which systems can easily have their geometry loaded into an ODS?

    :param device: string

    :return: list of strings
        List of formal IMAS names of hardware systems that can be easily loaded into an ODS by OMFIT
    """
    hw0 = 'setup_'
    hw1 = '_hardware_description_'
    available_hardware_d3d = [
        a.split(hw1 + 'd3d')[0].split(hw0)[-1]
        for a in omfit_classes.omfit_omas_d3d.__all__
        if a.startswith(hw0) and a.endswith(hw1 + 'd3d')
    ]
    available_hardware_east = [
        a.split(hw1 + 'east')[0].split(hw0)[-1]
        for a in omfit_classes.omfit_omas_east.__all__
        if a.startswith(hw0) and a.endswith(hw1 + 'east')
    ]
    available_hardware_kstar = [
        a.split(hw1 + 'kstar')[0].split(hw0)[-1]
        for a in omfit_classes.omfit_omas_kstar.__all__
        if a.startswith(hw0) and a.endswith(hw1 + 'kstar')
    ]
    available_hardware_general = [
        a.split(hw1 + 'general')[0].split(hw0)[-1]
        for a in omfit_classes.omfit_omas.__all__
        if a.startswith(hw0) and a.endswith(hw1 + 'general')
    ]

    if is_device(device, 'DIII-D'):
        available_hardware = available_hardware_general + available_hardware_d3d
    elif is_device(device, ['EAST', 'EAST_US']):
        available_hardware = available_hardware_general + available_hardware_east
    elif is_device(device, 'KSTAR'):
        available_hardware = available_hardware_general + available_hardware_kstar
    else:
        available_hardware = available_hardware_general
    return available_hardware


def list_available_hardware_data(ods, systems=None):
    """
    Determines which systems appear to have valid geometry data in ODS and could probably be overlaid in efitviewer.

    :param ods: ODS instance

    :param systems: list of strings
        List of formal IMAS names of hardware systems to consider in the search.
        Defaults to all keys in top level ods.

    :return: list of strings
        List of formal IMAS names of hardware systems that look like they're ready to plot using data already in ods.
    """
    if systems is None:
        systems = ods.keys()

    return [system for system in systems if len(ods.search_paths('{}.*(geometry|position|position_control)'.format(system))) > 0]


def list_hardware_overlay_methods():
    """
    Determines which hardware systems can be overlaid natively by OMAS

    :return: list of strings
        List of formal IMAS names of hardware systems that have plot overlay methods built into OMAS
    """
    a1 = 'plot_'
    a2 = '_overlay'
    return [a[len(a1) : -len(a2)] for a in dir(ODS) if a.startswith(a1) and a.endswith(a2) and a != 'plot_overlay']


def setup_avail_systems(suppress_systems=['pulse_schedule']):
    """
    Makes sure keys in systems correspond to available plot overlays in ODS

    Operates on the 0th ODS instance, not the different equilibrium overlays

    :param suppress_systems: list of strings
        Remove these systems from the list; their methods are redundant
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
    systems = settings['systems']
    if 'efitviewer_ods' in out:
        ods = out['efitviewer_ods']
        device = out['efitviewer_ods']['dataset_description.data_entry'].get('machine', tokamak(settings['cases'][0]['device']))
    else:
        ods = None
        device = tokamak(settings['cases'][0]['device'])

    has_plot_method = list_hardware_overlay_methods()
    has_loader_method = list_available_hardware_descriptors(device)
    has_data = list_available_hardware_data(ods)

    overlays = has_plot_method and (has_loader_method or has_data)
    overlays = [overlay for overlay in overlays if overlay not in suppress_systems]

    for k in list(systems.keys()):
        if k not in overlays:
            systems.pop(k)
    for overlay in overlays:
        systems.setdefault(overlay, False)
    return


# Special overlays ------------------------------------------------------------------------------------------------
def plot_scaled_boundary_overlay(
    ax=None, device='ITER', mds_tree='', shot=0, time=0, scale=1 / 3.68, x_offset=0, y_offset=-0.88 / 3.68, **kw
):
    r"""
    Overlays the boundary of another device, including scaling and offsets

    :param ax: Axes instance

    :param device: string

    :param mds_tree: string

    :param shot: int

    :param time: numeric
        Time in ms

    :param scale: float

    :param x_offset: float
        Horizontal offset after scaling (m)

    :param y_offset: float
        Vertical offset after scaling (m)

    :param \**kw: Keywords to pass to plot()

    :return: output from plot()
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    kw.pop('t', None)  # t is ignored since we're choosing an overlay time from the settings under value
    kw.pop('ods', None)  # We don't need this,but we have to take it to have a consistent call signature

    if ax is None:
        ax = scratch.get('efitviewer_ax', None)
    if ax is None:
        ax = gca()

    if is_device(device, 'ITER'):
        dat = np.genfromtxt(os.sep.join([OMFITsrc, '..', 'samples', 'iter_BL2010_Gribov.txt']), skip_header=3)
        r = dat[:, 0] * abs(scale) + x_offset
        z = dat[:, 1] * scale + y_offset
        label = 'Scaled ITER'
    else:
        eq_dat = read_basic_eq_from_mds(
            device=device,
            shot=shot,
            tree=mds_tree,
            g_file_quantities=['RBBBS', 'ZBBBS'],
            a_file_quantities=[],
            measurements=[],
            other_results=[],
            derived_quantities=['time'],
        )
        it = closestIndex(eq_dat['time'], time)
        r = eq_dat['RBBBS'][it, :] * scale + x_offset
        z = eq_dat['ZBBBS'][it, :] * scale + y_offset
        btime = eq_dat['time'][it]
        label = 'Scaled {}#{} @ {}'.format(device, shot, btime)

    kw.setdefault('label', label)
    return ax.plot(r, z, **kw)


def plot_beam_emission_spectroscopy_overlay(ax=None, ods=None, **kw):
    r"""
    Overlays measurement positions for the Beam Emission Spectroscopy (BES) diagnostic for DIII-D

    :param ax: Axes instance

    :param ods: ODS instance (for confirming device and getting shot)

    :param \**kw: Keywords to pass to plot, such as color, marker, etc.

    :return: output from plot() call
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if ods is None:
        ods = out.get('efitviewer_ods', None)
    if ods is None:
        return
    device = tokamak(ods['dataset_description.data_entry'].get('machine', settings['cases'][0]['device']))
    if not is_device(device, 'DIII-D'):
        printe('beam_emission_spectroscopy overlay supports DIII-D only, sorry. Aborting and deactivating.')
        settings['special_systems']['beam_emission_spectroscopy'] = False
        return

    shot = ods['dataset_description.data_entry'].get('.pulse', evalExpr(settings['cases'][0]['shot']))

    if ax is None:
        ax = scratch.get('efitviewer_ax', None)
    if ax is None:
        ax = gca()

    kw.pop('t', None)  # t is ignored for BES since the configuration doesn't change in time
    kw.pop('value', None)  # The BES activation flag doesn't carry special information that we need to consider

    # noinspection PyBroadException
    try:
        from omfit_classes.omfit_mds import OMFITmdsValue

        r = OMFITmdsValue(device, shot=shot, TDI='BES_R').data() / 100.0
        z = OMFITmdsValue(device, shot=shot, TDI='BES_Z').data() / 100.0
    except Exception:
        printe('BES data acquisition failed for {}#{}. Aborting and deactivating.'.format(device, shot))
        settings['special_systems']['beam_emission_spectroscopy'] = False
        report = ''.join(traceback.format_exception(*sys.exc_info()))
        printe(report)
        return
    kw.setdefault('marker', 's')
    kw.setdefault('linestyle', ' ')
    kw.setdefault('label', 'BES')
    return ax.plot(r, z, **kw)


def plot_custom_script_overlay(ax=None, ods=None, defaultvars_keywords=None, **kw):
    r"""
    Calls a script to draw a custom overlay or set of overlays.
    The script should use defaultVars() to accept the following keywords at minimum:
        ax
        ods

    :param ax: Axes instance [optional]
        If not provided, the custom script had better have a way of choosing.
        The default axes when using the efitviewer GUI are referenced in scratch.get('efitviewer_ax', None)

    :param ods: ODS instance

    :param defaultvars_keywords: dict
        Keywords to pass to script's defaultVars()

    :param \**kw: additional keywords accepted to avoid problems (ignored)
    """
    if ods is None:
        out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
        ods = out.get('efitviewer_ods', None)
    script_loc = kw.pop('script_loc', None)
    if script_loc is None:
        printe('Invalid script location. Cannot call custom script overlay.')
    printd('    efitviewer lib plot_custom_script_overlay: script_loc = {}'.format(repr(script_loc)))
    script = eval(script_loc)
    if defaultvars_keywords is None:
        defaultvars_keywords = {}
    script.runNoGUI(ax=ax, ods=ods, **defaultvars_keywords)
    return


def plot_alt_limiter_overlay(ax=None, **kw):
    """
    Plots an alternative limiter overlay

    :param ax: Axes instance

    :param kw: Additional keywords

    :return: output from plot() call
    """
    # Extract kw
    ignore_kw = ['t', 'value', 'labelevery', 'notesize', 'mask', 'ods']  # Unused
    ignore_kw += ['retain_wall']  # This should be used elsewhere
    for ikw in ignore_kw:
        kw.pop(ikw, None)
    scale = kw.pop('scale', 1.0)
    alt_lim_loc = kw.pop('alt_limiter_data_loc', None)
    alt_lim_data = kw.pop('alt_limiter_data_array', None)

    # Get data
    if alt_lim_data is None and alt_lim_loc is None:
        return None
    elif alt_lim_data is None:
        alt_lim_data = eval(alt_lim_loc)
        lim_name = alt_lim_loc.split("'")[-2]
    else:
        lim_name = ''
    r = alt_lim_data[:, 0] * scale
    z = alt_lim_data[:, 1] * scale

    # Set up plot
    if ax is None:
        ax = scratch.get('efitviewer_ax', None)
    if ax is None:
        ax = gca()
    kw.setdefault('label', 'Alternative limiter {}'.format(lim_name))

    return ax.plot(r, z, **kw)


# Plot and plot related utilities ---------------------------------------------------------------------------------
def plot_grid(fig=None, ax=None, enable=None, grid_kw=None):
    """
    :param fig: Figure instance

    :param ax: Axes instance

    :param enable: bool

    :param grid_kw: dict
        Keywords passed to grid
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    # Get default values
    if fig is None:
        fig = scratch.get('efitviewer_fig', None)
    if enable is None:
        enable = settings.setdefault('grid_enable', False)
    if grid_kw is None:
        grid_kw = settings.setdefault('grid_kw', {})
    ax = get_axes(ax)

    # Update grid
    if enable:
        ax.grid(enable, which='major', axis='both', **grid_kw)
    else:
        ax.grid(False, which='major', axis='both')

    # Make sure the update is actually drawn
    if fig is not None:
        fig.canvas.draw()
    return


def setup_special_contours(case=0, t=None, contour_quantity=None, spacing=None, decimal_places=3):
    """
    Finds contour levels in contour_quantity to give contours that obey settings in the dictionary called spacing

    :param case: int
        Which efitviewer case / ODS instance should be selected?

    :param t: float
        Time in s, to select a time slice in equilibrium data
        Defaults to setting for the relevant case in efitviewer settings

    :param contour_quantity: string
        Quantity for output contour levels. Defaults to contour quantity in efitviewer settings.

    :param spacing: dict
        Spacing instructions; can contain:
            quantity: string
                R, psi, psi_n, S
            amount: float array
                in data units relevant to quantity
            reference: string
                Reference point.
                For flux measurements, the reference is always the boundary & this setting is ignored.
                For R, try outer_midplane. For S, try outer_lower_strike.

    :param decimal_places: int
        Round to this many decimal places
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if case == 0:
        ods = out['efitviewer_ods']
    else:
        ods = out['efitviewer_ods_{}'.format(case)]
    if t is None:
        t = settings['cases'][case]['time'] / 1000.0
    if contour_quantity is None:
        contour_quantity = settings['contour_quantity']
    if spacing is None:
        spacing = settings['special_contour_spacing']

    it = closestIndex(ods['equilibrium']['time'], t)
    eq_slice = ods['equilibrium']['time_slice'][it]

    eq_phi = eq_slice['profiles_1d']['phi']
    eq_psi = eq_slice['profiles_1d']['psi']
    eq_psi_n = np.linspace(0, 1, len(eq_psi))

    cr = eq_slice['profiles_2d'][0]['grid']['dim1']
    cz = eq_slice['profiles_2d'][0]['grid']['dim2']
    if contour_quantity in ['psi', 'PSI']:
        cq = eq_slice['profiles_2d'][0]['psi']
        cq1d = eq_psi
    elif contour_quantity in ['psin', 'PSIN', 'psi_n', 'PSI_N']:
        psi_bdry = eq_slice['global_quantities']['psi_boundary']
        psi_axis = eq_slice['global_quantities']['psi_axis']
        cq = (eq_slice['profiles_2d'][0]['psi'] - psi_axis) / (psi_bdry - psi_axis)
        cq1d = eq_psi_n
    elif contour_quantity in ['phi', 'PHI']:
        cq = eq_slice['profiles_2d'][0]['phi']
        cq1d = eq_phi
    else:
        raise ValueError('Contour quantity {} is not yet supported for this operation, sorry.'.format(contour_quantity))

    space_q = spacing.get('quantity', 'R')
    space_a = np.atleast_1d(spacing.get('amount', np.array([0, 0.01])))
    space_ref = spacing.get('reference', 'outer_midplane')
    if space_q in ['R', 'Rmaj', 'R_major', 's', 'S']:
        if space_ref.lower() in ['outer_midplane', 'omp']:
            rmaxis = eq_slice['global_quantities.magnetic_axis.r']
            zmaxis = eq_slice['global_quantities.magnetic_axis.z']
            bdry_r = eq_slice['boundary.outline.r']
            bdry_z = eq_slice['boundary.outline.z']
            wr = bdry_r > rmaxis
            r_omp = interp1d(bdry_z[wr], bdry_r[wr])(zmaxis)
            ref_r = r_omp
            ref_z = zmaxis
        elif space_ref.lower() in ['outer_lower_strike']:
            # omfit_omas.multi_efit_to_omas() loads strike points in a set order: low out, low in, up out, up in
            ref_r = eq_slice['boundary.strike_point.0.r']
            ref_z = eq_slice['boundary.strike_point.0.z']
            if np.isnan(ref_r) or np.isnan(ref_z):
                raise ValueError('Outer lower strike point not defined; might be a limited shape or just missing from ODS')
        elif space_ref.lower() in ['outer_upper_strike']:
            # omfit_omas.multi_efit_to_omas() loads strike points in a set order: low out, low in, up out, up in
            ref_r = eq_slice['boundary.strike_point.2.r']
            ref_z = eq_slice['boundary.strike_point.2.z']
            if np.isnan(ref_r) or np.isnan(ref_z):
                raise ValueError('Outer upper strike point not defined; might be a limited shape or just missing from ODS')
        else:
            raise ValueError('Unrecognized custom contour spacing reference: {}'.format(space_ref))
        if space_q in ['R', 'Rmaj', 'R_major']:
            dr = space_a
            r = ref_r + dr
            z = ref_z + dr * 0
        elif space_q in ['S', 's']:
            ds = space_a
            wallr0 = ods['wall.description_2d.0.limiter.unit.0.outline.r']
            wallz0 = ods['wall.description_2d.0.limiter.unit.0.outline.z']
            # Upsample the wall so that the nearest point will be on the right surface. Since the wall has detailed
            # features, the nearest point can be behind the true surface. For example, a strike point on the lower
            # shelf might find a closest wall point in the pump duct under the shelf. To avoid locking onto such a
            # point, put in lots of extra points along the wall contour instead.
            idx = np.linspace(0, 1, len(wallr0))
            new_idx = np.linspace(0, 1, 20 * len(wallr0))
            wallr = interp1d(idx, wallr0)(new_idx)
            wallz = interp1d(idx, wallz0)(new_idx)
            ref_dist = np.sqrt((wallr - ref_r) ** 2 + (wallz - ref_z) ** 2)
            ic = ref_dist.argmin()

            # Figure out which way the wall goes
            neighborhood = np.arange(ic - 3, ic + 3)
            neighborhood = neighborhood[(neighborhood >= 0) & (neighborhood < len(wallr))]
            if np.nanmean(np.diff(wallr[neighborhood])) > 0:
                wall_dir = 1
            else:
                wall_dir = -1

            # Get wall coordinate
            wall_ds = np.append(0, np.sqrt(np.diff(wallr) ** 2 + np.diff(wallz) ** 2))
            wall_s = np.cumsum(wall_ds) * wall_dir
            wall_s -= wall_s[ic]

            # Get s coordinates of requested contour levels
            if ref_r > wallr[ic]:
                ref_s = ref_dist[ic]
            else:
                ref_s = -ref_dist[ic]
            s = ref_s + ds
            # Get R-Z coordinates of requested contour levels
            r = interp1d(wall_s, wallr)(s)
            z = interp1d(wall_s, wallz)(s)

        else:
            raise ValueError
        # Translate R-Z coordinates into flux surface labels (like psi, etc)
        contour_levels = (interp2d(cr, cz, cq.T, bounds_error=False, fill_value=np.NaN)(r, z))[0]
    elif space_q.lower() == 'psi':
        psi_levels = eq_slice['global_quantities']['psi_boundary'] + space_a
        contour_levels = interp1d(eq_psi, cq1d)(psi_levels)
    elif space_q.lower() in ['psi_n', 'psin']:
        psin_levels = 1 + space_a
        contour_levels = interp1d(eq_psi_n, cq1d)(psin_levels)
    else:
        raise ValueError('Unrecognized quantity for spacing contours: {}'.format(space_q))

    return np.round(contour_levels, decimal_places)


def get_axes(ax=None):
    """
    Choose the best plot axes to use

    :param ax: Axes instance [optional]
        If not specified, try to use efitviewer GUI's embedded axes. If those are not active, use gca().

    :return: Axes instance
    """
    if ax is None:
        out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

        printd('plot_single_cx_ods(): trying to look up efitviewer GUI figure...', topic='efitviewer')
        ax = scratch.get('efitviewer_ax', None)
    if ax is not None:
        # Check if ax is active
        try:
            # https://stackoverflow.com/a/15311949/6605826
            tk_figure_open = ax.figure.canvas.get_tk_widget().winfo_exists()
        except Exception:
            # I assume that get_tk_widget() will fail if the backend isn't tk
            tk_figure_open = False
        # https://stackoverflow.com/a/26485683/6605826
        figure_window_open = ax.figure in list(map(pyplot.figure, pyplot.get_fignums()))

        if (not tk_figure_open) and (not figure_window_open):
            printd('plot_single_cx_ods(): efitviewer figure seems to have been closed', topic='efitviewer')
            ax = None
    if ax is None:
        printd('plot_single_cx_ods(): using gca() to find axes', topic='efitviewer')
        ax = pyplot.gca()
    return ax


def plot_style_enforcement(ax=None, plot_style=None):
    """
    Applies efitviewers plot style settings to some axes

    :param ax: Axes instance [optional]
        Axes to modify; looks up efitviewer GUI axes or gca() if not specified

    :param plot_style: dict-like [optional]
        Settings to use for modifying axes appearance
    """
    # Unpack settings and axes reference
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
    if plot_style is None:
        plot_style = settings.get('plot_style_kw', {})
    ax = get_axes(ax)
    fig = ax.figure

    # Frame
    frame_on = plot_style.setdefault('frame_on', True)
    if frame_on is not None:
        ax.set_frame_on(frame_on)

    # Aspect ratio
    aspect = plot_style.setdefault('axes_aspect', 'equal_box')
    if aspect is not None:
        if '_' in str(aspect):
            aspect_ratio, adjustable = aspect.split('_')
        elif is_numeric(aspect):
            aspect_ratio = aspect
            adjustable = None
        else:
            aspect_ratio = aspect
            adjustable = None
        ax.set_aspect(aspect_ratio, adjustable=adjustable)

    # Tick spacing
    if plot_style.setdefault('tick_spacing', 0.25) is not None:
        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(plot_style['tick_spacing']))
        ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(plot_style['tick_spacing']))

    # Tick position
    ax.xaxis.set_ticks_position(plot_style.setdefault('xtick_loc', 'both'))
    ax.yaxis.set_ticks_position(plot_style.setdefault('ytick_loc', 'both'))

    # Grid
    plot_grid(fig=fig, ax=ax, enable=plot_style.setdefault('grid_enable', False), grid_kw=plot_style.setdefault('grid_kw', {}))

    # Annotations
    if plot_style.setdefault('subplot_label', None) is not None:
        font_size = settings.get('default_fontsize', None)
        if font_size is None:
            font_size = matplotlib.rcParams['xtick.labelsize']
        tag_plots_abc(
            fig=fig,
            axes=ax,
            start_at=plot_style.setdefault('subplot_label', 0),
            corner=plot_style.setdefault('subplot_label_corner', [1, 1]),
            font_size=font_size,
        )
    return


# Main plotting functions -----------------------------------------------------------------------------------------
def plot_cx_ods(ods_idx=None, odss=None, cases=None, **kw):
    r"""
    Wrapper for making multiple calls to plot_single_cx_ods()

    :param ods_idx: int or list of ints [optional]
        You should probably let it do its default behavior, but you can override it if you need to.

    :param odss: dict [optional]
        Keys are int matching entries in ods_idx
        Values are ODS instances.
        This is for overriding ODSs in the tree to support some very specific operations and is
        not recommended for most purposes.

    :param cases: dict-like [optional]
        Dictionary with entries foe each index in ods_idx specifying time (float or float array) and active (bool)

    :param \**kw: Additional keywords passed to plot_single_cx_ods() for 0th case.
        See docstring for plot_single_cx_ods.
        If you have overridden ods with your own list, the first entry in the list gets all the keywords, and
        subsequent entries get a subset.

    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if cases is None:
        cases = settings['cases']
    if ods_idx is None:
        # Default automatic selection of ods indices to loop over
        ods_idx = []
        for idx in cases:
            # Collect indices of active cases to overlay
            if cases[idx].get('active', True) or idx == 0:
                ods_idx += [idx]
    if odss is None:
        odss = {k: None for k in ods_idx}

    tkw = kw.pop('t', None)
    first_only = ['overlays', 'special_overlays', 'customization']
    clear_first = kw.pop('clear_first', None)
    kw2 = copy.copy(kw)
    for fkw in first_only:
        kw2.pop(fkw, None)
    kw2['overlays'] = {}
    kw2['special_overlays'] = {}

    for i, idx in enumerate(tolist(ods_idx)):
        # Special call for the primary ODS
        printd('plot_single_cx_odx() call for equilibrium slice i={}, idx={}'.format(i, idx))
        if len(tolist(ods_idx)) <= 1:
            use_kw = kw
            printd('  allowing overlay instructions in this call instead of doing separately at the end')
        else:
            use_kw = kw2
            printd('  no overlay instructions yet; must repeat at the end')
        plot_single_cx_ods(
            ods_idx=idx,
            ods=odss[idx],
            multi_cases=len(tolist(ods_idx)) > 1,
            t=cases[idx].get('time', None) if tkw is None else tkw,
            eq_active=cases[idx].get('active', True),
            wall_active=cases[idx].get('wall', True),
            clear_first=clear_first and (i == 0),
            eqkw=cases[idx].get('eqkw', {}),
            xkw=cases[idx].get('xkw', dict(marker='x')),
            **use_kw,
        )
    if len(tolist(ods_idx)) > 1:
        # Diagnostic overlays from first ODS
        printd('  extra overlay call at the end for diagnostics')
        plot_single_cx_ods(
            ods_idx=0,
            ods=odss[0],
            multi_cases=len(tolist(ods_idx)) > 1,
            t=cases[0].get('time', None) if tkw is None else tkw,
            eq_active=False,
            wall_active=False,
            **kw,
        )
    return


def plot_single_cx_ods(
    ax=None,
    ods_idx=0,
    multi_cases=False,
    ods=None,
    t=None,
    overlays=None,
    special_overlays=None,
    clear_first=False,
    gentle=False,
    contour_quantity=None,
    allow_fallback=None,
    levels=None,
    contour_resample_factor=None,
    xlim=None,
    ylim=None,
    customization=None,
    default_fontsize=None,
    show_legend=None,
    show_cornernote=None,
    eq_active=None,
    wall_active=None,
    plot_style_kw=None,
    eqkw=None,
    xkw=None,
):
    """
    Plots efitviewer-style cross section with overlays

    If data for an overlay are missing, they will be added before plotting

    :param ax: Axes instance
        Axes to draw on. Defaults to gca() if not specified.

    :param ods_idx: int
        For looking up which group of settings to use, & for looking up which ODS to use, if ods is not overridden.

    :param multi_cases: bool
        Set up for supporting multi-case overlay. Affects how some annotations are drawn.
        Does not actually do multiple cases in this call.

    :param ods: ODS instance
        This is the source of data. At minimum, it should contain equilibrium data for plotting contours.

    :param t: numeric scalar or iterable
        Time slice(s) of interest (ms). Control multi-slice overlays by passing a list or array.

    :param overlays: dict
        Dictionary with keys matching standard hardware systems and bool keys to activate overlays of those systems

    :param special_overlays: dict
        Dictionary with keys matching special hardware overlays
        Each function should accept ax, ods, t, and value

    :param clear_first: bool
        Clears Axes before plotting. Use for quickly updating the same plot embedded in a GUI.

    :param gentle: bool
        Prints exception reports instead of raising exceptions.
        Use to prevent a whole GUI system from going down on a failed plot.

    :param contour_quantity: string
        Options: psi (poloidal mag flux), rho (sqrt of toroidal mag flux), or phi (toroidal mag flux)

    :param allow_fallback: bool
        If rho/psi/phi isn't available, allow fallback to something that is

    :param levels: numeric iterable
        Contour levels

    :param contour_resample_factor: int
        Upsample 2d data to improve contour smoothness

    :param xlim: two element sorted numeric iterable

    :param ylim: two element sorted numeric iterable

    :param customization: dict-like
        Each key should match the name of an overlay, like 'scaled_boundary' or 'gas_injection'.
        The values should be dict-like and contain keywords and values to pass to the overlay
        functions. Some of these keywords have been standardized, but others are specific
        to individual plot overlay functions. The GUI will interpret function docstrings
        to provide entries for setting these up properly.

    :param default_fontsize: float

    :param show_legend: int
        0: prevent legend, even if it's a good idea
        1: do legend even if other annotations could probably cover it
        2: auto select: do legend for multi-cases only

    :param show_cornernote: int
        0: prevent cornernote, even if it's a good idea
        1: do cornernote based on primary case even if it might be not be the best idea
            (like if it mismatches with other cases that are also shown)
        2: auto select: do cornernote for single case only

    :param eq_active: bool
        Equilibrium overlay active?

    :param wall_active: bool
        Wall overlay active / included in eq overlay?

    :param plot_style_kw: dict-like
        Settings for enforcing plot axes style

    :param eqkw: dict-like
        Customization options for equilibrium overlay contours,
        passed to plot for boundary & contour for flux surfaces

    :param xkw: dict-like
        Customization options for equilibrium overlay's x-point, such as marker, color, markersize, mew, ...
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if ods is None:
        printd('plot_single_cx_ods(): no ODS passed; must try to look up...', topic='efitviewer')
        if ods_idx == 0:
            ods_tag = 'efitviewer_ods'
        else:
            ods_tag = 'efitviewer_ods_{}'.format(ods_idx)
        ods = out.get(ods_tag, None)
        printd('plot_single_cx_ods(): tried to get tag {} from {}'.format(ods_tag, out_loc), topic='efitviewer')
    else:
        printd('plot_single_cx_ods(): ODS was received; no auto-lookup', topic='efitviewer')
        ods_tag = None
    if ods is None:
        printd('plot_single_cx_ods(): ODS is still None after trying auto-lookup; aborting.', topic='efitviewer')
        return
    printd('plot_single_cx_ods(): ODS is okay now.', topic='efitviewer')

    timing_ref = None  # time.time()  # If this is not None, timing information will be printed
    if timing_ref is not None:
        printe('-' * 80)

    ax = get_axes(ax)
    fig = ax.figure
    if clear_first:
        ax.cla()

    # noinspection PyBroadException
    try:
        assert 'equilibrium' in ods, 'No equilibrium data. Cannot plot.'
        assert 'time' in ods['equilibrium'], 'No time in equilibrium.'

        # Resolve keyword default values
        if contour_quantity is None:
            contour_quantity = settings.setdefault('contour_quantity', 'psi')
        if allow_fallback is None:
            allow_fallback = settings.setdefault('allow_fallback', False)
        if levels is None:
            levels = settings['{}_levels'.format(contour_quantity)]
        if contour_resample_factor is None:
            contour_resample_factor = settings['contour_resample_factor']
        if xlim is None:
            xlim = settings['xlim']
        if ylim is None:
            ylim = settings['ylim']
        if overlays is None:
            overlays = settings['systems']
        if special_overlays is None:
            special_overlays = settings['special_systems']
        if t is None:
            t = evalExpr(settings['cases'][ods_idx]['time'])
        if customization is None:
            customization = settings['co_efv']
        if default_fontsize is None:
            default_fontsize = settings.get('default_fontsize', None)
        if show_legend is None:
            show_legend = settings.setdefault('show_legend', 2)
        if show_cornernote is None:
            show_cornernote = settings.setdefault('show_cornernote', 2)
        if eq_active is None:
            eq_active = settings['cases'][ods_idx]['active']
        if wall_active is None:
            wall_active = settings['cases'][ods_idx].get('wall', True)
        if plot_style_kw is None:
            plot_style_kw = settings.setdefault('plot_style_kw', {})
        if eqkw is None:
            eqkw = settings['cases'][ods_idx].get('eqkw', {})
        if xkw is None:
            xkw = settings['cases'][ods_idx].get('xkw', {'marker': 'x'})

        if timing_ref is not None:
            print(time.time() - timing_ref, 'omfitlib efitviewer unpack stuff')

        # Get machine and shot info
        device = tokamak(ods['dataset_description.data_entry'].get('machine', settings['cases'][0]['device']))
        shot = ods['dataset_description.data_entry'].get('pulse', evalExpr(settings['cases'][0]['shot']))
        try:
            efitid = ods['dataset_description.ids_properties.comment'].split('EFIT tree = ')[-1]
        except ValueError:
            efitid = ''
        if t is None:
            printd('plot_single_cx_ods{}: t is None; aborting...', topic='efitviewer')
            return
        t = np.atleast_1d(t)

        printd('ods_idx', ods_idx, 'ods_tag', ods_tag, 't', t)

        # Gather overlay information as needed
        for overlay, overlay_active in overlays.items():
            printd(
                'checking overlay {}; active = {}, in ods = {}, in pulse_schedule: {}'.format(
                    overlay, overlay_active, overlay in ods, overlay in ods['pulse_schedule']
                )
            )
            if overlay_active and (overlay not in ods) and (overlay not in ods['pulse_schedule']):
                printd('  Need to add missing overlay data: {}'.format(overlay))
                add_hardware_to_ods(ods, device, shot, overlay)

        if timing_ref is not None:
            print(time.time() - timing_ref, 'omfitlib efitviewer add missing data')

        # Plot equilibrium time-slice(s)
        if eq_active:
            printd('plot_single_cx_ods{}: this eq slice is active; trying to plot', topic='efitviewer')
            it = None
            for t_ in t:
                if t_ is None:
                    it = 0
                else:
                    it = closestIndex(ods['equilibrium.time'] * 1000, t_)
                # Set up keywords for equilibrium_CX
                if multi_cases:
                    eqcx_label = 'eq#{}: {}#{} {} {:0.1f} ms'.format(ods_idx, device, shot, efitid, ods['equilibrium.time'][it] * 1000)
                else:
                    eqcx_label = 'Equilibrium {:0.1f} ms'.format(ods['equilibrium.time'][it] * 1000)
                eqcx_label = eqkw.pop('label', eqcx_label)
                eqcxkw = dict(
                    ax=ax,
                    time_index=it,
                    levels=levels,
                    label=eqcx_label,
                    contour_quantity=contour_quantity,
                    allow_fallback=allow_fallback,
                    sf=contour_resample_factor,
                    xkw=xkw,
                    show_wall=(
                        (not special_overlays.get('alt_limiter', False)) or customization.get('alt_limiter', {}).get('retain_wall', True)
                    )
                    and wall_active,
                    **eqkw,
                )
                # Remove unsupported keywords based on omas version
                for kw, ver in omas_features.items():
                    if compare_version(ver, omas.__version__) > 0:
                        # Version required to support this keyword is newer than the OMAS version in use, so skip.
                        eqcxkw.pop(kw, None)

                ods.plot_equilibrium_CX(**eqcxkw)  # The call to draw the equilibrium contours
        else:
            printd('plot_single_cx_ods{}: this eq slice is INACTIVE; skipping eq plot', topic='efitviewer')
            it = 0
            ax.set_aspect('equal')
            ax.set_frame_on(False)
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')

        def overlay_customizations(ovls):
            ovls = dict(ovls)
            for ovl in ovls:
                if ovls[ovl] and ovl in customization:
                    # Replace "True" w/ custom overlay instructions (if present) but first do some processing
                    custom = dict(customization[ovl])
                    for item in list(custom.keys()):
                        # Remove "None", since we were too busy to look up real defaults & they might not be None
                        if custom[item] is None:
                            if item == 't':
                                custom[item] = t * 1e-3
                            else:
                                custom.pop(item, None)
                        if item.startswith('pass_in_keywords_'):
                            pikw = custom.pop(item, {})
                            custom.update(pikw)
                    # Special debugging
                    if ovl in ['position_control', 'pulse_schedule']:
                        custom['timing_ref'] = timing_ref
                    # Custom instructions ready
                    if len(custom):
                        ovls[ovl] = custom
                    else:
                        ovls[ovl] = True
            return ovls

        # Plot hardware overlay(s)
        overlays = overlay_customizations(overlays)
        scratch['overlays'] = overlays
        old_font_size = copy.copy(rcParams['font.size'])
        if default_fontsize is not None:
            try:
                rcParams['font.size'] = default_fontsize
            except ValueError as exc:
                printe(f"Could not set rcParams['font.size'] = {repr(default_fontsize)} " f"(default_fontsize), because of {exc}")

        scratch['overlays'] = overlays
        # Thomson scattering has a different default than others, so we must make sure blank is replaced by False
        overlays.setdefault('thomson_scattering', False)
        ods.plot_overlay(ax=ax, **overlays)  # The call to do the overlays

        # Plot special hardware overlay(s)
        special_overlays = overlay_customizations(special_overlays)
        scratch['special_overlays'] = special_overlays
        for so, soa in special_overlays.items():
            if soa:
                skw = soa if isinstance(soa, dict) else {}
                function_name = 'plot_{}_overlay'.format(so)
                try:
                    special_function = eval(function_name)
                except NameError:
                    printe('Unrecognized special overlay: {} has no function (expected {})'.format(so, function_name))
                else:
                    special_function(ax=ax, ods=ods, **skw)

        # Annotations and finishing touches
        actually_show_legend = (multi_cases and (show_legend > 0)) or (show_legend == 1)
        actually_show_cornernote = (not multi_cases and (show_cornernote > 0)) or (show_cornernote == 1)
        if actually_show_legend:
            ax.legend(loc=0)
        if actually_show_cornernote:
            cornernote(
                ax=ax,
                device=device,
                shot='{} {}'.format(shot, efitid),
                time='{:0.2f}'.format(ods['equilibrium.time'][it] * 1000) if len(t) == 1 else ' ',
            )
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)
        if len(t) > 1:
            ax.legend(loc=3)

        plot_style_enforcement(ax=ax, plot_style=plot_style_kw)

        if default_fontsize is not None:
            rcParams['font.size'] = old_font_size

        # Make sure it draws
        if fig is not None:
            fig.canvas.draw()
        printd('plot_single_cx_ods{}: finished plot attempts with no exceptions to catch', topic='efitviewer')

    except Exception:
        printd('plot_single_cx_ods{}: exception while trying to plot...', topic='efitviewer')
        if gentle:
            # Display the error instead of bringing the whole GUI down if the plot fails.
            print('Error in plot_cx:')
            report = ''.join(traceback.format_exception(*sys.exc_info()))
            printe(report)
            # noinspection PyBroadException
            try:
                if ax is None:
                    ax = gca()
                if clear_first:
                    ax.cla()
                ax.text(0.05, 0.95, report, ha='left', va='top', color='red')
            except Exception:
                printd('plot_single_cx_ods{}: Failed to properly report an exception!', topic='efitviewer')
        else:
            raise

    return


# Export ----------------------------------------------------------------------------------------------------------
def dump_plot_command_content():
    """
    Writes the contents of a script for reproducing the equilibrium cross section plot based on current settings

    :return: string
        Source code for a script that will reproduce the plot
    """

    import getpass
    import socket

    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    ods = out['efitviewer_ods']
    device = tokamak(ods['dataset_description.data_entry'].get('machine', settings['cases'][0]['device']))
    shot = ods['dataset_description.data_entry'].get('pulse', evalExpr(settings['cases'][0]['shot']))
    case_defaults = dict(time=0, active=True, wall=True, eqkw={}, xkw=dict(marker='x'))
    cases = {k: {kk: v.get(kk, case_defaults.get(kk, None)) for kk in v} for k, v in settings['cases'].items()}

    overlays = {k: v for k, v in settings['systems'].items() if v}
    special_overlays = {k: v for k, v in settings['special_systems'].items() if v}
    all_ovl = copy.copy(overlays)
    all_ovl.update(special_overlays)
    default_fontsize = settings.get('default_fontsize', None)

    customization = {}
    for k, v in settings['co_efv'].items():
        if all_ovl.get(k, False):
            customization[k] = {kk: vv for kk, vv in v.items() if (vv is not None) or (kk == 't')}
            for kk in list(customization[k].keys()):  # List first because the dict could change during the loop
                if kk.startswith('pass_in') and len(customization[k][kk]) == 0:
                    # Remove empty pass_in_keywords / pass_in_args since they are nothing but clutter
                    customization[k].pop(kk, None)

    # Create a string that contains load instructions so it evaluates into a dict containing ODS instances
    load_instructions_dict = {index: settings['cases'][index].get('instructions_for_loading_ods', 'None') for index in settings['cases']}
    load_instructions_string = {index: 'replace_{}'.format(index) for index in settings['cases']}
    load_instructions_string = repr(load_instructions_string)
    for index in settings['cases']:
        load_instructions_string = load_instructions_string.replace("'replace_{}'".format(index), load_instructions_dict[index])

    contents = '''def plot_eq_cx():
    """
    Plots an equilibrium slice with a specific configuration of hardware overlay(s)

    Automatically generated function output by efitviewer. Please save this file somewhere permanent to avoid losing it.

    Generated {date:} by {user:} on {host:}
    OMFIT version: {omfit_version:}
    """

    from omfit_classes.omfit_efitviewer import plot_cx_ods
    device = {device:}
    shot = {shot:}
    cases = {cases:}
    odss = {load_instructions:}
    fig, ax = pyplot.subplots(1)
    levels = {levels:}
    customization = {customization:}
    plot_cx_ods(
        ax=ax,
        odss=odss,
        cases=cases,
        contour_quantity={contour_quantity:},
        allow_fallback={allow_fallback:},
        levels=levels,
        plot_style_kw={plot_style_kw:},
        contour_resample_factor={contour_resample_factor:},
        xlim={xlim:},
        ylim={ylim:},
        overlays={overlays:},
        special_overlays={special_overlays:},
        customization=customization,
        default_fontsize={default_fontsize:},
        show_legend={show_legend:},
    )
    return

    '''.format(
        device=repr(device),
        shot=repr(shot),
        cases=repr(cases),
        load_instructions=load_instructions_string,
        contour_quantity=repr(settings['contour_quantity']),
        allow_fallback=repr(settings['allow_fallback']),
        levels=repr(settings['{}_levels'.format(settings['contour_quantity'])]),
        plot_style_kw=settings.setdefault('plot_style_kw', {}),
        contour_resample_factor=settings['contour_resample_factor'],
        xlim=repr(settings['xlim']),
        ylim=repr(settings['ylim']),
        overlays=repr(overlays),
        special_overlays=repr(special_overlays),
        customization=repr(customization),
        date=datetime.datetime.now(),
        user=getpass.getuser(),
        host=socket.gethostname(),
        omfit_version=repo.active_branch()[-1],
        default_fontsize=default_fontsize,
        show_legend=settings.setdefault('show_legend', 2),
    )
    contents += '\nplot_eq_cx()'
    contents = omfit_formatter(contents)

    print('The following commands will generate the last saved equilibrium cross section plot:\n')
    printi(contents)
    print('')

    return contents


def dump_plot_command():
    """
    Writes a script for reproducing the equilibrium cross section plot based on current settings

    :return: (OMFITpythonTask, string)
        Reference to the script and its contents
    """
    from omfit_classes.omfit_python import OMFITpythonTask

    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
    ods = out['efitviewer_ods']
    device = tokamak(ods['dataset_description.data_entry'].get('machine', settings['cases'][0]['device']))
    shot = ods['dataset_description.data_entry'].get('pulse', evalExpr(settings['cases'][0]['shot']))
    filename = settings.setdefault('export_script_filename', "saved_eq_cx_plot_{}_{}".format(device, shot))
    ext = os.extsep + 'py'
    if filename.endswith(ext):
        filename = filename[: -len(ext)]
    contents = dump_plot_command_content()
    script = out[filename] = OMFITpythonTask(filename + ext, fromString=contents)
    print("Script saved to out['{}']".format(filename))
    return script, contents


def box_plot_command(number=None, location=None):
    """
    Puts commands for reproducing the plot into the command box

    :param number: int
        Index (not visible number) of the command box to edit.
        Although normally an int, there are some special values:
            None: get number from location instead
            'new', 'New', or -1: create a new command box and use its number

    :param location: string
        Location in the tree where the command box number (not index) is stored

    :return: string
        String written to command box
    """
    if number is None:
        number_plus_1 = eval(location)
        number = number_plus_1 - 1 if is_numeric(number_plus_1) else number_plus_1
    if str(number).lower().startswith('new') or (number is None) or (is_numeric(number) and number < 0):
        number = add_command_box_tab()
    assert is_numeric(number)
    assert number >= 0
    contents = dump_plot_command_content()
    prior_cmd_box_contents = OMFITaux['GUI'].command[number].get()
    printw('Contents of command box index {}, #{} prior to overwriting with plot script:'.format(number, number + 1))
    printw('-' * 80)
    print(prior_cmd_box_contents)
    printw('-' * 80)
    printw('End of prior command box contents')
    OMFITaux['GUI'].command[number].set(contents)
    return contents


# GUI helpers -----------------------------------------------------------------------------------------------------
def add_case():
    """Extends the cases available for overlay by adding one case to the end"""
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    new_idx = np.max(list(settings['cases'].keys())) + 1
    settings['cases'][int(new_idx)] = SettingsName()  # new_idx must be int, not np.int64
    return


def delete_case(idx):
    """
    Removes a case from the list

    :param idx: int
        Index of case to delete

    :return: new_max: int
        New maximum case index, in case you wanted to know
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    assert idx > 0, "You're not allowed to delete the primary case. Naughty!"
    del settings['cases'][idx]
    new_max = np.max(list(settings['cases'].keys()))
    return new_max


def update_cx_time(location, index=None):
    """
    Updates list of times to use for overlays.
    In this way, the plot can be updated to add/remove diagnostics without forgetting time-slice overlay setup.

    :param location: string
        Location in the OMFITtree of the setting that changed to trigger the overlay update

    :param index: int
        Index of the case to update
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    printd(f'update_cx_time: {location}, index={index}', topic='efitviewer')
    new_time = eval(location)
    if index is None:
        try:
            index = int(location.split("['cases'][")[-1].split("]['time']")[0])
        except ValueError:
            try:
                index = int(location.split("scratch']['efitviewer_")[-1].split("_")[0])
            except ValueError:
                index = int(location.split("__scratch__']['efitviewer_")[-1].split("_")[0])
        printd(f'  update_cx_time: location = {location:}, index = {index:}', topic='efitviewer')
    if settings['overlay']:
        new_times = np.append(np.atleast_1d(settings['cases'].setdefault(index, SettingsName()).setdefault('time', None)), new_time)
    else:
        new_times = np.atleast_1d(new_time)
    settings['cases'].setdefault(index, SettingsName())['time'] = new_times

    plot_cx_ods(clear_first=True)
    return


def update_gui_figure(location=None, **kw):
    r"""
    Handle updates to the figure embedded in the GUI while setting defaults for appropriate keywords

    :param location: string
        Location in the OMFITtree of the setting that changed to trigger the overlay update

    :param \**kw: Additional keywords passed to plot_cx_ods
        You can override defaults
    """
    printd('updating figure after changing location: {}'.format(location))
    kw.setdefault('clear_first', True)
    kw.setdefault('gentle', True)
    plot_cx_ods(**kw)
    return


def update_overlay(location):
    """
    Updates times when overlay changes; used to clear old overlays when exiting overlay mode

    :param location: string
        Location in the OMFITtree of the setting that changed to trigger the overlay update
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    overlay = eval(location)
    if not overlay:
        for idx in settings['cases']:
            new_times = np.atleast_1d(settings['cases'][idx]['time'])[-1]
            settings['cases'][idx]['time'] = new_times
        update_gui_figure()
    return


def default_xylim(dev=None):
    """Updates current settings to match device defaults"""
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if dev is None:
        try:
            dev = out['efitviewer_ods']['dataset_description.data_entry.machine']
        except (KeyError, ValueError):
            dev = tokamak(settings['cases'][0]['device'])
    default_xlim = default_plot_limits.get(dev, {}).get('x', None)
    default_ylim = default_plot_limits.get(dev, {}).get('y', None)
    settings['xlim'] = default_xlim
    settings['ylim'] = default_ylim
    update_gui_figure()
    return


def grab_xylim(decimals=None):
    """
    Grabs current figure limits and updates settings so updated plots will preserve limits

    :param decimals: int
        How many decimal places to retain while rounding

    :return: xlim, ylim
        They are loaded into settings, so catching the return is not necessary
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if decimals is None:
        decimals = settings.setdefault('xylim_grab_rounding_decimals', 3)

    def proccess_lim(a):
        if decimals is None or decimals < 0:
            return a
        return tuple([np.round(aa, decimals) if is_numeric(aa) else aa for aa in np.atleast_1d(a)])

    ax = scratch.get('efitviewer_ax', None)
    if ax is not None:
        xlim = proccess_lim(ax.get_xlim())
        ylim = proccess_lim(ax.get_ylim())
        settings['xlim'] = xlim
        settings['ylim'] = ylim
    else:
        xlim = ylim = None
    return xlim, ylim


def load_contours():
    """
    Loads contours specified by custom_contour_spacing setup

    :return: float array of contour levels
        They are loaded into SETTINGS so you don't have to catch this, but you can, if you want to.
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    cq = settings['contour_quantity']
    cq_in = dict(psi='psin').get(cq, cq)
    spacing = settings['custom_contour_spacing']
    levels = setup_special_contours(contour_quantity=cq_in, spacing=spacing)
    settings['{}_levels'.format(cq)] = levels
    return levels


def get_default_snap_list(device):
    """
    Guess default snap list based on device
    :param device: str
    :return: dict
    """
    guesses = {'EAST': {'EFIT_EAST': 'EFIT_EAST'}, 'KSTAR': {'EFIT01': 'EFIT01', 'EFITRT1': 'EFITRT1'}}
    guesses['EAST_US'] = guesses['EAST']
    for gd in guesses.keys():
        if is_device(device, gd):
            return guesses[gd]
    return {}
