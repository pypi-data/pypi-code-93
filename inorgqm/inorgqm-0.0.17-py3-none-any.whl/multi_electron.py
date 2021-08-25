#! /usr/bin/env python3

import numpy as np
import numpy.linalg as la
import matplotlib.pyplot as plt
from . import utils as ut
from functools import reduce, lru_cache
from sympy.physics.wigner import wigner_3j, wigner_6j

@lru_cache(maxsize=None)
def recursive_a(k, q, m):
    """
    Given k,q,m this function
    calculates and returns the a(k,q-1,m)th
    Ryabov coefficient by recursion

    Positional arguments:
        k (int) : k value
        q (int) : q value
        m (int) : m value

    Keyword arguments:
        None

    Returns:
        coeff (np.ndarray) : a(k,q,m) values for each power of
                             X=J(J+1) (Ryabov) up to k+1

    """
    coeff = np.zeros(k+1)

    # Catch exceptions/outliers and end recursion
    if k == q-1 and m == 0:
        coeff[0] = 1
    elif q-1 + m > k:
        pass
    elif m < 0:
        pass
    else:
        # First and second terms
        coeff += (2*q+m-1)*recursive_a(k, q+1, m-1)
        coeff += (q*(q-1) - m*(m+1)/2) * recursive_a(k, q+1, m)

        # Third term (summation)
        for n in range(1, k-q-m+1):
            # First term in sum of third term
            coeff[1:] += (-1)**n * (
                            ut.binomial(m+n, m) * recursive_a(k, q+1, m+n)[:-1]
                        )
            # Second and third term in sum
            coeff += (-1)**n * (
                        - ut.binomial(m+n, m-1) - ut.binomial(m+n, m-2)
                    ) * recursive_a(k, q+1, m+n)

    return coeff


def get_ryabov_a_coeffs(k_max):

    """
    Given k_max this function calculates all possible values
    of a(k,q,m) for each power (i) of X=J(J+1)

    Positional arguments:
        k_max (int) : maximum k value

    Keyword arguments:
        None

    Returns:
        a (np.ndarray) : All a(k,q,m,i)
        f (np.ndarray) : Greatest common factor of each a(k,q,:,:)
    """

    a = np.zeros([k_max, k_max+1, k_max+1, k_max+1])
    f = np.zeros([k_max, k_max+1])

    # Calculate all a coefficients
    for k in range(1, k_max + 1):
        for qit, q in enumerate(range(k, -1, -1)):
            for m in range(k-q + 1):
                a[k-1, qit, m, :k+1] += recursive_a(k, q+1, m)

    # Calculate greatest common factor F for each a(k,q) value
    for k in range(1, k_max + 1):
        for qit, q in enumerate(range(k, -1, -1)):
            allvals = a[k-1, qit, :, :].flatten()
            nzind = np.nonzero(allvals)
            if np.size(nzind) > 0:
                f[k-1, qit] = reduce(ut.GCD, allvals[nzind])

    return a, f


