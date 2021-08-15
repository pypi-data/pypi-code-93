# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_config.ipynb (unless otherwise specified).

__all__ = ['Cache', 'Config', 'MJD', 'UTC', 'UTCnow', 'day', 'first_data', 'mission_start', 'bin_size_name',
           'decorate_with', 'df_4fgl']

# Cell
from astropy.time import Time
# from astropy.coordinates import SkyCoord, Angle
import astropy.units as u
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple
import os, sys
import numpy as np
import pickle

# Cell

class Cache(dict):
    """
    Manage a file cache

    - `path` -- string or `filepath` object <br> This is the folder where the index and data files are saved.
    - `clear` -- set True to clear the cache on initialization

    This uses pickle to save objects, associated with a hashable key, which is used to index the
    filename in a file `index.pkl` in the same folder.

    The `__call__` function is a convenient way to use it, so one call may either store a new entry or retrieve an existing one.

    """

    def __init__(self, path, clear:bool=False):

        self.path = Path(path) if path else None
        if self.path is None: return
        if not self.path.exists() :
            print(f'Warning: cache Path {self.path} does not exist, cache disabled ',file=sys.stderr)
            self.path=None
            return

        self.index_file = self.path/'index.pkl'

        if self.path.exists():
            if clear:
                print('Clearing cache!')
                self.clear()
            else:
                self._load_index()

    def _dump_index(self):
        with open(self.index_file, 'wb') as file:
            pickle.dump(self, file)

    def _load_index(self):
        if not self.index_file.exists():
            self._dump_index()
            return
        with open(self.index_file, 'rb') as file:
            self.update(pickle.load(file))

    def add(self, key, object,  exist_ok=False):
        if not self.path: return
        assert type(key)==str, f'Expect key to be a string, got {key}'
        if key  in self:
            if not exist_ok:
                print(f'Warning: cached object for key "{key}" exists', file=sys.stderr)
            filename = self[key]
        else:
            filename = self.path/f'cache_file_{hex(key.__hash__())[3:]}.pkl'
            self[key] = filename
            self._dump_index()

        with open(filename, 'wb') as file:
            pickle.dump(object, file )


    def get(self, key):
        if key not in self:
            return None
        filename = self[key]
        if not filename.exists():
            # perhaps deleted by another instance?
            print(f'File for Cache key {key} not found, removing entry', file='sys.stderr')
            selt.pop(key)
            return None
        with open(filename, 'rb') as file:
            ret = pickle.load(file)
        return ret

    def clear(self):
        if not self.path: return
        for f in self.path.iterdir():
            if f.is_file:
                f.unlink()
        super().clear()

        self._dump_index()

    def remove(self, key):
        """remove entry and associated file"""
        if not self.path: return
        if key not in self:
            print(f'Cache: key {key} not found', file=sys.stderr)
            return
        filename = self[key]
        try:
            filename.unlink()
        except:
            print(f'Failed to unlink file {filename}')
        super().pop(key)
        self._dump_index()


    def __call__(self, key, func, *pars, description='', overwrite=False, **kwargs,
                ):
        """
        One-line usage interface for cache use

        - `key` -- key to use, usually a string. Must be hashable <br>
            If None, ignore cache and return the function evaluation
        - `func` -- user function that will return an object that can be pickled
        - `pars`, `kwargs` -- pass to `func`
        - `description` -- optional string that will be printed
        - `overwrite` -- if set, overwrite previous entry if exists

        Example:
        <pre>
        mycache = Cache('/tmp/thecache', clear=True)

        def myfun(x):
            return x

        result = mycache('mykey', myfun, x=99,  description='My data')

        </pre>

        """

        if key is None or self.path is None:
            return func(*pars, **kwargs)


        if description:
            print(f'{description}: {"Saving to" if key not in self or overwrite else "Restoring from"} cache', end='')
            print('' if key == description else f' with key "{key}"')
        ret = self.get(key)
        if ret is None or overwrite:
            ret = func(*pars, **kwargs)
            self.add(key, ret, exist_ok=overwrite)
        return ret

    def show(self, starts_with=''):
        import datetime
        if not self.path: return 'Cache not enabled'
        if len(self.items())==0: return f'Cache at {self.path} is empty\n'
        title = 'Cache contents' if not starts_with else f'Cache entries starting with {starts_with}'
        s = f'{title}\n {"key":30}   {"size":>10}  {"time":20} {"name"}, folder {self.path}\n'
        for name, value in self.items():
            if name is None or not name.startswith(starts_with) : continue
            try:
                stat = value.stat()
                size = stat.st_size
                mtime= str(datetime.datetime.fromtimestamp(stat.st_mtime))[:16]
                s += f'  {name:30s}  {size:10}  {mtime:20} {value.name}\n'
            except Exception as msg:
                s += f'{name} -- file not found\n'
        return s

    def __str__(self):
        return self.show()

