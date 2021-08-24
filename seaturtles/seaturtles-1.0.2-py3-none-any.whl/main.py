"""
main.py
======================================
Author: Anne Hulsey, 2021, University of Auckland

The core module of the TURtLES package
"""

from .base import *
from .constants import *


def create_eqhazard_input(eq_input_file, rupture_dict, sites, gmm, sa_periods):
    """
    Creates the input file for EQHazard

    Parameters
    ----------
    eq_input_file: string
        name of the input file

    rupture_dict: dict
        includes the ERF, source idx and rupture idx

    sites: pd dataframe
        includes the site locations and Vs30

    gmm: string
        name of the selected ground motion model

    sa_periods: list
        periods of interest

    """
    rupture_forecast = rupture_dict['rupture_forecast']
    source_idx = rupture_dict['source_idx']
    rupture_idx = rupture_dict['rupture_idx']

    n_sites = len(sites)

    eq_hazard = dict()
    eq_hazard['Site'] = {'Type': 'SiteList'}
    site_list = [{'Location': {'Latitude': sites.loc[i, 'Latitude'], 'Longitude': sites.loc[i, 'Longitude']},
                  'Vs30': int(sites.loc[i, 'Vs30'])} for i in range(n_sites)]
    eq_hazard['Site']['SiteList'] = site_list

    eq_hazard['EqRupture'] = {'Type': 'ERF',
                              'RuptureForecast': rupture_forecast,
                              'SourceIndex': source_idx,
                              'RuptureIndex': rupture_idx,
                              }

    eq_hazard['GMPE'] = {'Type': gmm, 'Parameters': {}}

    eq_hazard['IntensityMeasure'] = {'Type': 'SA',
                                     'Periods': sa_periods,
                                     'EnableJsonOutput': True,
                                     'EnableCsvOutput': False,
                                     'EnableGeoJsonOutput': False}

    with open(eq_input_file, 'w') as f:
        json.dump(eq_hazard, f, indent=4)


def run_EQHazard(input_file, output_file):
    """
    Runs SimCenter's EQHazard tool

         The EQHazard tool documentation is available at:
         https://github.com/NHERI-SimCenter/GroundMotionUtilities/tree/master/EQHazard

    Parameters
    ----------
    input_file: string
        name of a json file following the EQHazard specifications
            with EnableJsonOutput = True

    """

    try:
        command_run = subprocess.call(['java', '-jar', '-mx1g', EQHazard_file, input_file, output_file])

        if command_run == 0:
            print('EQHazard ran successfully.')
        else:
            print('There was a problem running the EQHazard.jar file, start troubleshooting.')
            print('\tFor example, check your allowable heap size (may need to reduce it from the current -mx1g).')

    except:
        print('There was a problem running the EQHazard.jar file. Check that Java is installed.')