def calc_stev_ops(k_max, J, jp, jm, jz):
    """
    Calculates all Stevens operators Okq with k even and odd up to k_max
    k_max must be <= 12

    Positional arguments:
        k_max (int)     : maximum k value
        J  (int)        : J quantum number
        jp (np.array)  : Matrix representation of angular momentum operator
        jm (np.array)  : Matrix representation of angular momentum operator
        jz (np.array)  : Matrix representation of angular momentum operator

    Keyword arguments:
        None

    Returns:
        okq (np.ndarray of np.ndarrays) : List containing each Stevens
                                          operator indexed [k,q,:,:]
                                          k=1 q=-k->k, k=2 q=-k->k ...
    """

    # Only k <= 12 possible at double precision
    k_max = min(k_max, 12)

    # Get a(k,q,m,i) coefficients and greatest common factors
    a, f = get_ryabov_a_coeffs(k_max)

    # Sum a(k,q,m,i) coefficients over powers of J to give a(k,q,m)
    a_summed = np.zeros([k_max, k_max+1, k_max+1])

    for i in range(0, k_max+1):
        a_summed += a[:, :, :, i] * (J*(J+1))**i

    _jp = np.complex128(jp)
    _jm = np.complex128(jm)
    _jz = np.complex128(jz)

    n_states = int(2*J+1)

    okq = np.zeros([k_max, 2*k_max+1, n_states, n_states], dtype=np.complex128)

    # Calulate q operators both + and - at the same time
    for kit, k in enumerate(range(1, k_max + 1)):
        # New indices for q ordering in final okq array
        qposit = 2*k + 1
        qnegit = -1
        for qit, q in enumerate(range(k, -1, -1)):
            qposit -= 1
            qnegit += 1
            if k % 2:  # Odd k, either odd/even q
                alpha = 1.
            elif q % 2:  # Even k, odd q
                alpha = 0.5
            else:  # Even k, even q
                alpha = 1.

            # Positive q
            for m in range(k-q + 1):
                okq[kit, qposit, :, :] += a_summed[kit, qit, m]*(
                    (
                        la.matrix_power(_jp, q)
                        + (-1.)**(k-q-m)*la.matrix_power(_jm, q)
                    ) @ la.matrix_power(_jz, m)
                )

            okq[kit, qposit, :, :] *= alpha/(2*f[kit, qit])

            # Negative q
            if q != 0:
                for m in range(k-q + 1):
                    okq[kit, qnegit, :, :] += a_summed[kit, qit, m]*(
                        (
                            la.matrix_power(_jp, q)
                            - (-1.)**(k-q-m)*la.matrix_power(_jm, q)
                        ) @ la.matrix_power(_jz, m)
                    )

                okq[kit, qnegit, :, :] *= alpha/(2j*f[kit, qit])

    return okq


def calc_ang_mom_ops(J):
    """
    Calculates the angular momentum operators jx jy jz jp jm j2

    Positional arguments:
        J (float)      : J quantum number

    Keyword arguments:
        None

    Returns:
        jx (np.array)  : Matrix representation of angular momentum operator
        jy (np.array)  : Matrix representation of angular momentum operator
        jz (np.array)  : Matrix representation of angular momentum operator
        jp (np.array)  : Matrix representation of angular momentum operator
        jm (np.array)  : Matrix representation of angular momentum operator
        j2 (np.array)  : Matrix representation of angular momentum operator
    """

    # Create vector of mj values
    mj = np.arange(-J, J + 1, 1, dtype=np.complex128)
    # calculate number of states
    n_states = int(2 * J + 1)

    # jz operator - diagonal in jz basis- entries are mj
    jz = np.diag(mj)

    # jp and jm operators
    jp = np.zeros([n_states, n_states], dtype=np.complex128)
    jm = np.zeros([n_states, n_states], dtype=np.complex128)
    for it1, mjp in enumerate(mj):
        for it2, mjq in enumerate(mj):
            jp[it1, it2] = np.sqrt(J * (J + 1) - mjq * (mjq + 1))
            jp[it1, it2] *= ut.krodelta(mjp, mjq + 1)
            jm[it1, it2] = np.sqrt(J * (J + 1) - mjq * (mjq - 1))
            jm[it1, it2] *= ut.krodelta(mjp, mjq - 1)

    # jx, jy, and j2
    jx = 0.5 * (jp + jm)
    jy = 1. / (2. * 1j) * (jp - jm)
    j2 = jx @ jx + jy @ jy + jz @ jz

    return jx, jy, jz, jp, jm, j2


def load_CFPs(f_name, style="phi"):
    """
    Loads Crystal Field parameters from file
    """

    _CFPs = []
    if style == "phi":
        # Read in CFPs, and k and q values
        kq = []
        # site, k, q, Bkq
        with open(f_name, 'r') as f:
            for line in f:
                kq.append(line.split()[1:3])
                _CFPs.append(line.split()[3])
        kq = [[int(k), int(q)] for [k, q] in kq]
        _CFPs = [float(CFP) for CFP in _CFPs]

        # Include zero entries for missing CFPs
        CFPs = np.zeros([27])
        for CFP, [k, q] in zip(_CFPs, kq):
            CFPs[ut._even_kq_to_num(k, q)] = CFP

    return CFPs


