"""Optimization algorithms."""

import numpy as np
import tqdm


def metro_hast(
        tdata, N, simSetting, perturbSetting, simFunc, perturbFunc, scoreFunc
):
    """Metropolis hastings algorithm that samples parameter space.

    Parameters
    ----------
    tdata : np.array
        True dataset on which the score function calculates its value.
    N : int
        Number of iterations the metropolist hastings algorithm performs.
    simSetting : dict
        Dictionary of settings needed for the simulation.
    perturbSetting : dict
        Dictionary of settings needed for the perturbation function.
    simFunc : function
        Function that performs the actual simulation with np.array output.
    perturbFunc : function
        Function that perturbs variable inputs into simulation function.
    scoreFunc : function
        Function that calculates a score from the fit between real data and
        simulated data.

    Returns
    -------
    simSettings : np.array
        Set of variable settings that were sampled.
    allData : np.array
        Generated data from the previous settings.
    scores : np.array
        Scores according to provided score function regarding data fit.
    """
    # start simulation
    allData = [simFunc(**simSetting)[1]]
    scores = [scoreFunc(tdata, allData[-1])]
    simSettings = [simSetting]

    for i in tqdm(range(N)):
        # Perturb parameters slightly
        newSettings = perturbFunc(simSettings[-1].copy(), perturbSetting)
        # Run simulation
        newData = simFunc(**newSettings)[1]
        # Calculate score
        newScore = scoreFunc(tdata, newData)
        # See if score is better than the last iteration and keep if it is
        if newScore <= scores[-1]:
            simSettings.append(newSettings)
            allData.append(newData)
            scores.append(newScore)
        # Or else give a random chance to still be accepted
        else:
            random = np.random.rand()
            if random < scores[-1] / newScore:
                simSettings.append(newSettings)
                allData.append(newData)
                scores.append(newScore)
    return np.array(simSettings), np.array(allData), np.array(scores)