def extract_eqhazard_data(input_file, output_file):
    """
    Runs SimCenter's EQHazard tool and extracts the data in the desired format

         The EQHazard tool documentation is available at:
         https://github.com/NHERI-SimCenter/GroundMotionUtilities/tree/master/EQHazard

         Notes:
             This code assumes that the input file calls for spectral accelerations
                   as the intensity measure (IM) of interest

             For clarity, EQHazard's
                   IntraEvStdDev is renamed as WithinEvStdDev and
                   InterEvStdDev is renamed as BetweenEvStdDev

    Parameters
    ----------
    input_file: string
        name of a json file following the EQHazard specifications
            with EnableJsonOutput = True

    output_file: string
        name of a new .h5 file containing the following dsets:
            Ruptures (contains metadata of the ruptures considered)
            Sites    (contains site locations and Vs30)
            Periods  (contains the periods considered for Sa(T))
            Medians  (the median predicted Sa(T) value for each rupture, site, and period)
            TotalStdDeviations (for each rupture, site, and period)
            WithinEvStdDev     (for each rupture, site, and period)
            BetweenEvStdDev    (for each rupture, site, and period)

    """
    # prepare an intermediate filename for EQHazard output
    eqhazard_output = output_file.replace('.h5', '.json')

    # run EQHazard
    run_EQHazard(input_file, eqhazard_output)

    # open the EQHazard output
    with open(eqhazard_output, 'r') as inFile:
        eqhazard = json.load(inFile)

    # extract the rupture metadata
    df = pd.DataFrame()
    df['Magnitude'] = [eqhazard['EqRupture']['Magnitude']]
    df['SourceIndex'] = [eqhazard['EqRupture']['SourceIndex']]
    df['RuptureIndex'] = [eqhazard['EqRupture']['RuptureIndex']]
    df.to_hdf(output_file, key='Ruptures', mode='w')
    n_rups = len(df)

    # extract the site metadata
    n_sites = len(eqhazard['GroundMotions'])
    df = pd.DataFrame()
    df['Latitude'] = [eqhazard['GroundMotions'][i]['Location']['Latitude'] for i in range(n_sites)]
    df['Longitude'] = [eqhazard['GroundMotions'][i]['Location']['Longitude'] for i in range(n_sites)]
    df['Vs30'] = [eqhazard['GroundMotions'][i]['SiteData'][0]['Value'] for i in range(n_sites)]
    df.to_hdf(output_file, key='Sites', mode='r+')

    # extract the Sa(T) periods
    n_periods = len(eqhazard['Periods'])
    with h5py.File(output_file, 'r+') as hf:
        hf.create_dataset('Periods', data=eqhazard['Periods'])

    # extract the ground motion medians and std deviations
    gm_size = [n_rups, n_sites, n_periods]
    median = np.empty(gm_size)
    total_std_dev = np.empty(gm_size)
    within_ev_std_dev = np.empty(gm_size)
    between_ev_std_dev = np.empty(gm_size)

    for i in range(n_rups):
        median[i, :, :] = [np.exp(eqhazard['GroundMotions'][i]['lnSA']['Mean']) for i in range(n_sites)]
        total_std_dev[i, :, :] = [eqhazard['GroundMotions'][i]['lnSA']['TotalStdDev'] for i in range(n_sites)]
        within_ev_std_dev[i, :, :] = [eqhazard['GroundMotions'][i]['lnSA']['IntraEvStdDev'] for i in range(n_sites)]
        between_ev_std_dev[i, :, :] = [eqhazard['GroundMotions'][i]['lnSA']['InterEvStdDev'] for i in range(n_sites)]

    with h5py.File(output_file, 'r+') as hf:
        hf.create_dataset('Medians', data=median)
        hf.create_dataset('TotalStdDevs', data=total_std_dev)
        hf.create_dataset('WithinEvStdDevs', data=within_ev_std_dev)
        hf.create_dataset('BetweenEvStdDevs', data=between_ev_std_dev)


def baker_jayaram_correlation(t1, t2):
    """
    Computes the correlation of epsilons for the NGA ground motion models
        modeled after Matlab code by Jack Baker, available at:
        (https://web.stanford.edu/~bakerjw/GMPEs/baker_jayaram_correlation.m)


    The function is strictly empirical, fitted over the range 0.01s <= T1, T2 <= 10s

    Documentation is provided in the following document:
    Baker, J.W. and Jayaram, N. (2008), "Correlation of spectral acceleration
    values from NGA ground motion models," Earthquake Spectra, 24 (1), 299-317.

    Parameters
    ----------
    t1, t2: float
        the two periods of interest. The periods may be equal,
        with no restriction on which one is larger

    Returns
    -------
    rho: float
        the predicted correlation coefficent between the two periods
    """

    # order the input periods
    t_min = min(t1, t2)
    t_max = max(t1, t2)

    # calculate c1
    c1 = 1 - np.cos((np.pi / 2) - 0.366 * np.log(t_max / (max(t_min, 0.109))))

    # calculate c2
    if t_max < 0.2:
        c2 = 1 - 0.105 * (1 - 1 / (1 + np.exp(100 * t_max - 5))) * ((t_max - t_min) / (t_max - 0.0099))
    else:
        c2 = 0

    # calculate c3
    if t_max < 0.109:
        c3 = c2
    else:
        c3 = c1

    # calculate c4
    c4 = c1 + 0.5 * (np.sqrt(c3) - c3) * (1 + np.cos((np.pi * t_min) / 0.109))

    # calculate rho
    if t_max < 0.109:
        rho = c2
    elif t_min > 0.109:
        rho = c1
    elif t_max < 0.2:
        rho = min(c2, c4)
    else:
        rho = c4

    return rho