def calc_HCF(J, CFPs, stev_ops, k_max=False, oef=False):
    """
    Calculates crystal field Hamiltonian (HCF) using CFPs and Stevens operators
    Okq, where k even and ranges 2 -> 2j

    Hamiltonian is sum_k sum_q Bkq Okq

    Positional arguments:
        J (float)                   : J quantum number
        CFPs (np.array)             : Even k crystal Field parameters in order
                                      k=2 q=-k->k, k=4 q=-k->k ...
        stevops (list of np.arrays) : List containing each even k
                                      stevens operator
                                      indexed [k_ind,q_ind,:,:]
                                      k_ind = 1, .. k_max/2
                                      q_ind = 1, .. 2*q_max + 5 :(q_max=+-k)

    Keyword arguments:
        k_max (int)    : Maximum value of k to use in summation - by default 2*J
        oef (np.array) : Operator equivalent factors for each CFP
                         i.e. 27 CFPs = 27 OEFs
                         by default these are set to unity
    Returns:
        HCF (np.array)    : Matrix representation of Crystal Field Hamiltonian
        CF_val (np.array) : Eigenvalues of HCF (lowest eigenvalue is zero)
        CF_vec (np.array) : Eigenvectors of HCF

    """

    if not k_max:
        k_max = int(2*J)
        k_max -= k_max % 2
        k_max = min(k_max, 12)

    if not oef:
        oef = np.ones(np.size(CFPs))

    # calculate number of states
    n_states = int(2 * J + 1)

    # Form Hamiltonian
    HCF = np.zeros([n_states, n_states], dtype=np.complex128)
    for kit, k in enumerate(range(2, k_max+1, 2)):
        for qit, q in enumerate(range(-k, k+1)):
            HCF += stev_ops[kit, qit, :, :] * CFPs[ut._even_kq_to_num(k, q)] \
                    * oef[ut._even_kq_to_num(k, q)]

    # Diagonalise
    CF_val, CF_vec = la.eigh(HCF)

    # Set ground energy to zero
    CF_val -= CF_val[0]

    return HCF, CF_val, CF_vec


def calc_lande_g(J, L, S):
    """
    Calculates lande g factor

    Positional Arguments:
        J (float)      : J quantum number
        L (float)      : L quantum number
        S (float)      : S quantum number

    Keyword Arguments:
        None

    Returns
        gJ (float) : Lande g factor

    """

    # Orbital part
    gJ = (J*(J+1.) - S*(S+1.) + L*(L+1.))/(2.*J*(J+1.))

    # Spin part
    gJ += (J*(J+1.) + S*(S+1.) - L*(L+1.))/(J*(J+1.))

    return gJ


def calc_mag_moment_j(J, L, S, jx, jy, jz):
    """
    Calculate magnetic moment in total angular momentum basis |J, mJ>
    along each axis x, y, and z with units [cm-1 T-1]

    Positional Arguments:
        J (float)      : J quantum number
        L (float)      : L quantum number
        S (float)      : S quantum number
        jx (np.array)  : Matrix representation of angular momentum operator
        jy (np.array)  : Matrix representation of angular momentum operator
        jz (np.array)  : Matrix representation of angular momentum operator

    Keyword Arguments:
        None

    Returns
        mu_x (np.ndarray) : Magnetic moment operator in x direction [cm-1 T-1]
        mu_y (np.ndarray) : Magnetic moment operator in y direction [cm-1 T-1]
        mu_z (np.ndarray) : Magnetic moment operator in z direction [cm-1 T-1]

    """

    _jx = np.complex128(jx)
    _jy = np.complex128(jy)
    _jz = np.complex128(jz)

    gJ = calc_lande_g(J, L, S)

    mu_B = 0.466866577042538

    mu_x = gJ * _jx * mu_B
    mu_y = gJ * _jy * mu_B
    mu_z = gJ * _jz * mu_B

    return mu_x, mu_y, mu_z


