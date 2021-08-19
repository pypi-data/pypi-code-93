#
# Import section
#
import numpy

from syned.beamline.beamline_element import BeamlineElement
from syned.beamline.element_coordinates import ElementCoordinates
from wofry.propagator.propagator import PropagationManager, PropagationElements, PropagationParameters

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

from wofryimpl.propagator.propagators1D.fresnel import Fresnel1D
from wofryimpl.propagator.propagators1D.fresnel_convolution import FresnelConvolution1D
from wofryimpl.propagator.propagators1D.fraunhofer import Fraunhofer1D
from wofryimpl.propagator.propagators1D.integral import Integral1D
from wofryimpl.propagator.propagators1D.fresnel_zoom import FresnelZoom1D
from wofryimpl.propagator.propagators1D.fresnel_zoom_scaling_theorem import FresnelZoomScaling1D


#
# AUXILIAR FINCTION(S)=========================
#
def get_CF_after_rediagonalization(sc, do_plot=False):
    # retrieve arrays
    WFs = sc.get_wavefronts()
    nmodes = sc.get_number_of_calls()
    abscissas = WFs[-1].get_abscissas()

    #
    # calculate the CSD
    #

    input_array = numpy.zeros((nmodes, abscissas.size), dtype=complex)
    for i, wf in enumerate(WFs):
        input_array[i, :] = wf.get_complex_amplitude()  # tmp[i][0]

    cross_spectral_density = numpy.zeros((abscissas.size, abscissas.size), dtype=complex)

    for i in range(nmodes):
        cross_spectral_density += numpy.outer(numpy.conjugate(input_array[i, :]), input_array[i, :])

    if do_plot:
        plot_image(numpy.abs(cross_spectral_density), 1e6 * abscissas, 1e6 * abscissas,
                   title="Cross Spectral Density", xtitle="X1 [um]", ytitle="X2 [um]")
    print("matrix cross_spectral_density: ", cross_spectral_density.shape)

    #
    # diagonalize the CSD
    #

    w, v = numpy.linalg.eig(cross_spectral_density)
    print(w.shape, v.shape)
    idx = w.argsort()[::-1]  # large to small
    eigenvalues = numpy.real(w[idx])
    eigenvectors = v[:, idx].T

    #
    # plot intensity
    #
    if do_plot:
        y = numpy.zeros_like(abscissas)

        for i in range(nmodes):
            y += eigenvalues[i] * numpy.real(numpy.conjugate(eigenvectors[i, :]) * eigenvectors[i, :])

        cumulated_intensity = sc.get_additional_stored_values()[-1][0]

        plot(1e6 * abscissas, cumulated_intensity,
             1e6 * abscissas, y, legend=["Data", "From modes"],
             xtitle="x [um]", ytitle="Spectral Density")

        plot(numpy.arange(nmodes), eigenvalues[0:nmodes] / (eigenvalues[0:nmodes].sum()),
             title="CF: %g" % (eigenvalues[0] / eigenvalues.sum()),
             xtitle="mode index", ytitle="occupation")

    return eigenvalues[0] / eigenvalues.sum()


#
# SOURCE========================
#


def run_source(my_mode_index=0):
    global coherent_mode_decomposition
    try:
        tmp = coherent_mode_decomposition
    except:

        ##########  SOURCE ##########

        #
        # create output_wavefront
        #
        #
        from wofryimpl.propagator.util.undulator_coherent_mode_decomposition_1d import \
            UndulatorCoherentModeDecomposition1D
        coherent_mode_decomposition = UndulatorCoherentModeDecomposition1D(
            electron_energy=6,
            electron_current=0.2,
            undulator_period=0.02,
            undulator_nperiods=100,
            K=1.19,
            photon_energy=10000,
            abscissas_interval=0.00025,
            number_of_points=800,
            distance_to_screen=100,
            scan_direction='V',
            sigmaxx=3.01836e-05,
            sigmaxpxp=4.36821e-06,
            useGSMapproximation=False, )
        # make calculation
        coherent_mode_decomposition_results = coherent_mode_decomposition.calculate()

        mode_index = 0
        output_wavefront = coherent_mode_decomposition.get_eigenvector_wavefront(mode_index)
    output_wavefront = coherent_mode_decomposition.get_eigenvector_wavefront(my_mode_index)
    return output_wavefront


#
# BEAMLINE========================
#


def run_beamline(output_wavefront):
    return output_wavefront


#
# MAIN========================
#


from srxraylib.plot.gol import plot, plot_image
from orangecontrib.esrf.wofry.util.score import Score

sc = Score(scan_variable_name='mode index', additional_stored_variable_names=['cumulated_intensity'],
           do_store_wavefronts=True)
for my_mode_index in range(100):
    output_wavefront = run_source(my_mode_index=my_mode_index)
    output_wavefront = run_beamline(output_wavefront)
    if my_mode_index == 0:
        intensity = output_wavefront.get_intensity()
    else:
        intensity += output_wavefront.get_intensity()
    sc.append(output_wavefront, scan_variable_value=my_mode_index, additional_stored_values=[intensity])
# plot(output_wavefront.get_abscissas(), output_wavefront.get_intensity(), title='LAST Mode %d' % my_mode_index)

cf = get_CF_after_rediagonalization(sc, do_plot=True)
print('Coherent fraction from new (rediagonalized) modes: %f ' % cf)