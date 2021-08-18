import numpy as np
from faps.genotypeArray import genotypeArray
from faps.alogsumexp import alogsumexp

def sibship_paternity(offspring, mothers, males, allele_freqs, mu, partition, reciprocal = False):
    """
    Calculate the likelihoods that each candidate father is the sire of each
    full sibship implied by a partition sturcture. Includes likelihood that
    paternal alleles are drawn from population allele frequencies.


    Parameters
    ----------
    offspring: genotypeArray, or list of genotypeArrays
        Observed genotype data for the offspring.
    mothers: genotypeArray, or list of genotypeArrays
        Observed genotype data for the offspring. Data on mothers need
        to be in the same order as those for the offspring.
    males: genotypeArray
        Observed genotype data for the candidate males.
    allele_freqs: array-like
        Vector of population allele frequencies for the parents.
    mu: float between zero and one
        Point estimate of the genotyping error rate. Clustering is unstable if
        mu_input is set to exactly zero.
    partition: array
        1-d array of integers labelling individuals into families. This should
        have as many elements as there are individuals in paternity_probs.
    reciprocal: bool, optional
        If true, function return 1-transition probabilities, or the
        probability of *not* generating the offspring given maternal and
        candidate paternal genotypes

    Returns
    -------
    Array of likelihoods of paternity indexing sibships x candidates.
    """
    if not isinstance(offspring, genotypeArray):
        raise TypeError('offspring is not a genotypeArray')
    if not isinstance(mothers, genotypeArray):
        raise TypeError('mothers is not a genotypeArray')
    if not isinstance(males, genotypeArray):
        raise TypeError('males is not a genotypeArray')
    if len(partition) != offspring.size:
        raise ValueError('Length of partition does not match number of offspring.')
    if mu == 0:
        warn('Setting error rate to exactly zero causes clustering to be unstable.')

    # diploid genotypes
    offspring_diploid = offspring.geno.sum(2)
    maternal_diploid = mothers.geno.sum(2)
    male_diploid = males.geno.sum(2)

    # array of viable transition probabilities
    trans_prob_array = np.array([[[1,  0.5, 0  ],
                                  [0.5,0.25,0  ],
                                  [0,  0,   0  ]],
                                 [[0,  0.5, 1  ],
                                  [0.5,0.5, 0.5],
                                  [1,  0.5, 0  ]],
                                 [[0,  0,   0  ],
                                  [0,  0.25,0.5],
                                  [0,  0.5, 1  ]]])

    # array of probabilities for paternal genotypes when drawn from allele frequencies.
    af = np.array([allele_freqs**2,
              allele_freqs * (1-allele_freqs),
              (1-allele_freqs)**2])

    vals    = np.unique(partition)
    prob_s  = np.zeros([len(vals), males.size+1])
    missing = np.zeros(len(vals))

    for v in range(len(vals)):
        ix = np.where(partition == vals[v])[0]
        #print ix
        # empty arrays to stores probabilities.
        prob_f = np.zeros([3, males.size, offspring.nloci])
        prob_a = np.zeros([3, males.nloci])

        # positions of dropouts
        drop_m = (maternal_diploid[ix] < 0) + (offspring_diploid[ix] < 0) # offspring vs mothers

        geno =[0,1,2]
        for f in geno:
            prob_m = np.zeros(offspring_diploid[ix].shape)
            for m in geno:
                prob_o = np.zeros(offspring_diploid[ix].shape)
                for o in geno:
                    # the transition probability for the given genotypes.
                    if reciprocal: trans_prob = 1-trans_prob_array[o, m, f]
                    else:          trans_prob =   trans_prob_array[o, m, f]
                    # Probabilities that the observed offspring marker data match observed data.
                    pr_offs = np.zeros(offspring_diploid[ix].shape)
                    pr_offs[offspring_diploid[ix] == o] = 1-mu
                    pr_offs[offspring_diploid[ix] != o] = mu
                    prob_o = prob_o + (trans_prob * pr_offs * 1/3)
                # Probabilities that the observed maternal marker data match observed data.
                pr_mothers = np.zeros(maternal_diploid[ix].shape)
                pr_mothers[maternal_diploid[ix] == m] = 1-mu
                pr_mothers[maternal_diploid[ix] != m] = mu
                prob_m = prob_m + (prob_o * pr_mothers * 1/3)

            prob_m = prob_m / 3
            # Probabilities that the observed candidate male marker data match observed data.
            pr_males = np.zeros(male_diploid.shape)
            pr_males[male_diploid == f] = 1-mu
            pr_males[male_diploid != f] = mu

            prob_m[drop_m] = 1 # set loci with dropouts to prob=1. We will correct them these later.
            arr = np.log(prob_m).sum(0) + np.log(pr_males) # multiply by probability of paternal genotypes
            arr[male_diploid < 0] = 0 # allow for dropouts in the candidates
            # send to output.
            prob_f[f] = arr[np.newaxis]
            prob_a[f] = np.log(prob_m).sum(0) + np.log(af[f])

        # sum over possible paternal genotypes
        prob_f = alogsumexp(prob_f, axis=0)
        # correct for dropouts in father
        drop_f = drop_m[np.newaxis] + (male_diploid<0)[:,np.newaxis]
        corr = float(offspring.size*offspring.nloci) / (1-drop_f).sum(1).sum(1)
        prob_f = prob_f.sum(1) * corr
        # correct dropouts for missing fathers
        prob_a = alogsumexp(prob_a, axis=0).sum()
        corr = float(offspring.size*offspring.nloci) / (1-drop_m).sum()
        prob_a = prob_a * corr
        # send to output
        prob_s[v] = np.append(prob_f, prob_a)
    return(prob_s)
