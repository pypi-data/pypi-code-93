import logging
import time

from pyHepMC3 import HepMC3 as hm

from mcconv import detect_mc_type
from .formats.beagle import BeagleReader
from .generic_reader import GenericTextReader, UnparsedTextEvent
from .formats.lund import parse_lund_particles, parse_lund_particle_tokens
from .file_types import McFileTypes
from .eic_smear_reader import EicTreeReader, EicSmearEventData
from .lund_to_hepmc import LUND_CONV_RULES, lund_to_hepmc

logger = logging.getLogger("mcconv.hepmc_convert")


def hepmc_convert(input_file, output_file, input_type, hepmc_vers, progress_func=None, nskip=0, nprocess=0):

    # Choose the output format: hepmc 2 or 3 writer
    if hepmc_vers == 2 or hepmc_vers == "2" or (isinstance(hepmc_vers, str) and hepmc_vers.lower() == "hepmc2"):
        writer = hm.WriterAsciiHepMC2(output_file)
    else:
        writer = hm.WriterAscii(output_file)

    # What is the input type? Is it known?
    if not input_type or input_type == McFileTypes.UNKNOWN:
        logger.debug("Input file type is not given or UNKNOWN. Trying autodetect")

        # Input type is unknown, trying autodetection
        input_type = detect_mc_type(input_file)

    # If it is still UNKNOWN - we where unable to detect. Error raising
    if input_type == McFileTypes.UNKNOWN:
        raise ValueError("File format is UNKNOWN")

    # Set event reader according to file type
    if input_type == McFileTypes.EIC_SMEAR:
        reader = EicTreeReader()
    else:
        reader = GenericTextReader()

        if input_type == McFileTypes.BEAGLE:
            reader.particle_tokens_len = 18

    # Open input file
    reader.open(input_file)

    # This is basically the same as with statement. But HepMcWriter doesn't implement __enter__() etc.
    hepmc_event = hm.GenEvent(hm.Units.GEV, hm.Units.MM)
    start_time = time.time()
    try:
        # Iterate events
        for evt_index, source_event in enumerate(reader.events(nskip, nprocess)):

            # What conversion function to use?
            if input_type == McFileTypes.EIC_SMEAR:
                # ROOT format EIC_SMEAR
                eic_smear_to_hepmc(hepmc_event, source_event)
            elif input_type in LUND_CONV_RULES.keys():
                # One of LUND formats
                lund_to_hepmc(hepmc_event, source_event, LUND_CONV_RULES[input_type])

            # Write event
            writer.write_event(hepmc_event)

            # call progress func, so one could work on it
            if progress_func:
                progress_func(evt_index, hepmc_event)

            hepmc_event.clear()
    finally:
        # closing everything (we are not using with statement as it is not supported by HepMC)
        writer.close()
        reader.close()
        hepmc_event.clear()
        logger.info(f"Time for the conversion = {time.time() - start_time} sec")


def eic_smear_to_hepmc(hepmc_evt, source_evt):
    """

    """
    assert isinstance(source_evt, EicSmearEventData)

    v1 = hm.GenVertex()
    hepmc_evt.add_vertex(v1)

    #particles = parse_lund_particles(unparsed_event)
    for particle in source_evt.particles:

        # Create a hepmc particle
        hm_particle = hm.GenParticle(hm.FourVector(particle.px, particle.py, particle.pz, particle.energy),
                                     particle.pid,
                                     particle.status)

        # Add particle to event
        hepmc_evt.add_particle(hm_particle)

    return hepmc_evt