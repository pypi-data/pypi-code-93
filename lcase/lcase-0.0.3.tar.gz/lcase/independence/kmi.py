import numpy as np

def kernel_mutual_information(x1, x2):
    """Calculate the mutual informations."""
    # if x1.ndim == 1:
    #     x1 = np.expand_dims(x1, axis=1)
    #
    # if x2.ndim == 1:
    #     x2 = np.expand_dims(x2, axis=1)

    if x1.shape[0] > 1000:
        param = [2e-3, 0.5]
    else:
        param = [2e-2, 1.0]

    kappa, sigma = param
    n = len(x1)
    X1 = np.tile(x1, (n, 1))
    K1 = np.exp(-1 / (2 * sigma ** 2) * (X1 ** 2 + X1.T ** 2 - 2 * X1 * X1.T))
    X2 = np.tile(x2, (n, 1))
    K2 = np.exp(-1 / (2 * sigma ** 2) * (X2 ** 2 + X2.T ** 2 - 2 * X2 * X2.T))

    tmp1 = K1 + n * kappa * np.identity(n) / 2
    tmp2 = K2 + n * kappa * np.identity(n) / 2
    K_kappa = np.r_[np.c_[tmp1 @ tmp1, K1 @ K2],
                    np.c_[K2 @ K1, tmp2 @ tmp2]]
    D_kappa = np.r_[np.c_[tmp1 @ tmp1, np.zeros([n, n])],
                    np.c_[np.zeros([n, n]), tmp2 @ tmp2]]

    sigma_K = np.linalg.svd(K_kappa, compute_uv=False)
    sigma_D = np.linalg.svd(D_kappa, compute_uv=False)

    return (-1 / 2) * (np.sum(np.log(sigma_K)) - np.sum(np.log(sigma_D)))