def between_event_simulation(periods, n_sims):
    """

    Simulates correlated residuals for all periods, across multiple events

    Parameters
    ----------
    periods: numpy array
        periods of interest for Sa(T)

    n_sims: int
        number of events to simulate

    Returns
    -------
    residuals: numpy array
        between event residuals, shape: [n_periods, n_sims]

    """

    # calculate the empirical correlation between each period
    n_t = len(periods)
    rho = np.array([baker_jayaram_correlation(t1, t2) for t1 in periods for t2 in periods]).reshape([n_t, n_t])

    # check that the correlation matrix is symmetric
    if not np.allclose(rho, rho.T, atol=1e-8):
        raise ValueError('Correlation matrix for etas is not symmetric.')

    # simulate correlated residuals for each event
    residuals = np.random.multivariate_normal(np.zeros(n_t), rho, n_sims).T

    return residuals


def utm_conversion(lat, long):
    """
    Converts latitude and longitude coordinates to meters

    Notes:
           if the locations are not all in the same UTM zone,
                  this code will throw an error

    Parameters
    ----------
    lat, long: numpy arrays
        paired arrays of latitude and longitude, in WGS84 coordinate system

    Returns
    -------
    x,y: numpy arrays
        corresponding arrays in meters, with the origin based on the UTM zone
    """

    # convert WGS84 coordinates to meters
    x = np.empty(lat.shape)
    y = np.empty(lat.shape)
    zone = np.empty(lat.shape)
    for lat, long, i in zip(lat, long, range(len(x))):
        [x[i], y[i], zone[i], _] = utm.from_latlon(lat, long)

    # throw an error if the UTM zones are not the same
    if any(i != zone[0] for i in zone):
        raise ValueError('locations are not in the same UTM zone')

    return x, y


def isotropic_nested_covariance(variogram_pc, distance_matrix):
    """

    Calculates covariance for the current principal component, based on the distance and nugget

    Documentation is provided in the following document:
         Markhvida, M., Ceferino, L., and Baker, J. W. (2018), “Modeling spatially correlated
         spectral accelerations at multiple periods using principal component analysis and geostatistics.”
         Earthquake Engineering & Structural Dynamics, 47(5), 1107–1123.

    Parameters
    ----------
    variogram_pc: dict
        dictionary containing the variables for the current pricipal component
    distance_matrix: numpy array
        distance between each site

    Returns
    -------
    c_h: numpy array
        covariance matrix for the principal component

    """


    # retrive the variogram parameters
    co = variogram_pc['co']
    c1 = variogram_pc['c1']
    a1 = variogram_pc['a1']
    c2 = variogram_pc['c2']
    a2 = variogram_pc['a2']

    # size of the covariance matrix
    n = len(distance_matrix)

    # calculate C(h), based on the distance matrix (eqn. 26)
    c_h = co * np.eye(n) + c1 * np.exp((-3 * distance_matrix) / a1) + c2 * np.exp((-3 * distance_matrix) / a2)

    return c_h


def nugget_covariance(variogram_pc, distance_matrix):
    """

    Calculates covariance for the current principal component, based on the nugget

    Documentation is provided in the following document:
         Markhvida, M., Ceferino, L., and Baker, J. W. (2018), “Modeling spatially correlated
         spectral accelerations at multiple periods using principal component analysis and geostatistics.”
         Earthquake Engineering & Structural Dynamics, 47(5), 1107–1123.

    Parameters
    ----------
    variogram_pc: dict
        dictionary containing the variables for the current pricipal component
    distance_matrix: numpy array
        distance between each site

    Returns
    -------
    c_h: numpy array
        covariance matrix for the principal component

    """

    # retrive the variogram parameters
    co = variogram_pc['co']

    # size of the covariance matrix
    n = len(distance_matrix)

    # calculate C(h), based on the distance matrix (eqn. 26)
    c_h = co * np.eye(n)

    return c_h


