import enum


class McFileTypes (enum.Enum):
    """Enumeration of known formats (unique strings)

    (!) Warning (!) Inside this library use 'import .file_types' not 'import mcconv.file_types'
    https://stackoverflow.com/a/61395054/548894

    Another thing on enums - values are uppercase because they are constants
    https://stackoverflow.com/a/21359677/548894
    """
    UNKNOWN = "unknown"
    BEAGLE = "beagle"
    HEPMC2 = "hepmc2"
    HEPMC3 = "hepmc3"
    LUND = "lund"
    LUND_GEMC = "lund_gemc"
    PYTHIA6_EIC = "pythia_bnl"
    EIC_SMEAR = "eic_smear"


def parse_file_type(in_string, raise_on_unknown=True):
    if not in_string or in_string == "unknown":
        return McFileTypes.UNKNOWN
    if in_string == "beagle":
        return McFileTypes.BEAGLE
    if in_string == "hepmc2":
        return McFileTypes.HEPMC2
    if in_string == "hepmc3":
        return McFileTypes.HEPMC300
    if in_string == "pythia_bnl":
        return McFileTypes.PYTHIA6_EIC
    if in_string in ["lund", "pythia_lund", "lund_pythia", "lund_py6"]:
        return McFileTypes.LUND
    if in_string == ["pythia_gemc", "lund_gemc"]:
        return McFileTypes.LUND_GEMC

    if raise_on_unknown:
        message = f"File type='{in_string}' is unknown"
        raise ValueError(message)

    return McFileTypes.UNKNOWN