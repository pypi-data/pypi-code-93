"""
Reads EicSmear tree (aka EicTree) and converts to hepmc
The class uses uproot, so it has to be installed
"""

import io
import enum
import logging

from typing import AnyStr, Callable, List
import re
import uproot
import os

# the default ccdb logger

logger = logging.getLogger("mcconv.eic_smear_reader")


class EicSmearParticleData:
    """Holds basic information on EicSmearParticle"""
    def __init__(self, pid, px, py, pz, e, status, vtx_x, vtx_y, vtx_z):
        self.pid = pid
        self.px = px
        self.py = py
        self.pz = pz
        self.energy = e
        self.status = status
        self.vtx_x = vtx_x
        self.vtx_y = vtx_y
        self.vtx_z = vtx_z


class EicSmearEventData:

    def __init__(self, particles):
        self.io_event_index = 0
        self.particles: List[EicSmearParticleData] = particles


class EicTreeReader:
    """Class EicTree reader"""

    batch_size = 1000

    def __init__(self, file=None, file_path=""):
        self.file_path = file_path
        self.file = file
        self.event_index = 0

    def open(self, file_path):
        self.file_path = file_path
        self.file = uproot.open(self.file_path)
        self.event_index = 0

    def close(self):
        if self.file:
            self.file.close()

    def events(self, evt_skip: int = 0, evt_take: int = 0):
        """Generator, reads event by event"""

        # Root files branches names:
        branch_pid = 'event/erhic::EventMC/particles/particles.id'
        branch_px = 'event/erhic::EventMC/particles/particles.px'
        branch_py = 'event/erhic::EventMC/particles/particles.py'
        branch_pz = 'event/erhic::EventMC/particles/particles.pz'
        branch_e = 'event/erhic::EventMC/particles/particles.E'
        branch_status = 'event/erhic::EventMC/particles/particles.KS'
        branch_vtx_x = 'event/erhic::EventMC/particles/particles.xv'
        branch_vtx_y = 'event/erhic::EventMC/particles/particles.yv'
        branch_vtx_z = 'event/erhic::EventMC/particles/particles.zv'

        # for convenience
        all_branches = [
            branch_pid,
            branch_px,
            branch_py,
            branch_pz,
            branch_e,
            branch_status,
            branch_vtx_x,
            branch_vtx_y,
            branch_vtx_z,
        ]

        print(self.file['EICTree'].num_entries)

        # In uproot you have to specify top index to read instead of how many events to take
        # None - take all events
        entry_stop = evt_skip + evt_take if evt_take else None

        for batch in self.file['EICTree'].iterate(all_branches, step_size=self.batch_size*10, entry_start=evt_skip, entry_stop=entry_stop, report=True):
            events, report = batch
            print(report)
            for event in events:
                particles = []
                for data in zip(event[branch_pid],
                                    event[branch_px],
                                    event[branch_py],
                                    event[branch_pz],
                                    event[branch_e],
                                    event[branch_status],
                                    event[branch_vtx_x],
                                    event[branch_vtx_y],
                                    event[branch_vtx_z]):
                    particle = EicSmearParticleData(*data)
                    particles.append(particle)
                yield EicSmearEventData(particles)
                self.event_index += 1

    def to_pandas(self, event_fields, particle_fields, chunk_size=0):
        """
        Converts events to pandas data frame.

        If
        """
        raise NotImplementedError("to_pandas function is not implemented for EicTreeReader")


