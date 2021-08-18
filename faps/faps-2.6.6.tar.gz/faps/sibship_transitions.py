from warnings import warn

def sibship_transitions(families, paternity_array, males, exp=False):
    """
    Transition probabilities (really log likelihoods) that each male is the sire
    of a set of putative full sibships.

    This differs from transition_probabilities in that sibship_transitions
    multiplies over sibships *before* summing over paternal genotypes. This
    ought to be more accurate because any genotyping error in the candidate 
    fathers is not multiplied over offspring, but incurs a loss in speed of
    about one order of magnitude.

    Parameters
    ----------
    families: list of vectors.
        A list of vectors, each giving the indices of one or more offspring in
        a putative full sibship. This is usually based on a set of partitions
        generated using sibship_partitions.
    paternity_array: paternityArray
        paternityArray object used to generate families.
    males: genotypeArray
        genotypeArray object used to generate families.
    exp: boolean, optional
        If True, likelihood arrays are exponentiated. This confers a substantial
        speed boost, but is unstable if the sample includes families with very
        low likelihood, because it is necessary to multiply over many small
        numbers, causing underflow.

    Returns
    -------
    An array of likelihoods that each full sibship was sired by each candidate
    male, indexed as n.families x n/candidates+1. The extra column is for the 
    likelihood that paternal alleles are drawn from population allele frequencies.
    Output is not normalised over candidates.

    Example
    -------
    import numpy as np
    from faps import *

    # generate 4 families of 5 offspring
    allele_freqs = np.random.uniform(0.3, 0.5, 50)
    males = make_parents(200, allele_freqs)
    offspring = make_sibships(males, 0, range(1,5), 5)

    # Add muations
    mu = 0.0013
    males = males.dropouts(0.01).mutations(mu)
    offspring= offspring.dropouts(0.01).mutations(mu)

    mothers = males.subset(offspring.parent_index('m', males.names))
    patlik = paternity_array(offspring, mothers, males, allele_freqs, mu)
    # Generate possible sets of families from fullpairs
    partition_sample = sibship_partitions(patlik)

    #get a list of all unique families.
    unique_families = [np.where(p == val)[0] for p in partition_sample for val in np.unique(p)]
    unique_families = set([tuple(up) for up in unique_families]) # coerce to tuple to create set
    unique_families = [np.array(up) for up in unique_families] # coerce back to numpy arrays

    sibship_transitions(unique_families, patlik, males)

    """
    # check types.
    if not isinstance(males, genotypeArray):
        TypeError("Argument paternity_array should be the paternityArray used to generate the list of plausible families.")
    if not isinstance(paternity_array, paternityArray):
        TypeError("Argument paternity_array should be the paternityArray used to generate the list of plausible families.")
    if not all(paternity_array.candidates == males.names):
        warn("Not all names of candidate fathers in the paternity array match those in the genotype array.\nEnsure both arrays are really those used to generate the list of families.")
    if paternity_array.by_locus is None:
        ValueError("paternity_array does not include ")

    if isinstance(patlik.by_locus, np.ndarray):
        if patlik.by_locus.shape == (3, len(patlik.offspring), males.nloci):
            ValueError("The attribute by_locus in the genotype array does not match the genotype array.")
    else:
        TypeError("The attribute by_locus in the genotype array does not exist, or is not a NumPy array.")
 
    # set mutational error rate.
    mu = paternity_array.mu
    if mu == 0:
        mu = 10**-12
        warn('Setting error rate to exactly zero causes clustering to be unstable. mu set to 10e-12')
    
    male_diploid = males.geno.sum(2)
    # create matrix to correct for dropouts.
    drop_f = (male_diploid < 0)
    corr   = 1/(1 - drop_f.mean(1))[np.newaxis]
    
    # likelihood for each unique family given maternal and offspring genotypes. 
    prob_u = np.array([paternity_array.by_locus[:,up].sum(1) for up in families])
    
        # array of possible allele frequency probabilities
    af = np.array([allele_freqs ** 2,
                   allele_freqs * (1-allele_freqs),
                   (1-allele_freqs)**2])
    af = np.log(af)
    prob_a = alogsumexp(prob_u + af[np.newaxis], 1).sum(1)
    # get the likelihood for each possible paternal genotype, exponentiating likelihoods.
    if exp:
        prob_f = np.zeros([len(families), males.size, males.nloci])
        prob_u = np.exp(prob_u)
        for f in [0,1,2]:
            pr_males = np.zeros(male_diploid.shape)
            pr_males[male_diploid == f] = 1-mu
            pr_males[male_diploid != f] = mu
            pr_males[drop_f] = 1
            prob_f += prob_u[:,f][:, np.newaxis] * pr_males[np.newaxis]
        with np.errstate(divide='ignore'):
            siblik = np.log(prob_f.prod(2))
    
    # get the likelihood for each possible paternal genotype, without exponentiating likelihoods.
    else:
        prob_f = np.zeros([3, len(families), males.size, males.nloci])
        for f in [0,1,2]:
            pr_males = np.zeros(male_diploid.shape)
            pr_males[male_diploid == f] = 1-mu
            pr_males[male_diploid != f] = mu
            pr_males[drop_f] = 1
            prob_f[f] = prob_u[:,f][:, np.newaxis] + np.log(pr_males)[np.newaxis]
        siblik = alogsumexp(prob_f, axis=0).sum(2)
    
    siblik = siblik + np.log(corr)
    
    return np.column_stack([siblik, prob_a])