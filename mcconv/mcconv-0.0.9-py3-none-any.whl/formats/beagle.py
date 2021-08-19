from mcconv import GenericTextReader, UnparsedTextEvent


def _is_line_relevant(line):
    is_comment = any(word in line for word in ['BEAGLE', 'I', '='])
    return not is_comment


def _is_event(tokens):
    return len(tokens) > 20  # Beagle event header has like 50 tokens, particle like 16


def _is_particle(tokens):
    return len(tokens) < 20


class BeagleReader(GenericTextReader):

    def __init__(self):
        super().__init__(_is_line_relevant, _is_event, _is_particle)

    def unparsed_events(self):
        """Just a proxy for an unparsed events"""
        for event in super().events():
            yield event

    def events(self):
        """Generator, reads event by event"""

        for event in super().events():
            assert isinstance(event, UnparsedTextEvent)





class BeagleEventData:

    def __init__(self, unparsed_event):

        self.unparsed_event = unparsed_event

        self.event_index = -1              # Usually it what people call 'event number' but the 'number' is very misleading
        self.started_at_line = -1

        self.genevent: int = 0             # 2 I  trials to generate this event
        self.ltype: int = 0                # 3 I  particle code for incoming lepton
        self.a_targ: int = 0               # 4 I  A of the target nucleus
        self.z_targ: int = 0               # 5 I  Z of the target nucleus
        self.pzlep: float = 0              # 6 D  lab pz of the lepton beam (sign(pz)*p for non-zero crossing angle)
        self.pztarg: float = 0             # 7 D  lab pz/A of the ion beam (sign(pz)*p/A for non-zero crossing angle)
        self.pznucl: float = 0             # 8 D  lab pz of the struck nucleon (sign(pz)*p for non-zero crossing angle)
        self.crang: float = 0              # 9 D  crossing-angle (mr). crang = (1000*) atan(px/pz) for the beam momentum with nonzero px. Note: we assume one of the beams has px=py=0 and the other py=0.
        self.crori: int = 0                # 10 I  crossing angle orientation. lepton beam defines \pm\hat{z} direction. \pm 2 hadron/ion beam defines
                                           # \pm\hat{z} direction. 0 means no crossing angle.
        self.subprocess: int = 0           # 11 I   pythia subprocess (MSTI(1)), for details see PYTHIA
        self.nucleon: int = 0              # 12 I   hadron beam type (MSTI(12))
        self.targetparton: int = 0         # 13 I  parton hit in the target (MSTI(16))
        self.xtargparton: float = 0        # 14 D  x of target parton (PARI(34))
        self.beamparton: int = 0           # 15 I  in case of resolved photon processes and soft VMD the virtual photon has a hadronic structure. This gives the info which parton interacted with the target parton (MSTI(15))
        self.xbeamparton: float = 0        # 16 D  x of beam parton (PARI(33))
        self.thetabeamparton: float = 0    # 17 D  theta of beam parton (PARI(53))
        self.truey: float = 0              # 18 D  are the kinematic variables of the event.
        self.trueQ2: float = 0             # 19 D  are the kinematic variables of the event.
        self.truex: float = 0              # 20 D  are the kinematic variables of the event.
        self.trueW2: float = 0             # 21 D  are the kinematic variables of the event.
        self.trueNu: float = 0             # 22 D  are the kinematic variables of the event.
                                           #       If radiative corrections are turned on they are different from what is calculated from the scattered lepton.
                                           #       If radiative corrections are turned off they are the same as what is calculated from the scattered lepton
        self.leptonphi: float = 0          # 23 D  phi of the lepton (VINT(313)) in the laboratory frame
        self.s_hat: float = 0              # 24 D  s-hat of the process (PARI(14))
        self.t_hat: float = 0              # 25 D  Mandelstam t (PARI(15))
        self.u_hat: float = 0              # 26 D  Mandelstam u (PARI(16))
        self.pt2_hat: float = 0            # 27 D  pT2-hat of the hard scattering (PARI(18))
        self.Q2_hat: float = 0             # 28 D  Q2-hat of the hard scattering (PARI(22)),
        self.F2: float = 0                 # 29 D  information used and needed in the radiative correction code
        self.F1: float = 0                 # 30 D  information used and needed in the radiative correction code
        self.R: float = 0                  # 31 D  information used and needed in the radiative correction code
        self.sigma_rad: float = 0          # 32 D  information used and needed in the radiative correction code
        self.SigRadCor: float = 0          # 33 D  information used and needed in the radiative correction code
        self.EBrems: float = 0             # 34 D  energy of the radiative photon in the nuclear rest frame
        self.photonflux: float = 0         # 35 D  flux factor from PYTHIA (VINT(319))
        self.b: float = 0                  # 36 D  Impact parameter (in fm), radial position of virtual photon w.r.t. the center of the nucleus in the nuclear TRF with z along γ*
        self.Phib: float = 0               # 37 D  azimuthal angle of the impact parameter of the virtual photon in the nuclear TRF with z along γ* and φ=0 for the scattered electron
        self.Thickness: float = 0          # 38 D  Nuclear thickness T(b)/ρ0 in units of fm.
        self.ThickScl: float = 0           # 39 D  Nuclear thickness T(b) in nucleons/fm2.
        self.Ncollt: int = 0               # 40 I  Number of collisions between the incoming γ* and nucleons in the nucleus (same as number of participating nucleons)
        self.Ncolli: int = 0               # 41 I  Number of inelastic collisions between the incoming γ* and nucleons in the nucleus (same as number of inelastically participating nucleons)
        self.Nwound: int = 0               # 42 I  Number of wounded nucleons, including those involved in the intranuclear cascade. WARNING: This variable is not finalized yet
        self.Nwdch: int = 0                # 43 I  Number of wounded protons, including those involved in the intranuclear cascade. WARNING: This variable is not finalized yet
        self.Nnevap: int = 0               # 44 I  Number of evaporation (and nuclear breakup) neutrons
        self.Npevap: int = 0               # 45 I  Number of evaporation (and nuclear breakup) protons
        self.Aremn: int = 0                # 46 I  A of the nuclear remnant after evaporation and breakup
        self.Ninc: int = 0                 # 47 I  Number of stable hadrons from the Intra Nuclear Cascade
        self.Nincch: int = 0               # 48 I  Number of charged stable hadrons from the Intra Nuclear Cascade
        self.d1st: float = 0               # 49 D  density-weighted distance from first collision to the edge of the nucleus (amount of material traversed / ρ0)
        self.davg: float = 0               # 50 D  Average density-weighted distance from all inelastic collisions to the edge of the nucleus
        self.pxf: float = 0                # 51 D  Fermi-momentum of the struck nucleon (or sum Fermi momentum for all inelastic nucleon participants for Ncolli>1) in target rest frame with z along gamma* direction
        self.pyf: float = 0                # 52 D  Fermi-momentum of the struck nucleon (or sum Fermi momentum for all inelastic nucleon participants for Ncolli>1) in target rest frame with z along gamma* direction
        self.pzf: float = 0                # 53 D  Fermi-momentum of the struck nucleon (or sum Fermi momentum for all inelastic nucleon participants for Ncolli>1) in target rest frame with z along gamma* direction
        self.Eexc: float = 0               # 54 D  Excitation energy in the nuclear remnant before evaporation and breakup.
        self.RA: float = 0                 # 55 D  Nuclear PDF ratio for the up sea for the given event kinematics (x,Q2), but set to 1 if multi-nucleon shadowing is off (genShd=1)
        self.User1: float = 0              # 56 D  User variables to prevent/delay future format changes
        self.User2: float = 0              # 57 D  User variables to prevent/delay future format changes
        self.User3: float = 0              # 58 D  User variables to prevent/delay future format changes
        self.nrTracks: int = 0             # 59 I  number of tracks in this event, including event history


