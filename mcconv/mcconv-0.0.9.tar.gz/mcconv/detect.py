from .file_types import McFileTypes
import pathlib


def detect_mc_type(file_name: str) -> McFileTypes:
    """Tries to detect a file type"""

    if pathlib.Path(file_name).suffix == ".root":
        return McFileTypes.EIC_SMEAR

    with open(file_name, 'r') as f:
        line = ""
        try:
            i = 0
            while not line:                 # Just to fake a lot of readlines and hit the end
                line = next(f).replace('\n', '')

                # Don't go too far away if one can't determine file type
                i += 1
                if i > 20:
                    break

        except StopIteration:
            return McFileTypes.UNKNOWN

        # Determining file types
        if "BEAGLE EVENT FILE" in line:
            return McFileTypes.BEAGLE
        elif "HepMC::Version 2" in line:
            return McFileTypes.HEPMC2
        elif "HepMC::Version 3" in line:
            return McFileTypes.HEPMC3
        elif "PYTHIA EVENT FILE" in line:
            return McFileTypes.PYTHIA6_EIC
        elif len(line.split()) == 10:
            return McFileTypes.LUND_GEMC
    return McFileTypes.UNKNOWN