def markhvida_ceferino_baker_simulation(sites, periods, n_sims, n_pcs):
    """

    Simulates correlated within-event residuals for multiple sites and periods

    Documentation is provided in the following document:
         Markhvida, M., Ceferino, L., and Baker, J. W. (2018), “Modeling spatially correlated
         spectral accelerations at multiple periods using principal component analysis and geostatistics.”
         Earthquake Engineering & Structural Dynamics, 47(5), 1107–1123.

    Parameters
    ----------
    sites: pandas dataframe
        list of sites with Latitude and Longitude columns

    periods: numpy array
        the periods to be simulated for Sa(T)

    n_sims: int
        total simulations (ruptures x realizations)

    n_pcs: int
        number of principal components to include (5-19)

    Returns
    -------
    z_residuals: numpy array
        within event residuals for each site, period, and simulation
        (n_sites x n_periods x n_simulations)

    """

    # load the PCA model parameters
    # [variogram, pca_coefficients, variance_explained, pca_periods] = load_pca_model()

    # retrieve the cumulative variance explained for the number of principal components used
    cum_var_expl = pca_variance_explained[n_pcs - 1]

    # convert site latitude and longitude into meters
    [x, y] = utm_conversion(sites['Latitude'], sites['Longitude'])

    # convert x and y into point pairs in kilometers
    pts = np.array([i for i in zip(x / 1000, y / 1000)])

    # calculate a distance matrix
    distance_matrix = np.sum((pts[None, :] - pts[:, None]) ** 2, -1) ** 0.5

    # prep for simulating residuals
    n_sites = len(sites)
    pca_residuals = np.empty([n_pcs, n_sites, n_sims])
    mu = np.zeros(n_sites)

    # simulate residuals for each principal component
    for i in range(n_pcs):
        pc_tag = 'PC' + str(i + 1)

        # identify the covariance type to call the appropriate function
        cov_type = pca_variogram[pc_tag][0]['Type']
        c_h = eval(cov_type + '(pca_variogram[pc_tag][0], distance_matrix)')

        # normalize by the cumulative percent of explained variance (eqn 29)
        c_h = c_h / cum_var_expl

        # simulate the residuals, using a multi-variate random normal distribution
        pca_residuals[i, :, :] = np.random.multivariate_normal(mu, c_h, n_sims).T

    # linearly interpolate the pca coefficients to obtain a transformation for the periods of interest
    f = interp1d(pca_periods, pca_coefficients[:, :n_pcs], axis=0)
    z_coefficients = f(periods)

    # transform the PCA residuals to Sa(T) residuals
    z_residuals = np.empty([n_sites, len(periods), n_sims])
    for i in range(n_sims):
        z_residuals[:, :, i] = np.matmul(np.matrix(z_coefficients), pca_residuals[:, :, i]).T

    return z_residuals


def within_event_simulation(sites, periods, n_sims):
    """

    Simulates correlated residuals for all site and periods

    Accommodates the maximum period in the Markhvida et al. correlation model by
        assuming that all the residuals for all periods above T=5s are perfectly correlated.

    Parameters
    ----------
    sites: pandas dataframe
        list of sites with Latitude and Longitude columns

    periods: numpy array
        periods of interest for Sa(T)
        must be increasing in value for the maximum period accommodation

    n_sims: int
        number of events to simulate

    Returns
    -------
    residuals: numpy array
        within event residuals, shape: [n_sites, n_periods, n_sims]

    """

    # use all the available principal components
    n_pcs = 19

    # modify the period list to account for the maximum period in the simulation method
    n_t = len(periods)
    max_t = 5
    idx_available = np.where(periods <= max_t)[0]
    idx_exceeding = np.where(periods > max_t)[0]
    if len(idx_exceeding) > 0:
        periods = periods[periods <= max_t]
        idx_supplement = len(periods)
        periods = np.append(periods, [max_t])

        residuals = markhvida_ceferino_baker_simulation(sites, periods, n_sims, n_pcs)

    # add the unsimulated periods, assuming perfect correlation with Sa(T=5)
    if len(idx_exceeding) > 0:
        temp = np.empty([len(sites), n_t, n_sims])
        temp[:, idx_available, :] = residuals[:, idx_available, :]
        for idx in idx_exceeding:
            temp[:, idx, :] = residuals[:, idx_supplement, :]
            residuals = temp

    return residuals