def beagle_parse_event(unparsed_event: UnparsedTextEvent) -> BeagleEventData:
    event_tokens = unparsed_event.event_tokens
    event = BeagleEventData(unparsed_event)

    # event_tokens[0] I  line num (always zero in file)
    event.event_index  = int(event_tokens[1])         # 1  I ievent - event num
    event.genevent     = int(event_tokens[2])         # 2  I trials to generate this event
    event.ltype        = int(event_tokens[3])         # 3  I particle code for incoming lepton
    event.a_targ       = int(event_tokens[4])         # 4  I A of the target nucleus
    event.z_targ       = int(event_tokens[5])         # 5  I Z of the target nucleus
    event.pzlep        = float(event_tokens[6])       # 6  D lab pz of the lepton beam (sign(pz)*p for non-zero crossing angle)
    event.pztarg       = float(event_tokens[7])       # 7  D lab pz/A of the ion beam (sign(pz)*p/A for non-zero crossing angle)
    event.pznucl       = float(event_tokens[8])       # 8  D lab pz of the struck nucleon (sign(pz)*p for non-zero crossing angle)
    event.crang        = float(event_tokens[9])       # 9  D crossing-angle (mr). crang = (1000*) atan(px/pz) for the beam momentum with nonzero px. Note: we assume one of the beams has px=py=0 and the other py=0.
    event.crori        = int(event_tokens[10])        # 10 I  crossing angle orientation. lepton beam defines \pm\hat{z} direction. \pm 2 hadron/ion beam defines                                                                    #    \pm\hat{z} direction. 0 means no crossing angle.
    event.subprocess   = int(event_tokens[11])        # 11 I   pythia subprocess (MSTI(1)), for details see PYTHIA
    event.nucleon      = int(event_tokens[12])        # 12 I   hadron beam type (MSTI(12))
    event.targetparton =    int(event_tokens[13])     # 13 I  parton hit in the target (MSTI(16))
    event.xtargparton =     float(event_tokens[14])   # 14 D  x of target parton (PARI(34))
    event.beamparton =      int(event_tokens[15])     # 15 I  in case of resolved photon processes and soft VMD the virtual photon has a hadronic structure. This gives the info which parton interacted with the target parton (MSTI(15))
    event.xbeamparton =     float(event_tokens[16])   # 16 D  x of beam parton (PARI(33))
    event.thetabeamparton = float(event_tokens[17])   # 17 D  theta of beam parton (PARI(53))
    event.truey =           float(event_tokens[18])   # 18 D  are the kinematic variables of the event.
    event.trueQ2 =          float(event_tokens[19])   # 19 D  are the kinematic variables of the event.
    event.truex =           float(event_tokens[20])   # 20 D  are the kinematic variables of the event.
    event.trueW2 =          float(event_tokens[21])   # 21 D  are the kinematic variables of the event.
    event.trueNu =          float(event_tokens[22])   # 22 D  are the kinematic variables of the event.
    event.leptonphi =       float(event_tokens[23])   # 23 D  phi of the lepton (VINT(313)) in the laboratory frame
    event.s_hat =           float(event_tokens[24])   # 24 D  s-hat of the process (PARI(14))
    event.t_hat =           float(event_tokens[25])   # 25 D  Mandelstam t (PARI(15))
    event.u_hat =           float(event_tokens[26])   # 26 D  Mandelstam u (PARI(16))
    event.pt2_hat =         float(event_tokens[27])   # 27 D  pT2-hat of the hard scattering (PARI(18))
    event.Q2_hat =          float(event_tokens[28])   # 28 D  Q2-hat of the hard scattering (PARI(22)),
    event.F2 =              float(event_tokens[29])   # 29 D  information used and needed in the radiative correction code
    event.F1 =              float(event_tokens[30])   # 30 D  information used and needed in the radiative correction code
    event.R =               float(event_tokens[31])   # 31 D  information used and needed in the radiative correction code
    event.sigma_rad =       float(event_tokens[32])   # 32 D  information used and needed in the radiative correction code
    event.SigRadCor =       float(event_tokens[33])   # 33 D  information used and needed in the radiative correction code
    event.EBrems =          float(event_tokens[34])   # 34 D  energy of the radiative photon in the nuclear rest frame
    event.photonflux =      float(event_tokens[35])   # 35 D  flux factor from PYTHIA (VINT(319))
    event.b =               float(event_tokens[36])   # 36 D  Impact parameter (in fm), radial position of virtual photon w.r.t. the center of the nucleus in the nuclear TRF with z along γ*
    event.Phib =            float(event_tokens[37])   # 37 D  azimuthal angle of the impact parameter of the virtual photon in the nuclear TRF with z along γ* and φ=0 for the scattered electron
    event.Thickness =       float(event_tokens[38])   # 38 D  Nuclear thickness T(b)/ρ0 in units of fm.
    event.ThickScl =        float(event_tokens[39])   # 39 D  Nuclear thickness T(b) in nucleons/fm2.
    event.Ncollt =          int(event_tokens[40])     # 40 I  Number of collisions between the incoming γ* and nucleons in the nucleus (same as number of participating nucleons)
    event.Ncolli =          int(event_tokens[41])     # 41 I  Number of inelastic collisions between the incoming γ* and nucleons in the nucleus (same as number of inelastically participating nucleons)
    event.Nwound =          int(event_tokens[42])     # 42 I  Number of wounded nucleons, including those involved in the intranuclear cascade. WARNING: This variable is not finalized yet
    event.Nwdch =           int(event_tokens[43])     # 43 I  Number of wounded protons, including those involved in the intranuclear cascade. WARNING: This variable is not finalized yet
    event.Nnevap =          int(event_tokens[44])     # 44 I  Number of evaporation (and nuclear breakup) neutrons
    event.Npevap =          int(event_tokens[45])     # 45 I  Number of evaporation (and nuclear breakup) protons
    event.Aremn =           int(event_tokens[46])     # 46 I  A of the nuclear remnant after evaporation and breakup
    event.Ninc =            int(event_tokens[47])     # 47 I  Number of stable hadrons from the Intra Nuclear Cascade
    event.Nincch =          int(event_tokens[48])     # 48 I  Number of charged stable hadrons from the Intra Nuclear Cascade
    event.d1st =            float(event_tokens[49])   # 49 D  density-weighted distance from first collision to the edge of the nucleus (amount of material traversed / ρ0)
    event.davg =            float(event_tokens[50])   # 50 D  Average density-weighted distance from all inelastic collisions to the edge of the nucleus
    event.pxf =             float(event_tokens[51])   # 51 D  Fermi-momentum of the struck nucleon (or sum Fermi momentum for all inelastic nucleon participants for Ncolli>1) in target rest frame with z along gamma* direction
    event.pyf =             float(event_tokens[52])   # 52 D  Fermi-momentum of the struck nucleon (or sum Fermi momentum for all inelastic nucleon participants for Ncolli>1) in target rest frame with z along gamma* direction
    event.pzf =             float(event_tokens[53])   # 53 D  Fermi-momentum of the struck nucleon (or sum Fermi momentum for all inelastic nucleon participants for Ncolli>1) in target rest frame with z along gamma* direction
    event.Eexc =            float(event_tokens[54])   # 54 D  Excitation energy in the nuclear remnant before evaporation and breakup.
    event.RA =              float(event_tokens[55])   # 55 D  Nuclear PDF ratio for the up sea for the given event kinematics (x,Q2), but set to 1 if multi-nucleon shadowing is off (genShd=1)
    event.User1 =           float(event_tokens[56])   # 56 D  User variables to prevent/delay future format changes
    event.User2 =           float(event_tokens[57])   # 57 D  User variables to prevent/delay future format changes
    event.User3 =           float(event_tokens[58])   # 58 D  User variables to prevent/delay future format changes
    event.nrTracks =        int(event_tokens[59])     # 59 I  number of tracks in this event, including event history
    return event