def calc_HZee_j(J, L, S, jx, jy, jz, B):
    """
    Calculate Zeeman Hamiltonian in total angular momentum basis |J, mJ>

    Positional Arguments:
        J (float)      : J quantum number
        L (float)      : L quantum number
        S (float)      : S quantum number
        jx (np.array)  : Matrix representation of angular momentum operator
        jy (np.array)  : Matrix representation of angular momentum operator
        jz (np.array)  : Matrix representation of angular momentum operator
        B (np.array)   : Magnetic field strengths in x, y, z - [Bx, By, Bz]
                            in Tesla

    Keyword Arguments:
        None

    Returns
        mu_x (np.ndarray) : Magnetic moment operator in x direction
        mu_y (np.ndarray) : Magnetic moment operator in y direction
        mu_z (np.ndarray) : Magnetic moment operator in z direction

    """

    # Make sure operators are complex type
    _jx = np.complex128(jx)
    _jy = np.complex128(jy)
    _jz = np.complex128(jz)

    # Magnetic moment with units [cm-1 T-1]
    _mu_x, _mu_y, _mu_z = calc_mag_moment_j(J, L, S, _jx, _jy, _jz)

    # Form Zeeman Hamiltonian
    HZee = _mu_x * B[0] + _mu_y * B[1] + _mu_z * B[2]

    # Diagonalise
    Zee_val, Zee_vec = la.eigh(HZee)

    # Set ground energy to zero
    Zee_val -= Zee_val[0]

    return HZee, Zee_val, Zee_vec


def calc_oef(n, J, L, S):
    """ 
    Calculate operator equivalent factors for Stevens Crystal Field
    Hamiltonian in |J, mJ> basis

    Using the approach of
    https://arxiv.org/pdf/0803.4358.pdf

    Parameters:
        n (int) : number of electrons in f shell
        J (int) : J Quantum number
        L (int) : L Quantum number
        S (int) : S Quantum number

    Returns:
        oefs (np.array) : array of operator equivalent factors for
                          each parameter k,q
    """

    def _oef_lambda(p, J, L, S):
        lam = (-1)**(J+L+S+p)*(2*J+1)
        lam *= wigner_6j(J, J, p, L, L, S)/wigner_3j(p, L, L, 0, L, -L)
        return lam

    def _oef_k(p, k, n):
        K = 7. * wigner_3j(p, 3, 3, 0, 0, 0)
        if n <= 7:
            n_max = n
        else:
            n_max = n-7
            if k == 0:
                K -= np.sqrt(7)

        Kay = 0
        for j in range(1, n_max+1):
            Kay += (-1.)**j * wigner_3j(k, 3, 3, 0, 4-j, j-4)

        return K*Kay

    def _oef_RedJ(J, p):
        return 1./(2.**p) * (ut.factorial(2*J+p+1)/ut.factorial(2*J-p))**0.5

    # Calculate OEFs and store in array
    # Each parameter Bkq has its own parameter
    oef = np.zeros(27)
    shift = 0
    for k in range(2, int(2*J), 2):
        oef[shift:shift + 2*k+1] = float(_oef_lambda(k, J, L, S))
        oef[shift:shift + 2*k+1] *= float(_oef_k(k, k, n) / _oef_RedJ(J, k))
        shift += 2*k + 1

    return oef


def _evolve_trans_mat(J, Jz_expect, trans, scale_trans=True,
                      allowed_trans="forwards", normalise=True):
    """
    Scales transition matrix by "amount" coming into each state
    and removes backwards or downwards transitions

    Positional arguments:
        J (float)             : J quantum number
        Jz_expect (np.array)  : 1D array of <Jz> in eigenbasis of HCF
        trans (np.array)      : Matrix representation of magnetic transition
                                 dipole moment operator
    Keyword arguments:
        allowed_trans (str) : Which transitions should be plotted:
                                forwards: Only those which move up and over
                                          barrier
                                all : All transitions
        scale_trans (bool)  : If true, scale all outgoing transitions from
                              a state by amount coming in.
        normalise   (bool)  : If true, normalise all transitions from a state
                              by their sum

    Returns:
        output_trans (np.array)    : Matrix representation of magnetic
                                      transition dipole moment operator after
                                      scaling

    """

    # Calculate number of states
    n_states = int(2 * J + 1)

    # Remove self transitions
    np.fill_diagonal(trans, 0.)

    # Remove all transitions backwards over the barrier
    # or downwards between states
    if allowed_trans == "forwards":
        for i in np.arange(n_states):  # from
            for f in np.arange(n_states):  # to
                if Jz_expect[i] > Jz_expect[f]:
                    trans[f, i] = 0.  # No backwards or downwards steps

    # Normalise each column so transition probability is a fraction of 1
    if normalise:
        for i in np.arange(n_states):
            total = 0.
            total = sum(trans[:, i])
            if total > 0.:
                trans[:, i] = trans[:, i] / total

    # Find indexing which relates the current arrrangement of the array
    # Jz_expect to the arrangement it would
    # have if it was written in descending order (largest first)
    # This is done because our pathway consists only of transitions which
    # increase (-ve to eventually +ve) <Jz>
    index = Jz_expect.argsort()

    # Scale transition probability by amount coming into each state
    # Assume unit "population" of ground state (Jz=-J)
    # i.e. trans[:,index[0]] is already 1
    if scale_trans:
        for ind in index:
            if ind == 0:
                continue
            else:
                # scale outward by inward
                trans[:, ind] *= np.sum(trans[ind, :])

    # Scale matrix to be a percentage
    trans = 100. * trans

    # Find transitions with >1% probability
    # write their indices to an array along with the probabilty as a decimal
    # this is used to set the transparency of the arrows on the plot
    num_trans = 0
    output_trans = []
    for row in np.arange(n_states):
        for col in np.arange(n_states):
            if trans[row, col] > 1.:
                alpha = float(trans[row, col] / 100.0)
                if alpha > 1.:
                    alpha = 1.
                output_trans.append([row, col, alpha])
                num_trans += 1

    return output_trans, num_trans


