import uproot
import os
from pprint import pprint

def _data_path(file_name):
    """Gets data file path"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, 'data', file_name)

local_file = uproot.open(_data_path('eic_DEMPGen_10on100_1B_1_100.root'))

#for event in local_file['EICTree']
pprint(local_file['EICTree'].typenames())

rules = {
    'id': 'event/erhic::EventMC/particles/particles.id',
    'px': 'event/erhic::EventMC/particles/particles.px',
    'py': 'event/erhic::EventMC/particles/particles.py',
    'pz': 'event/erhic::EventMC/particles/particles.pz',
    'e': 'event/erhic::EventMC/particles/particles.E',
    'ks': 'event/erhic::EventMC/particles/particles.KS',
    'vtx_x':  'event/erhic::EventMC/particles/particles.xv',
    'vtx_y':  'event/erhic::EventMC/particles/particles.yv',
    'vtx_z':  'event/erhic::EventMC/particles/particles.zv',
}

branch_names = [
    rules['id'],
    rules['px'],
    rules['py'],
    rules['pz'],
    rules['e'],
    rules['ks'],
    rules['vtx_x'],
    rules['vtx_y'],
    rules['vtx_z']
]

for events in local_file['EICTree'].iterate(branch_names, step_size=100, entry_start=0, entry_stop=2):
    for event in events:
        for particle in zip(event[rules['id']], event[rules['px']], event[rules['py']], event[rules['pz']], event[rules['e']], event[rules['ks']], event[rules['vtx_x']], event[rules['vtx_y']], event[rules['vtx_z']]):
            print(particle)
    print("-------------------------------------------")