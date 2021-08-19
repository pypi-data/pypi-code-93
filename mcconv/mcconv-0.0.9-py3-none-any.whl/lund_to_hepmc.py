from pyHepMC3 import HepMC3 as hm

from mcconv import McFileTypes, UnparsedTextEvent


def add_hepmc_attribute(obj, name, str_value, val_type):
    if val_type == int:
        obj.add_attribute(name, hm.IntAttribute(int(str_value)))
    if val_type == float:
        obj.add_attribute(name, hm.FloatAttribute(float(str_value)))
    if val_type == str:
        obj.add_attribute(name, hm.StringAttribute(str_value))


LUND_RULES = {
    "px": 6,        # Column where px is stored
    "py": 7,        # Column where py is stored
    "pz": 8,        # Column where pz is stored
    "e": 9,         # Energy
    "pid": 2,       # PID of particle (PDG code)
    "status": 1,    # Status
    "evt_attrs": {"weight": (9, float)},        # That is how one can store event level data
    "prt_attrs": {}
}

LUND_GEMC_RULES = {
    "px": 6,        # Column where px is stored
    "py": 7,        # Column where py is stored
    "pz": 8,        # Column where pz is stored
    "e": 9,         # Energy
    "pid": 3,       # PID of particle (PDG code)
    "status": 2,    # Status
    "evt_attrs": {"weight": (9, float)},        # That is how one can store event level data
    "prt_attrs": {"life_time": (1, float)},     # In LUND GemC the second col. (index 1) is life time.
    # If that is need to be stored, that is how to store it
}

BEAGLE_RULES = LUND_RULES
BEAGLE_RULES["evt_attrs"] = {}    # TODO event attributes for BEAGLE

# A map of rules by HepMC
LUND_CONV_RULES = {
    McFileTypes.BEAGLE: BEAGLE_RULES,
    McFileTypes.LUND: LUND_RULES,
    McFileTypes.LUND_GEMC: LUND_GEMC_RULES,
    McFileTypes.PYTHIA6_EIC: LUND_RULES
}


def lund_to_hepmc(hepmc_evt, unparsed_event, rules):
    """
        Rules define columns, that are used for extraction of parameters

        rules = {
            "px": 6,        # Column where px is stored
            "py": 7,        # Column where py is stored
            "pz": 8,        # Column where pz is stored
            "e": 9,         # Energy
            "pid": 2,       # PID of particle (PDG code)
            "status": 1,    # Status
            "evt_attrs": {"weight": (9, float)},        # That is how one can store event level data
            "prt_attrs": {"life_time": (1, float)},     # In LUND GemC the second col. (index 1) is life time.
                                                        # If that is need to be stored, that is how to store it

        }
        rules["px"]
        rules["py"]
        rules["pz"]
        rules["e"]
        rules["pid"]
        rules["status"]
        rules["evt_attrs"]
        rules["prt_attrs"]

    """
    assert isinstance(unparsed_event, UnparsedTextEvent)

    prt_col_px = rules["px"]
    prt_col_py = rules["py"]
    prt_col_pz = rules["pz"]
    prt_col_e = rules["e"]
    prt_col_pid = rules["pid"]
    prt_col_status = rules["status"]
    evt_attrs = rules["evt_attrs"]
    prt_attrs = rules["prt_attrs"]

    hepmc_evt.add_attribute("start_line_index", hm.IntAttribute(unparsed_event.start_line_index))

    v1 = hm.GenVertex()

    #particles = parse_lund_particles(unparsed_event)
    for particle_line in unparsed_event.unparsed_particles:

        # Parse main columns with 4 vectors
        px = float(particle_line[prt_col_px])
        py = float(particle_line[prt_col_py])
        pz = float(particle_line[prt_col_pz])
        energy = float(particle_line[prt_col_e])
        pid = int(particle_line[prt_col_pid])
        status = int(particle_line[prt_col_status])

        # Take only final state particle
        if status not in [1, 4]:
            continue

        # Create a hepmc particle
        hm_particle = hm.GenParticle(hm.FourVector(px, py, pz, energy), pid, status)

        # Add particle level attributes
        for name, params in prt_attrs.items():
            column_index, field_type = params
            add_hepmc_attribute(hm_particle, name, column_index, field_type)

        # Add particle to event
        if status == 4:
            # Beam particle
            v1.add_particle_in(hm_particle)
        else:
            # All other particles
            v1.add_particle_out(hm_particle)


        # Add event level attributes
        for name, params in evt_attrs.items():
            column_index, field_type = params
            add_hepmc_attribute(hepmc_evt, name, column_index, field_type)

    hepmc_evt.add_vertex(v1)
    print(len(hepmc_evt.particles()))
    return hepmc_evt