def barrier_figure(J, energies, Jz_expect, trans=False, ax_in=False,
                   trans_colour="#ff0000", state_colour="black",
                   yax2=False, yax2_conv=1.4, figsize=[7, 5.5],
                   show=False, save=True, save_name="barrier.svg",
                   allowed_trans="forwards", normalise_trans=True,
                   scale_trans=True, initial_state="max_moment",
                   levels_name="", xlabel=r"$\langle \ \hat{J}_{z} \ \rangle$",
                   ylabel=r"Energy (cm$^{-1}$)", yax2_label="Energy (K)"):

    """
    Plots barrier figure with transition intensities from user provided matrix
    Y axis is Energy in cm-1, x axis is <Jz> of each state
    Arrows are transitions with intensity specified by specified by trans array

    Positional arguments:
        J (float)         : J or L or S quantum number
        energies (list)     : List of state energies
        Jz_expect (list)  : List of <Jz> for each state

    Keyword arguments:
        trans (np.array)  : Matrix of transition probabilities between states
        ax_in  (matplotlib axis object)   : Axis to use for plot
        trans_colour (str) : Hex code or name specifying arrow colours
        state_colour (str) : Hex code or name specifying state colours
        yax2 (bool)        : If True use secondary y (energy) axis
        yax2_conv (float)  : Conversion factor from primary to secondary y axis
        figsize (list)     : Size of figure [width, height] in inches
        show (bool)        : If True, show plot on screen - disabled with ax_in
        save (bool)        : If True, save plot to file - disabled with ax_in
        save_name (str)    : Filename for saved image
        allowed_trans (str) : Which transitions should be plotted:
                                forwards: Only those which move up and over
                                          barrier
                                all : All transitions
        normalise_trans (bool) : If True, normalise all transitions out of a
                                state by their sum
        scale_trans (bool)  : If true, scale all outgoing transitions from
                              a state by amount coming in.
        initial_state (str) : Which state has unit population when scale_trans
                              is used. Either 'max_moment' or 'lowest_energy'
        levels_name (str)   : Label name for energy levels
        xlabel (str)        : Plot x label
        ylabel (str)        : Plot y label
        yax2_label (str)    : Label for secondary y (energy) axis

    Returns:
        fig (matplotlib figure object) : Figure window handle
        axes  (matplotlib axis object)   : Axes for current plot
    """

    # Create plot and axes
    if not ax_in:
        fig, ax = plt.subplots(1, 1, sharey='all', figsize=figsize)
    else:
        fig = None
        ax = ax_in

    if yax2:
        ax2 = ax.twinx()
        axes = [ax, ax2]
    else:
        axes = [ax]

    # Draw energy level lines
    ax.plot(
        Jz_expect,
        energies,
        marker='_',
        markersize='25',
        mew='2.5',
        linewidth=0,
        color=state_colour,
        label=levels_name
        )

    # Plot transition arrows
    if isinstance(trans, np.ndarray):

        # Evolve transition matrix and find allowed transitions
        output_trans, num_trans = _evolve_trans_mat(J, Jz_expect, trans,
                                                    allowed_trans=allowed_trans,
                                                    normalise=normalise_trans)

        np.savetxt("inputtrans.dat", trans)
        np.savetxt("outputtrans.dat", output_trans)

        # Final <Jz>
        Jz_expect_final = [
                           Jz_expect[output_trans[row][1]]
                           for row in range(num_trans)
                          ]

        # Difference between initial and final <Jz>
        Jz_expect_diff = [
                          Jz_expect[output_trans[row][0]]-Jz_expect[output_trans[row][1]]
                          for row in range(num_trans)
                         ]

        # Final energies
        energies_final = [energies[output_trans[row][1]] for row in range(num_trans)]

        # Difference between initial and final energies
        energies_diff = [
                         energies[output_trans[row][0]] - energies[output_trans[row][1]]
                         for row in range(num_trans)
                        ]

        # Alpha channel values
        alphas = [output_trans[row][2] for row in range(num_trans)]

        # Make colours array
        # Columns are red, green, blue, alpha
        t_rgba_colors = np.zeros((num_trans, 4))

        # Convert user hex to rgb
        t_rgba_colors[:, 0:3] = ut.hex_to_rgb(trans_colour)

        t_rgba_colors[:, 3] = np.asarray(alphas)

        # Draw lines between levels
        ax.quiver(
                  Jz_expect_final,
                  energies_final,
                  Jz_expect_diff,
                  energies_diff,
                  scale_units='xy',
                  angles='xy',
                  scale=1,
                  color=t_rgba_colors
                )

    # Set x axis options
    ax.set_xlabel(xlabel)
    ax.tick_params(axis='both', which='both', length=2.0)
    ax.xaxis.set_major_locator(plt.MaxNLocator(8))

    # Set y axis options for cm-1
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_locator(plt.MaxNLocator(7))

    # Set y axis options for K
    if yax2:
        ax2.set_ylabel(yax2_label)
        ax2.set_ylim(
                     ax.get_ylim()[0] * yax2_conv,
                     ax.get_ylim()[1] * yax2_conv
                    )
        ax2.yaxis.set_major_locator(plt.MaxNLocator(7))

    # Set axis limits
    ax.set_xlim([-J * 1.1, J * 1.1])

    # Set number and position of x axis ticks
    ax.set_xticks(np.arange(-J, J + 1, 1))

    # Set x axis tick labels
    labels = []

    # Fractions if J non-integer
    if J % 2 != 0:
        for it in np.arange(0, int(2 * J + 1)):
            labels.append(str(-int(2 * J) + 2 * it) + '/2')
    else:
        for it in np.arange(0, int(2 * J + 1)):
            labels.append(str(-int(J) + it))

    ax.set_xticklabels(labels, rotation=45)

    if not ax_in:
        fig.tight_layout()
        # Save or show plot
        if save:
            fig.savefig(save_name, dpi=500)
        if show:
            plt.show()

    return fig, axes


