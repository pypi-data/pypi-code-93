import numpy as np
import scipy as sp


def compute_credible_intervals(
        samples, credible_level=.95, use_median=False):
    tail_percentile = 100 * (1 - credible_level) / 2
    compute_middle = np.median if use_median else np.mean
    middle = compute_middle(samples, -1)
    upper = np.percentile(samples, 100 - tail_percentile, axis=-1)
    lower = np.percentile(samples, tail_percentile, axis=-1)
    return middle, lower, upper


def find_signif_coef(coef_samples, signif_level=.05, n_burnin=0):
    """
    Returns the indices of the cofficients whose one-sided tail probability
    is larger than 1 - signif_level / 2.
    """

    tail_prob = compute_tail_prob(coef_samples, n_burnin)
    top_coef_index, = np.nonzero(tail_prob > (1 - signif_level / 2))
    tail_prob = tail_prob[top_coef_index]

    # Sort the indices in terms of the tail probabilities.
    sorting_index = np.argsort(tail_prob)[::-1]
    top_coef_index = top_coef_index[sorting_index]
    tail_prob = tail_prob[sorting_index]

    # Break the ties in terms of the posterior mean.
    tie_indicator = (tail_prob == 1.)
    tied_indices = top_coef_index[tie_indicator]
    post_mean_magnitude = np.abs(
        np.mean(coef_samples[tied_indices, n_burnin:], -1))
    sorting_index = np.flip(np.argsort(post_mean_magnitude))
    top_coef_index[tie_indicator] = tied_indices[sorting_index]
    tail_prob[tie_indicator] = tail_prob[tie_indicator][sorting_index]

    return top_coef_index, tail_prob


def compute_tail_prob(coef_samples, n_burnin=0):
    tail_prob = np.max(np.vstack((
        np.mean(coef_samples[:, n_burnin:] > 0, 1),
        np.mean(coef_samples[:, n_burnin:] < 0, 1)
    )), 0)
    return tail_prob


# def compute_ave_treatment_effect(
#         treatment, X_interaction, treatment_samples, interaction_samples):
#     treatment_effect_samples = np.zeros(treatment_samples.size)
#     treatment_freq = np.mean(treatment)
#     for i in range(treatment_samples.size):
#         treatment_effect_samples[i] \
#             = treatment_freq * treatment_samples[i] \
#               + X_interaction.dot(interaction_samples[:, i]).mean()
#     return treatment_effect_samples


def compute_ave_treatment_effect(
        treatment_coef_samples, interaction_coef_samples, treatment, X_main):
    n_mcmc_sample = treatment_coef_samples.size
    treatment_effect_samples = np.squeeze(treatment_coef_samples)
    for i in range(n_mcmc_sample):
        treatment_effect_samples[i] \
            += X_main.dot(interaction_coef_samples[:, i]).mean()
    return treatment_effect_samples
