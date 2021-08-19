import collections
from typing import List


from mcconv import GenericTextReader, UnparsedTextEvent


def _is_line_relevant(line):
    if line.strip():
        return True
    return False


def _is_event(tokens):
    return len(tokens) < 14  # Beagle event header has like 50 tokens, particle like 16


def _is_particle(tokens):
    return len(tokens) >= 14


class LundEventData:

    def __init__(self):
        """
        | 0        | Number of particles                         |
        | 1        | Mass number of the target (UD)              |
        | 2        | Atomic number oif the target (UD)           |
        | 3        | Target polarization (UD)                    |
        | 4        | Beam Polarization                           |
        | 5        | Beam type, electron=11, photon=22” (UD)     |
        | 6        | Beam energy (GeV) (UD)                      |
        | 7        | Interacted nucleon ID (2212 or 2112) (UD)   |
        | 8        | Process ID (UD)                             |
        | 9        | Event weight (UD)                           |
        """

class LundParticleData:
    """
    | 0  | line index, runs from 1 to nrTracks                                                                        |
    | 1  | status code KS (1: stable particles 11: particles which decay 55; radiative photon)                        |
    | 2  | particle KF code (211: pion, 2112:n, ....)                                                                 |
    | 3  | line number of parent particle                                                                             |
    | 4  | normally the line number of the first daughter; it is 0 for an undecayed particle or unfragmented parton   |
    | 5  | normally the line number of the last daughter; it is 0 for an undecayed particle or unfragmented parton.   |
    | 6  | px of particle                                                                                             |
    | 7  | py of particle                                                                                             |
    | 8  | pz of particle                                                                                             |
    | 9  | Energy of particle                                                                                         |
    | 10 | mass of particle                                                                                           |
    | 11 | x vertex information                                                                                       |
    | 12 | y vertex information                                                                                       |
    | 13 | z vertex information                                                                                       |
    """

    def __init__(self):
        self.id = -1
        self.status = 0
        self.pdg = 0
        self.parent_id = 0
        self.daughter_first = 0
        self.daughter_last = 0
        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0
        self.energy = 0.0
        self.mass = 0.0
        self.vtx_x = 0.0
        self.vtx_y = 0.0
        self.vtx_z = 0.0


class GemcLundParticleData:

    def __init__(self):
        """
        Event record:
          column       quantity
          0         **Number of particles**
          1         Mass number of the target (UD)
          2         Atomic number oif the target (UD)
          3         Target polarization  (UD)
          4         **Beam Polarization**
          5         Beam type, electron=11, photon=22" (UD)
          6         Beam energy (GeV)  (UD)
          7         Interacted nucleon ID (2212 or 2112)  (UD)
          8         Process ID (UD)
          9         Event weight (UD)

        Particle record:
          column    quantity
          0         **index**
          1         Lifetime [nanoseconds] (UD)
          2         **status (1 is active)**
          3         **particle ID**
          4         Index of the parent (UD)
          5         Index of the first daughter (UD)
          6         **momentum x   [GeV]**
          7         **momentum y   [GeV]**
          8         **momentum z   [GeV]**
          9         Energy of the particle [GeV] (UD)
          10        Mass of the particle [GeV] (UD)
          11        **vertex x [cm]**
          12        **vertex y [cm]**
          13        **vertex z [cm]**
        """

        self.id = -1
        self.lifetime = 0
        self.status = 0
        self.pdg = 0
        self.parent_id = 0
        self.daughter_first = 0
        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0
        self.energy = 0.0
        self.mass = 0.0
        self.vtx_x = 0.0
        self.vtx_y = 0.0
        self.vtx_z = 0.0


LundParticleTuple = collections.namedtuple('LundParticleTuple',
    [
        'id',
        'status',
        'pdg',
        'parent_id',
        'daughter_first',
        'daughter_last',
        'px',
        'py',
        'pz',
        'energy',
        'mass',
        'vtx_x',
        'vtx_y',
        'vtx_z',
    ])


def parse_lund_particle_tokens(particle_tokens):
    return LundParticleTuple(
    int(particle_tokens[0])     ,    # id
    int(particle_tokens[1])     ,    # status
    int(particle_tokens[2])     ,    # pdg
    int(particle_tokens[3])     ,    # parent_id
    int(particle_tokens[4])     ,    # daughter_first
    int(particle_tokens[5])     ,    # daughter_last
    float(particle_tokens[6])   ,    # px
    float(particle_tokens[7])   ,    # py
    float(particle_tokens[8])   ,    # pz
    float(particle_tokens[9])   ,    # energy
    float(particle_tokens[10])  ,    # mass
    float(particle_tokens[11])  ,    # vtx_x
    float(particle_tokens[12])  ,    # vtx_y
    float(particle_tokens[13])  ,    # vtx_z
    )



def parse_lund_particles(unparsed_event: UnparsedTextEvent):

    particles = []
    for particle_tokens in unparsed_event.unparsed_particles:
        particle = LundParticleData()
        particle.id = int(particle_tokens[0])
        particle.status = int(particle_tokens[1])
        particle.pdg = int(particle_tokens[2])
        particle.parent_id = int(particle_tokens[3])
        particle.daughter_first = int(particle_tokens[4])
        particle.daughter_last = int(particle_tokens[5])
        particle.px = float(particle_tokens[6])
        particle.py = float(particle_tokens[7])
        particle.pz = float(particle_tokens[8])
        particle.energy = float(particle_tokens[9])
        particle.mass = float(particle_tokens[10])
        particle.vtx_x = float(particle_tokens[11])
        particle.vtx_y = float(particle_tokens[12])
        particle.vtx_z = float(particle_tokens[13])
        particles.append(particle)

    return particles


def parse_gemc_lund_particles(unparsed_event: UnparsedTextEvent):

    particles = []
    for particle_line in unparsed_event.unparsed_particles:
        particle = GemcLundParticleData()
        particle.id = int(particle_line[0])
        particle.lifetime = float(particle_line[1])
        particle.status = int(particle_line[2])
        particle.pdg = int(particle_line[3])
        particle.parent_id = int(particle_line[4])
        particle.daughter_first = int(particle_line[5])
        particle.px = float(particle_line[6])
        particle.py = float(particle_line[7])
        particle.pz = float(particle_line[8])
        particle.energy = float(particle_line[9])
        particle.mass = float(particle_line[10])
        particle.vtx_x = float(particle_line[11])
        particle.vtx_y = float(particle_line[12])
        particle.vtx_z = float(particle_line[13])
        particles.append(particle)

    return particles