def hunds_ground_term(n_elec, n_orb):
    """
    Calculate J, L, and S quantum numbers using number of
    electrons and orbitals

    Positional Arguments:
        n_elec (int) : Number of electrons
        n_orb (int)  : Number of orbitals (either 3, 5, or 7 i.e. (p, d, f))

    Returns:
        j (float) : Total angular momentum quantum number
        l (float) : Orbital angular momentum quantum number
        s (float) : Spin angular momentum quantum number
    """

    # Set constants for given shell
    if n_orb == 7:
        ml_vals = [3, 2, 1, 0, -1, -2, -3]
        max_s = 3.5
    elif n_orb == 5:
        ml_vals = [2, 1, 0, -1, -2]
        max_s = 2.5
    elif n_orb == 3:
        ml_vals = [1, 0, -1]
        max_s = 1.5
    else:
        print('Unsupported number of orbitals: {:d}'.format(n_orb))
        exit()

    # More than half filled
    if n_elec > n_orb:
        s = max_s - float(n_elec - n_orb) * 0.5
        l = float(sum(ml_vals[:n_elec - n_orb]))
        j = l + s
    # Less than half filled
    elif n_elec < n_orb:
        s = 0.5 * float(n_elec)
        l = float(sum(ml_vals[:n_elec]))
        j = l - s
    # Half filled
    elif n_elec == n_orb:
        s = max_s
        l = 0.
        j  = 0.

    return j, l, s