def ground_motion_simulation(eqhazard_file, n_realizations, output_file):
    """

    Simulates ground motion map realizations for the ground motion data provided by OpenSHA

    Saves ground motions and all intermediate simulations to a new data file

    Parameters
    ----------
    eqhazard_file: string
        name of a new .h5 file containing the following dsets:
            Ruptures (contains metadata of the ruptures considered)
            Sites    (contains site locations and Vs30)
            Periods  (contains the periods considered for Sa(T))
            Medians  (the median predicted Sa(T) value for each rupture, site, and period)
            TotalStdDeviations (for each rupture, site, and period)
            WithinEvStdDev     (for each rupture, site, and period)
            BetweenEvStdDev    (for each rupture, site, and period)

    n_realizations: int
        number of ground motion realizations to simulate

    output_file: string
        name of a new .h5 file containing the eqhazard datasets and the following dsets:
            GroundMotions (for each rupture, site, period, and realization)
            Epsilons      (for each rupture, site, period, and realization)
            Etas          (for each rupture, site, period, and realization)
            WithinEvResiduals (for each rupture, site, period, and realization)
            BetweenEvResiduals (for each rupture, site, period, and realization)



    """
    # retrieve site and rupture metadata
    sites = pd.read_hdf(eqhazard_file, 'Sites')
    n_sites = len(sites)

    ruptures = pd.read_hdf(eqhazard_file, 'Ruptures')
    n_ruptures = len(ruptures)

    # retrieve underlying ground motion distributions
    with h5py.File(eqhazard_file, 'r') as hf:
        periods = hf['Periods'][:]
        medians = hf['Medians'][:]
        within_stdevs = hf['WithinEvStdDevs'][:]
        between_stdevs = hf['BetweenEvStdDevs'][:]

    # total number of simulations (all realizations of all ruptures)
    n_sims = n_ruptures * n_realizations

    # simulate within-event residuals (epsilon), unique to each site
    within_residuals = within_event_simulation(sites, periods, n_sims)
    # reshape to separate simulations in realizations by rupture
    within_residuals = np.array(
        [within_residuals[:, :, n_realizations * iRup:n_realizations * (iRup + 1)] for iRup in range(n_ruptures)])

    # simulate between-event residuals (eta), common to all sites
    between_residuals = between_event_simulation(periods, n_sims)
    # reshape to separate simulations in realizations by rupture
    between_residuals = np.array([between_residuals[:, n_realizations * iRup:n_realizations * (iRup + 1)] for iRup in range(n_ruptures)])
    # repeat across all sites
    between_residuals = np.tile(np.expand_dims(between_residuals, 1), (1, n_sites, 1, 1))

    # ground motion prediction equation, in log space
    epsilons = np.empty_like(within_residuals)
    etas = np.empty_like(within_residuals)
    ln_sa = np.empty_like(within_residuals)
    for iReal in range(n_realizations):
        # calculate epsilons (scaled by the within event std devitation
        epsilons[:, :, :, iReal] = within_residuals[:, :, :, iReal] * within_stdevs
        # calculate etas (scaled by the between event std devitation
        etas[:, :, :, iReal] = between_residuals[:, :, :, iReal] * between_stdevs
        # combine for ground motion prediction equation
        ln_sa[:, :, :, iReal] = medians + epsilons[:, :, :, iReal] + etas[:, :, :,iReal]

    # ground motion, in real space
    ground_motion = np.exp(ln_sa)

    # create new output file from eqhazard file
    shutil.copyfile(eqhazard_file, output_file)
    # write ground motion and underlying simulations to output
    with h5py.File(output_file, 'r+') as hf:
        hf.create_dataset('GroundMotions', data=ground_motion)
        hf.create_dataset('Epsilons', data=epsilons)
        hf.create_dataset('Etas', data=etas)
        hf.create_dataset('WithinEvResiduals', data=within_residuals)
        hf.create_dataset('BetweenEvResiduals', data=between_residuals)