# Cell
class Config():
    defaults=\
    """
        verbose         : 1 # set to zero for no output
        usermode        : true # default suppress warnings

        datapath        : None # where to find data--must be set
        cachepath       : ~/.cache/wtlike #

        # Expect 4FGL FITS file, e.g.,  gll_psc_v28.fit
        catalog_file    :

        # data cuts, processing
        radius          : 4
        cos_theta_max   : 0.4
        z_max           : 100
        offset_size     : 2.e-06  # scale factor used for event time

        # binning -- actually determined by weight run
        energy_edge_pars : [2,6,17] # pars for np.logspace
        etypes          : [0, 1] # front, back
        nside           : 1024
        nest            : True

        # data selection for cell creation
        week_range      : []  # default all weeks found
        time_bins       : [0, 0, 7] # full MJD range, 7-day cells
        exp_min         : 5    # threshold for exposure per cell, in cm^2 Ms units.

        # cell fitting
        use_kerr        : False
        likelihood_rep  : poisson
        poisson_tolerance : 0.2

    """




    def __init__(self, **kwargs):
        import yaml
        from yaml import SafeLoader

        # parameters: first defaults, then from ~/.config/wtlike/config.yaml, then kwars
        pars = yaml.load(self.defaults, Loader=SafeLoader)
        dp = Path('~/.config/wtlike/config.yaml').expanduser()
        if dp.is_file():
            userpars = yaml.load(open(dp,'r'), Loader=SafeLoader)
            pars.update(userpars)
            #print(f'update from user file {dp}: {userpars}')
        pars.update(kwargs)

        self.__dict__.update(pars)

        # suppress warnings unless testing or in usermode
        if self.usermode:
            if not sys.warnoptions:
                import warnings
                warnings.simplefilter("ignore")

        self.energy_edges = ee=np.logspace(*self.energy_edge_pars)
        self.energy_bins = np.sqrt(ee[1:] * ee[:-1])
        if not self.week_range:
            self.week_range = (None, None)

       # set up, check files paths
        self.error_msg=''
        if self.datapath is None:
            self.error_msg+='\ndatapath must be a folder with wtlike data'
        else:
            self.datapath = df = Path(self.datapath).expanduser()
            if not (self.datapath.is_dir() or  self.datapath.is_symlink()):
                self.error_msg+=f'\ndata_folder "{df}" is not a directory or symlink'
            subs = 'aeff_files weight_files data_files'.split()
            for sub in subs:
                if not ( (df/sub).is_dir() or  (df/sub).is_symlink()) :
                    self.error_msg+=f'\n{df/sub} is not a directory or symlink'

        self.cachepath =  Path(self.cachepath).expanduser()
        os.makedirs(self.cachepath, exist_ok=True)
        if not self.cachepath.is_dir():
            self.error_msg +=f'cachepath {self.cachepath} is not a folder.'

    @property
    def cache(self):
        if not hasattr(self, '_cache'):
            self._cache = Cache(self.cachepath, clear=False)
        return self._cache

    @property
    def valid(self):
        if len(self.error_msg)==0: return True
        print(f'wtlike configuration is invalid:\n{self.error_msg}',file=sys.stderr)
        return False

    def __str__(self):
        s = 'Configuration parameters \n'
        for name, value in self.__dict__.items():
            if name=='files' or name.startswith('_'): continue
            s += f'  {name:15s} : {value}\n'
        return s

    def __repr__(self): return str(self)
    def get(self, *pars): return self.__dict__.get(*pars)



# Cell

day = 24*3600.
first_data=54683
#mission_start = Time('2001-01-01T00:00:00', scale='utc').mjd
# From a FT2 file header
# MJDREFI =               51910. / Integer part of MJD corresponding to SC clock S
# MJDREFF =  0.00074287037037037 / Fractional part of MJD corresponding to SC cloc
mission_start = 51910.00074287037

def MJD(arg):

    if type(arg)==str:
        while len(arg.split('-'))<3:
            arg+='-1'
        return Time(arg, format='iso').mjd

    "convert MET or UTC to MJD"
    return (mission_start + arg/day  )

def UTC(mjd):
    " convert MJD value to ISO date string"
    t=Time(mjd, format='mjd')
    t.format='iso'; t.out_subfmt='date_hm'
    return t.value

def UTCnow():
    from datetime import datetime
    t=datetime.utcnow()
    return f'UTC {t.year}-{t.month:02d}-{t.day} {t.hour:02d}:{t.minute:02d}'


# Cell
def bin_size_name(bins):
    """Provide a nice name, e.g., 'day' for a time interval
    """
    if np.isscalar(bins) :
        binsize = bins
    else:
        binsize = np.mean(bins)

    def check_unit(x):
        unit_table = dict(week=1/7, day=1, hour=24, min=24*60, s=24*3600)
        for name, unit in unit_table.items():
            t = x*unit
            r = np.mod(t+1e-9,1)
            if r<1e-6 or t>1:
                return t, name
        return x, 'day'
    n, unit =  check_unit(binsize)
    nt = f'{n:.0f}' if np.mod(n,1)<1e-2 else f'{n:.0f}'
    return f'{nt}-{unit}'# if n>1 else f'{unit}'

# Cell
def decorate_with(other_func):
    def decorator(func):
        func.__doc__ += other_func.__doc__
        return func
    return decorator

# Cell
def df_4fgl():
    """Return a DataFrame with a summary of the 4FGL-DR3 catalog
    """

    from pathlib import Path
    from astropy.io import fits
    from astropy.coordinates import SkyCoord
    import pandas as pd

    catfile = Path(Config().catalog_file).expanduser()
    if not catfile.exists(): return

    with fits.open(catfile) as hdu:
        cat = hdu[1].data

    # return columns: strip the names, convert floats to little endian
    cname = lambda n : [s.strip() for s in cat[n]]
    cvar = lambda a: cat[a].astype(float)
    # use this to get (ra,dec) and (l,b) pairs
    skycoord = SkyCoord(cvar('RAJ2000'), cvar('DEJ2000'), unit='deg', frame='fk5')

    catdf = pd.DataFrame(dict(

        fk5 = zip( (skycoord.ra.deg).round(3),
                   (skycoord.dec.deg).round(3)),
        gal = zip( (skycoord.galactic.l.deg).round(3),
                   (skycoord.galactic.b.deg).round(3)),
        significance = cvar('Signif_Avg'),
        variability = cvar('Variability_Index'),
        assoc_prob = cvar('ASSOC_PROB_BAY'),
        assoc_name = cname('ASSOC1'),

        ))
    catdf.index = cname('Source_Name')
    catdf.index.name='name'
    return catdf