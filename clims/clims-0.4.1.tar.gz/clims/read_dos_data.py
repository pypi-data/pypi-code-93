import numpy as np
from pathlib import Path
import re


files = [x for x in Path(".").iterdir() if not x.is_dir()]

def get_file_name(pattern,files):
    for file in files:
        filename = file.as_posix()
        if pattern.search(filename) and not 'raw' in filename and not 'no_soc' in filename:
            return file
    raise FileNotFoundError
    
def get_mu(filename):
    f = open(filename)
    for _ in range(3):
        line = f.readline()
        if "chemical potential" in line:
            return float(line.split()[-2])
    raise

def read_species_dos(species, max_spin_channel):
    dos_species = {}
    maxdos = 0.0
    energy_lim = [100000,-100000]

    spinstrs = [ "" ]
    if max_spin_channel == 2:
        spinstrs = [ "_spin_up",r"_spin_d(ow)?n" ]
    
    for s in species:
        dos_species[s] = []
        for ss in spinstrs:
            pattern = re.compile(s+r"_l_proj_dos(\_tetrahedron)?"+ss)
            filename = get_file_name(pattern,files)
            mu = get_mu(filename)
            data = np.loadtxt(filename)
            maxdos = max(maxdos,data[:,1].max())
            dos_species[s].append(data)
            energy_lim = [
                min(data[:,0][0],energy_lim[0]),
                max(data[:,0][-1],energy_lim[1])
            ]
    dos_species['maxdos'] = maxdos
    dos_species['energy_lim'] = energy_lim
    
    return dos_species
        
def read_total_dos():
    pattern = re.compile("KS_DOS_total")
    filename = get_file_name(pattern,files)
    mu = get_mu(filename)
    data = np.loadtxt(filename)
    energy = data[:,0]
    dos = data[:,1:]
    maxdos = dos.max()
    energy_lim = [energy[0],energy[-1]]
    return energy, dos, maxdos, energy_lim
