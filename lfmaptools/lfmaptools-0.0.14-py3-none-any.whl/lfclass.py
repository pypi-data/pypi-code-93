
import sys
import os
import glob
import itertools
import warnings
import numpy as np
from shapely import wkt
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon, LineString, MultiLineString, LinearRing, mapping
from shapely.ops import transform, linemerge, unary_union, polygonize
from shapely.affinity import translate
import pandas as pd
import geopandas as gpd
import rasterio as rio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import get_data_window
import xarray as xa
import rioxarray as rxa
import pyproj as Proj
from functools import partial
import contextily as ctx
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.legend as mlegend
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
from matplotlib.textpath import TextToPath
from matplotlib.font_manager import FontProperties
from mpl_toolkits.axes_grid1 import make_axes_locatable
import webbrowser

from skimage.measure import find_contours
from scipy.interpolate import interp1d
import jenkspy

import zipfile
import tarfile
import utm
import numbers
import osmnx as osm
import folium

from lfmaptools.utilities import (_nice_round, 
                                  _represents_int, 
                                  latlon_to_utm_epsg,
                                  _path_of_file_in_zip,
                                  csv_active_cols,
                                  csv_num_cols)
from lfmaptools.geotools import LatLon_TM_polygonize
from lfmaptools.epsg_defs import webmerc, wgs84
from lfmaptools.mapping import add_stamen_basemap

_LFoutput_fmt = [
    {'file': 'all', 'column': 0, 'short_name': 'tile', 'long_name': 'tile id', 'symbol': None, 'units': 'dimensionless', 'dtype': int, 'infile': True, },
    {'file': 'all', 'column': 1, 'short_name': 'x_distance', 'long_name': 'Easting distance from origin at the domain centre', 'symbol': 'x', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'all', 'column': 2, 'short_name': 'y_distance', 'long_name': 'Northing distance from origin at the domain centre', 'symbol': 'y', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'all', 'column': 3, 'short_name': 'latitude', 'long_name': 'Latitude in WGS84 coordinates', 'symbol': 'lat', 'units': 'decimal degrees', 'dtype': 'real', 'infile': True, },
    {'file': 'all', 'column': 4, 'short_name': 'longitude', 'long_name': 'Longitude in WGS84 coordinates', 'symbol': 'lon', 'units': 'decimal degrees', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 5, 'short_name': 'flow_depth', 'long_name': 'Depth of lahar', 'symbol': 'h', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 6, 'short_name': 'flow_speed', 'long_name': 'Speed of lahar', 'symbol': '√(u^2+v^2)', 'units': 'm/s', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 7, 'short_name': 'mass_per_unit_area', 'long_name': 'Mass of lahar per unit area', 'symbol': 'ρh', 'units': 'kg/m^2', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 8, 'short_name': 'x_flux', 'long_name': 'Mass flux in the easting per unit length', 'symbol': 'ρhu', 'units': 'kg/m/s', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 9, 'short_name': 'y_flux', 'long_name': 'Mass flux in the northing per unit length', 'symbol': 'ρhv', 'units': 'kg/m/s', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 10, 'short_name': 'mass_of_solids', 'long_name': 'Mass of solids per unit area', 'symbol': 'ρhc', 'units': 'kg/m^2', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 11, 'short_name': 'base_elevation', 'long_name': 'Base topographic elevation', 'symbol': 'b0', 'units': 'm (a.s.l.)', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 12, 'short_name': 'base_x_slope', 'long_name': 'Slope of base topography in Easting', 'symbol': '∂b0/∂x', 'units': 'dimensionless', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 13, 'short_name': 'base_y_slope', 'long_name': 'Slope of base topography in Northing', 'symbol': '∂b0/∂y', 'units': 'dimensionless', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 14, 'short_name': 'elevation_change', 'long_name': 'Change in topographic elevation', 'symbol': 'bt', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 15, 'short_name': 'change_in_x_slope', 'long_name': 'Change in x-slope of topography', 'symbol': '∂bt/∂x', 'units': 'dimensionless', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 16, 'short_name': 'change_in_y_slope', 'long_name': 'Change in y-slope of topography', 'symbol': '∂bt/∂y', 'units': 'dimensionless', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 17, 'short_name': 'land_use', 'long_name': 'Land use category', 'symbol': ' ', 'units': 'dimensionless', 'dtype': 'int', 'infile': True, },
    {'file': 'snapshot', 'column': None, 'short_name': 'concentration', 'long_name': 'Solid mass concentration', 'symbol': 'c', 'units': 'dimensionless', 'dtype': 'real', 'infile': False, },
    {'file': 'MaxHeights.txt', 'column': 5, 'short_name': 'maximum_depth', 'long_name': 'Maximum depth of lahar', 'symbol': 'maxh', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'MaxHeights.txt', 'column': 6, 'short_name': 'time_of_maximum', 'long_name': 'Time of the maximum depth', 'symbol': 't_maxh', 'units': 's', 'dtype': 'real', 'infile': True, },
    {'file': 'MaxSpeeds.txt', 'column': 5, 'short_name': 'maximum_speed', 'long_name': 'Maximum speed of lahar', 'symbol': 'maxspd', 'units': 'm/s', 'dtype': 'real', 'infile': True, },
    {'file': 'MaxSpeeds.txt', 'column': 6, 'short_name': 'time_of_maximum', 'long_name': 'Time of the maximum speed', 'symbol': 't_maxspd', 'units': 's', 'dtype': 'real', 'infile': True, },
    {'file': 'InundationTime.txt', 'column': 5, 'short_name': 'inundation_time', 'long_name': 'Time of first inundation', 'symbol': 't_inun', 'units': 's', 'dtype': 'real', 'infile': True, },
]
_LFoutput_shortnames = [d['short_name'] for d in _LFoutput_fmt]
def _get_LF_output_fmt(short_name, filetype='snapshot'):
    try:
        ret = next(item for item in _LFoutput_fmt if item['short_name'] == short_name and item['file'] in [filetype, 'all'])
    except:
        warnings.warn('Item {} not in known output formats for filetype {}'.format(short_name, filetype))
        ret = {'file': 'unknown', 'short_name': short_name, 'long_name': short_name.replace('_', ' '), 'symbol': '', 'units': '', 'dtype': '', 'infile': True, }
    return ret

class LaharFlowData(object):
    def __init__(self,LaharFlowDir,zipped=False):

        if zipped:
            self.zipped = True
            if not os.path.exists(LaharFlowDir+'.zip'):
                print('File {} does not exist'.format(LaharFlowDir+'.zip'))
                self.dir = None
                return
            else:
                self.dir = LaharFlowDir
                self._zipref = zipfile.ZipFile(LaharFlowDir+'.zip',"r")
        else:
            self.zipped = False
            if not os.path.exists(LaharFlowDir):
                print('Directory {} does not exist'.format(LaharFlowDir))
                self.dir = None
                return
            else:
                self.dir = LaharFlowDir
            
        if zipped:
            infoFilePath = _path_of_file_in_zip('RunInfo.txt',self._zipref)[0]
            infoFile = self._zipref.extract(infoFilePath,path=self.dir)
        else:
            infoFile = os.path.join(LaharFlowDir,"RunInfo.txt")
            assert(os.path.isfile(infoFile)), 'Run info file {} does not exist'.format(infoFile)
        self.infoFile = infoFile

        with open(infoFile) as f:
            for ln, line in enumerate(f):
                if "Input file name" in line:
                    self.inputFile = (line.split(':',1)[1]).strip(' \t\n\r')
                if "Latitude of domain centre" in line:
                    self.clat = float(line.split('=',1)[1])
                if "Longitude of domain centre" in line:
                    self.clong = float(line.split('=',1)[1])
                if "Time step between outputs" in line:
                    self.dtout = float(line.split('=',1)[1])
                if "height threshold" in line:
                    self.hthres = float(line.split('=',1)[1])
                if "nTiles" in line:
                    self.nTiles = float(line.split('=',1)[1])
                if "nXtiles" in line:
                    self.nXtiles = float(line.split('=',1)[1])
                if "nYtiles" in line:
                    self.nYtiles = float(line.split('=',1)[1])
                if "nXpertile" in line:
                    self.nXpertile = float(line.split('=',1)[1])
                if "nYpertile" in line:
                    self.nYpertile = float(line.split('=',1)[1])
                if "Xtilesize" in line:
                    self.Xtilesize = float(line.split('=',1)[1])
                if "Ytilesize" in line:
                    self.Ytilesize = float(line.split('=',1)[1])
                if "xSize" in line:
                    self.xSize = float(line.split('=',1)[1])
                if "ySize" in line:
                    self.ySize = float(line.split('=',1)[1])
                if "nXPoints" in line:
                    self.nX = int(line.split('=',1)[1])
                if "nYPoints" in line:
                    self.nY = int(line.split('=',1)[1])
                if "deltaX" in line:
                    self.dX = float(line.split('=',1)[1])
                if "deltaY" in line:
                    self.dY = float(line.split('=',1)[1])
                if "Number of output files" in line:
                    self.Nout = int(line.split('=',1)[1])
                if "Last output file" in line:
                    self.lastOut = int(line.split('=',1)[1])
                if "end time" in line:
                    self.endTime = float(line.split('=',1)[1])
                if "Time step between outputs" in line:
                    self.dT = float(line.split('=',1)[1])
                if "rhow" in line:
                    self.rhow = float(line.split('=',1)[1])
                if "rhos" in line:
                    self.rhos = float(line.split('=',1)[1])
                if "Erosion depth" in line:
                    self.Edepth = float(line.split('=',1)[1])
                if "Topography type" in line:
                    TopoType = line.split('=',1)[1]
                    self.TopoType = TopoType.strip(' \t\n\r')
                if "Topography path" in line:
                    self.TopoPath = line.split('=',1)[1].strip(' \t\n\r')
                if "Raster path" in line:
                    self.RasterPath = line.split('=',1)[1].strip(' \t\n\r')
                if "Raster file" in line:
                    self.RasterFile = line.split('=',1)[1].strip(' \t\n\r')
                if "SRTM path" in line:
                    self.SRTMPath = line.split('=',1)[1].strip(' \t\n\r')
                if "SRTM files" in line:
                    fileList=line.split('=',1)[1]
                    fileList=fileList.strip("\n")
                    fileList=fileList.strip()
                    SRTMFiles = fileList.split(",")
                    self.SRTMFiles = list(filter(None, SRTMFiles))
                if "SRTM virtual file" in line:
                    self.SRTMvrt = line.split('=',1)[1].strip(' \t\n\r')
                if "Embedded raster" in line:
                    if (line.split('=',1)[1].strip()=='on'):
                        self.embed = True
                    else:
                        self.embed = False
                if "Land use path" in line:
                    self.LandUsePath = line.split('=',1)[1].strip(' \t\n\r')
                if "Land use file" in line:
                    self.LandUseFile = line.split('=',1)[1].strip(' \t\n\r')
                # if "Number of flux sources" in line:
                # 	self.num_flux = int(line.split('=',1)[1])
                # 	src_count = 0
                # 	while src_count<self.num_flux:
                # 		for k in range(0,10):
                # 			next(f,None)
                # 			print(ln,' ',line)
                # 		src_count+=1
                    
            self.files=[]
            self.txt_files=[]
            self.tar_files=[]
            
            self.get_files()
            self.get_txt_files()
            self.get_tar_files()
            self.get_tiff_files()

            self.clatlong = [self.clat,self.clong]

            self.utm = utm.from_latlon(self.clat,self.clong)
            self.utmCode = latlon_to_utm_epsg(self.clat, self.clong)
            self.utmZone = utm.latlon_to_zone_number(self.clat,self.clong)

            if self.inputFile in self.files:
                self._get_parameters_from_inputfile()
            else:
                self._get_parameters_from_runinfo()
            self._get_max_depth()
            self._get_max_speed()
    
    def _get_parameters_from_inputfile(self):
        if self.zipped:
            inputFilePath = _path_of_file_in_zip(self.inputFile,self._zipref)[0]
            inputFile = self._zipref.extract(inputFilePath,path=self.dir)
        else:
            inputFile = os.path.join(self.dir,os.path.split(self.inputFile)[1])
            if not os.path.isfile(inputFile):
                print('Input file {} does not exist'.format(inputFile))
                return
        parameters = []
        with open(inputFile) as f:
            for line in f:
                try:
                    keyword,value = line.split('=',2)
                    keyword = keyword.rstrip()
                    value = value.rstrip()
                    if keyword=="Drag":
                        self.Drag = value
                        parameters.append('Drag')
                    if keyword=="Chezy co":
                        self.Chezy_co = float(value)
                        parameters.append('Chezy_co')
                    if keyword=="Pouliquen min":
                        self.Pouliquen_min = float(value)
                        parameters.append('Pouliquen_min')
                    if keyword=="Pouliquen max":
                        self.Pouliquen_max = float(value)
                        parameters.append('Pouliquen_max')
                    if keyword=="Pouliquen delta":
                        self.Pouliquen_delta = float(value)
                        parameters.append('Pouliquen_delta')
                    if keyword=="Pouliquen beta":
                        self.Pouliquen_beta = float(value)
                        parameters.append('Pouliquen_beta')
                    if keyword=="Pouliquen L on d":
                        self.Pouliquen_L_on_d = float(value)
                        parameters.append('Pouliquen_L_on_d')
                    if keyword=="Erosion Rate":
                        self.ErosionRate = float(value)
                        parameters.append('ErosionRate')
                    if keyword=="Granular Erosion Rate":
                        self.GranularErosionRate = float(value)
                        parameters.append('GranularErosionRate')
                    if keyword=="Erosion depth":
                        self.ErosionDepth = float(value)
                        parameters.append('ErosionDepth')
                    if keyword=="Erosion critical Eond":
                        self.ErosionCritical_E_on_d = float(value)
                        parameters.append('ErosionCritical_E_on_d')
                    if keyword=="Voellmy switch rate":
                        self.Voellmy_switch_rate = float(value)
                        parameters.append('Voellmy_switch_rate')
                    if keyword=="VoellmySwitch on maxPack":
                        self.VoellmySwitch_on_maxPack = float(value)
                        parameters.append('VoellmySwitch_on_maxPack')
                    if keyword=="Bed porosity":
                        self.Bed_porosity = float(value)
                        parameters.append('Bed_porosity')
                    if keyword=="Voellmy switch value":
                        self.Voellmy_switch_value = float(value)
                        parameters.append('Voellmy_switch_value')
                    if keyword=="maxPack":
                        self.maxPack = float(value)
                        parameters.append('maxPack')
                    if keyword=="rhow":
                        self.rhow = float(value)
                        parameters.append('rhow')
                    if keyword=="rhos":
                        self.rhos = float(value)
                        parameters.append('rhos')
                    if keyword=="Erosion critical height":
                        self.Erosion_critical_height = float(value)
                        parameters.append('Erosion_critical_height')
                    if keyword=="Pouliquen L":
                        self.Pouliquen_L = float(value)
                        parameters.append('Pouliquen_L')
                    if keyword=="Solid diameter":
                        self.Solid_diameter = float(value)
                        parameters.append('Solid_diameter')
                except:
                    pass
        self.parameters = parameters

    def _get_parameters_from_runinfo(self):
        parameters = []
        with open(self.infoFile) as f:
            for line in f:
                delim = '=' if '=' in line else ':'
                try:
                    keyword,value = line.split(delim,1)
                    keyword = keyword.rstrip()
                    value = value.rstrip()
                    if keyword=="Drag":
                        self.Drag = value
                        parameters.append('Drag')
                    if keyword=="Chezy coefficient":
                        self.Chezy_co = float(value)
                        parameters.append('Chezy_co')
                    if keyword=="Pouliquen Min Slope":
                        self.Pouliquen_min = float(value)
                        parameters.append('Pouliquen_min')
                    if keyword=="Pouliquen Max Slope":
                        self.Pouliquen_max = float(value)
                        parameters.append('Pouliquen_max')
                    if keyword=="Erosion rate":
                        self.ErosionRate = float(value)
                        parameters.append('ErosionRate')
                    if keyword=="Erosion depth":
                        self.ErosionDepth = float(value)
                        parameters.append('ErosionDepth')
                    if keyword=="Voellmy switch rate":
                        self.Voellmy_switch_rate = float(value)
                        parameters.append('Voellmy_switch_rate')
                    if keyword=="Bed porosity":
                        self.Bed_porosity = float(value)
                        parameters.append('Bed_porosity')
                    if keyword=="Voellmy switch value":
                        self.Voellmy_switch_value = float(value)
                        parameters.append('Voellmy_switch_value')
                    if keyword=="Maximum packing fraction":
                        self.maxPack = float(value)
                        parameters.append('maxPack')
                    if keyword=="rhow":
                        self.rhow = float(value)
                        parameters.append('rhow')
                    if keyword=="rhos":
                        self.rhos = float(value)
                        parameters.append('rhos')
                    if keyword=="Erosion critical height":
                        self.Erosion_critical_height = float(value)
                        parameters.append('Erosion_critical_height')
                    if keyword=="Solid diameter":
                        self.Solid_diameter = float(value)
                        parameters.append('Solid_diameter')
                    if keyword=="Erosion":
                        self.Erosion = value
                        parameters.append('Erosion')
                except:
                    pass
                    
        self.parameters = parameters

    def get_XY(self):
        
        x = ((np.arange(0,self.xSize,self.dX)-self.xSize/2)+self.dX/2)
        y = ((np.arange(0,self.ySize,self.dY)-self.ySize/2)+self.dY/2)
        
        return x, y
    
    def get_files(self):
        if self.zipped:
            files = self._zipref.namelist()
            self.files = [os.path.split(f)[1] for f in files]
        else:
            self.files = os.listdir(self.dir)
    
    def get_tar_files(self):
        self.tar_files = [f for f in self.files if f.endswith('.tar.gz')]
        self.tar_files.sort()

    def get_txt_files(self):
        self.txt_files = [f for f in self.files if f.endswith('.txt')]
        self.txt_files.sort()
    
    def get_snapshot_files(self):
        sfiles = [f for f in self.txt_files if f.strip('.txt').isnumeric()]
        sfiles.sort()
        return sfiles

    def get_tiff_files(self):
        self.tiffFiles = {}
        k=0
        for f in self.files:
            if f.endswith('.tif'):
                raster = rio.open(os.path.join(self.dir,f))
                epsg = raster.crs.to_epsg()
                raster.close()
                this_file = {'file': f,'epsg':epsg,'index':k}
                self.tiffFiles[str(f)] = this_file
                k+=1
        return
    
    def _update_tiff_files(self,file,epsg=None):
        assert(file.endswith('tif')), 'In updateTiff, file must have a .tif extension; received {}'.format(file)
        
        n = len(self.tiffFiles)
        if epsg is None:
            with rio.open(os.path.join(self.dir,file)) as src:
                epsg = src.crs.to_epsg()
        self.tiffFiles[file] = {'file':file,'epsg':epsg,'index':n}
        return

    def _valid_input_file(self, fileIn):
        if isinstance(fileIn, str):
            if fileIn not in self.files:
                raise ValueError('Result file {file} is not in directory {dir}'.format(file=fileIn, dir=self.dir))
        elif isinstance(fileIn, int):
            if '{0:06d}.txt'.format(fileIn) in self.files:
                fileIn = '{0:06d}.txt'.format(fileIn)
            elif '{0:06d}.txt.tar.gz'.format(fileIn) in self.files:
                fileIn = '{0:06d}.txt.tar.gz'.format(fileIn)
            else:
                raise ValueError('Result file {file} is not in directory {dir}'.format(file=fileIn, dir=self.dir))
        else:
            raise RuntimeError("Result must be either the name of file in directory {dirc}, or an integer".format(dirc=self.dir))
        return fileIn
    
    def _file_type(self, filename):
        _ = self._valid_input_file(filename)
        if isinstance(filename, str):
            if filename=='MaxHeights.txt':
                filetype = 'MaxHeights.txt'
            elif filename=='MaxSpeeds.txt':
                filetype = 'MaxSpeeds.txt'
            else:
                filetype = 'snapshot'
        elif isinstance(filename, int):
            filetype = 'snapshot'
        
        return filetype

    def _valid_variable(self, variable):
        if variable not in _LFoutput_shortnames:
            raise RuntimeError('variable {var} not recognized'.format(var=variable))

    def _extract_file(self, filename):
        if self.zipped:
            LaharFlowFilePath = _path_of_file_in_zip(filename, self._zipref)[0]
            LaharFlowFile = self._zipref.extract(LaharFlowFilePath, path=self.dir)
            ExtractPath = os.path.join(self.dir, os.path.split(LaharFlowFilePath)[0])
        elif filename in self.txt_files:
            LaharFlowFile = os.path.join(self.dir, filename)
            ExtractPath = self.dir
        
        if (os.path.split(LaharFlowFile)[1] in self.tar_files) and (os.path.split(LaharFlowFile)[1] not in self.txt_files):
            tar = tarfile.open(LaharFlowFile, mode='r')
            tar.extractall(path=ExtractPath)
            tar.close()
            self.get_txt_files()
            LaharFlowFile = '.'.join(LaharFlowFile.split('.')[:-2])
        return LaharFlowFile

    def _get_data_column_names(self, filename):
        filename = self._valid_input_file(filename)
        LaharFlowFile = self._extract_file(filename)
        
        cols = csv_active_cols(LaharFlowFile)
        return cols

    def _get_data(self, filename):

        filename = self._valid_input_file(filename)

        LaharFlowFile = self._extract_file(filename)
        
        try:
            cols = csv_active_cols(LaharFlowFile)
            data = np.genfromtxt(LaharFlowFile, delimiter=',', names=True, usecols=cols)
            return data
        except:
            return None
    
    def raster(self, filename, full_domain=False, nodata=np.nan, masked=True, crs=None):
        filetype = self._file_type(filename)
        
        filename = self._valid_input_file(filename)
        
        LaharFlowFile = self._extract_file(filename)
        
        cols = csv_active_cols(LaharFlowFile)
        data = np.genfromtxt(LaharFlowFile, delimiter=',', names=True, usecols=cols)
        
        extra_cols = ['tile', 'x_distance', 'y_distance', 'latitude', 'longitude']
        data_cols = [x for x in data.dtype.names 
                        if x not in extra_cols]
        
        x = data['x_distance']
        y = data['y_distance']

        ux = np.unique(x)
        uy = np.unique(y)
        Nux = len(ux)
        Nuy = len(uy)
        if full_domain:
            x0, y0= self.get_XY()
            array = nodata*np.ones((self.nY,self.nX,len(data_cols)))
        else:
            x0 = ux
            y0 = uy
            array = nodata*np.ones((Nuy,Nux,len(data_cols)))

        for k in range(0,len(x)):
            xk = x[k]
            yk = y[k]
            ii = np.where(yk==y0)
            jj = np.where(xk==x0)
            for d, col in enumerate(data_cols):
                array[ii,jj,d] = data[col][k]
        
        if masked:
            array = np.ma.masked_where(array==nodata, array)
        
        ds = xa.Dataset()
        ds.coords["x"] = x0 + self.utm[0]
        ds.coords["y"] = y0 + self.utm[1]
        for d, col in enumerate(data_cols):
            ds[col] = (("y","x"), array[:,:,d])
            ds[col].rio.write_nodata(nodata, inplace=True)
            fmt = _get_LF_output_fmt(col, filetype=filetype)
            ds[col].attrs["short_name"] = fmt['short_name']
            ds[col].attrs["long_name"] = fmt['long_name']
            ds[col].attrs["units"] = fmt['units']
            ds[col].attrs["symbol"] = fmt['symbol']
        
        if filetype=='snapshot':
            ds['concentration'] = ds['mass_of_solids']
            ds['concentration'] = np.divide(ds['mass_of_solids'], ds['mass_per_unit_area'], where=ds['mass_per_unit_area'].where(ds['mass_per_unit_area'].data>1e-8))
            fmt = _get_LF_output_fmt('concentration')
            ds['concentration'].attrs["short_name"] = fmt['short_name']
            ds['concentration'].attrs["long_name"] = fmt['long_name']
            ds['concentration'].attrs["units"] = fmt['units']
            ds['concentration'].attrs["symbol"] = fmt['symbol']

        ds.x.attrs["units"] = "metres"
        ds.y.attrs["units"] = "metres"
        
        ds = ds.rio.write_crs(self.utmCode)

        if crs is not None:
            ds = ds.rio.reproject(crs)
        
        return ds

    def _raster_flatten(raster):
        rflat = raster.data.flatten()
        return rflat[~np.isnan(rflat)]

    def _get_data_column(self, filename, data_col):

        dataFile = self._extract_file(filename)

        try:
            data = np.genfromtxt(dataFile,delimiter=',',comments='%',skip_header=1)
            x = data[:,1]
            y = data[:,2]
            d = data[:,data_col]
            return x, y, d
        except:
            return None, None, None
    
    def _data_to_array(self, x, y, data,
                       nodata=-1.0,
                       masked=True,
                       vmin=None,
                       full_domain=True):
        ux = np.unique(x)
        uy = np.unique(y)
        Nux = len(ux)
        Nuy = len(uy)
        if full_domain:
            x0, y0= self.get_XY()
            array = nodata*np.ones((self.nY,self.nX))
        else:
            x0 = ux
            y0 = uy
            array = nodata*np.ones((self.Nuy,self.Nux))
        
        for k in range(0,len(x)):
            xk = x[k]
            yk = y[k]
            ii = np.where(yk==y0)
            jj = np.where(xk==x0)
            if (vmin is None) or (data[k]>vmin):
                array[ii,jj] = data[k]
        
        if masked:
            array = np.ma.masked_where(array==nodata,array)
        return array

    def _get_max_bed_evolution(self):
        last_outfile = self.get_snapshot_files()[-1]
        
        dataFile = self._extract_file(last_outfile)

        if not os.path.isfile(dataFile):
            MaxErosion = np.nan
            MaxDeposit = np.nan
        else:
            x, y, bt = self._get_data_column(dataFile, 14)
            
            MaxErosion = max(-np.amin(bt),0.0)
            MaxDeposit = max(np.amax(bt),0.0)

        self.MaxErosion = MaxErosion
        self.MaxDeposit = MaxDeposit

        return {'MaxErosion': MaxErosion, 'MaxDeposit': MaxDeposit}
    
    def max_bed_evolution(self, vmin=None, vmax=None):
        last_outfile = self.get_snapshot_files()[-1]
        data = self.raster(last_outfile)
        bt = data['elevation_change']
        
        if vmin is not None:
            bt = bt.where(bt.data>vmin)
        
        if vmax is not None:
            bt = bt.where(bt.data<vmax)
        
        return bt

    def _get_max_depth(self):
        
        _, _, h = self._get_data_column('MaxHeights.txt', 5)
        
        self.MaxDepth = np.amax(h)
    
    def max_depth(self, vmin=None):

        data = self.raster('MaxHeights.txt')
        maxh = data['maximum_depth']

        if vmin is not None:
            maxh = maxh.where(maxh.data>vmin)

        return maxh

    def _get_max_speed(self):
        
        _, _, spd = self._get_data_column('MaxSpeeds.txt', 5)
        
        self.MaxSpeed = np.amax(spd)
        
    def max_speed(self, vmin=None):

        data = self.raster('MaxSpeeds.txt')
        maxspd = data['maximum_speed']

        if vmin is not None:
            maxspd = maxspd.where(maxspd.data>vmin)

        return maxspd
    
    def inundation_time(self, vmin=None):

        data = self.raster('InundationTime.txt')
        itime = data['inundation_time']

        if vmin is not None:
            itime = itime.where(itime.data>vmin)
        
        return itime

    def _get_max_deposit(self):

        last_outfile = self.get_snapshot_files()[-1]
        _, _, bt = self._get_data_column(last_outfile, 14)
        
        self.MaxDeposit = max(np.amax(bt),0.0)

    def _get_max_erosion(self):
        
        last_outfile = self.get_snapshot_files()[-1]
        _, _, bt = self._get_data_column(last_outfile, 14)
        
        self.MaxErosion = max(-np.amin(bt),0.0)

    def snapshot_data(self,fnum):
        assert isinstance(fnum,int), 'in getSnapshotData, input must be an integer'
        fnum = '{0:06d}.txt'.format(fnum)
        assert( any([c in self.files for c in ('{0:06d}.txt'.format(fnum), '{0:06d}.txt.tar.gz'.format(fnum))] )), 'Results file {file} is not in directory {dir}'.format(file=fnum,dir=self.dir)

        LaharFlowFile = self._extract_file(fnum)

        cols = csv_active_cols(LaharFlowFile)
        data = np.genfromtxt(LaharFlowFile,delimiter=',',names=True,usecols=cols)
        return data
    
    def snapshot_variable(self, fnum, var, vmin=None, full_domain=False):
        
        dataset = self.raster(fnum, full_domain=full_domain)

        valid_vars = _LFoutput_shortnames

        if var not in valid_vars:
            raise ValueError("variable name must be one of {names}, received '{var}'".format(names=valid_vars, var=var))
        
        dat = dataset[var]

        if vmin is not None:
            dat = dat.where(dat.data>vmin)

        return dat
        
    def _raster_contour(self, raster, name, cntrs):

        data = raster.data
        x = raster.x.data
        y = raster.y.data

        x0, y0 = self.get_XY()
        x0 += self.utm[0]
        y0 += self.utm[1]
        
        fx = interp1d(np.arange(0,len(x0)),x0)
        fy = interp1d(np.arange(0,len(y0)),y0)

        # fx = interp1d(np.arange(0,len(x)),x)
        # fy = interp1d(np.arange(0,len(y)),y)

        for kk, this_cntr in enumerate(cntrs):
            
            C = find_contours(data, this_cntr)
            
            if len(C)==0:
                pass
            for jj, p in enumerate(C):
                p[:,0] = fy(p[:, 0])
                p[:,1] = fx(p[:, 1])
                
                p[:, [0, 1]] = p[:, [1, 0]]
                
                thisPoly = Polygon(p).buffer(0)
                if not thisPoly.is_empty:
                    if jj==0:
                        geom = thisPoly
                        g_tmp = gpd.GeoDataFrame(columns=['contour', 'name', 'geometry'],
                                                 crs=self.utmCode)
                        g_tmp.loc[0, 'contour'] = this_cntr
                        g_tmp.loc[0, 'geometry'] = geom
                        g_tmp.loc[0, 'name'] = name
                    else:
                        if g_tmp.loc[0, 'geometry'].contains(thisPoly):
                            geom = g_tmp.loc[0, 'geometry'].difference(thisPoly)
                        else:
                            try:
                                geom = g_tmp.loc[0, 'geometry'].union(thisPoly)
                            except:
                                print('Error processing polygon contour -- skipping.  Better check the result!')
                        g_tmp.loc[[0], 'geometry'] = gpd.GeoSeries([geom])
                
            if kk==0:
                g = gpd.GeoDataFrame(g_tmp).set_geometry('geometry')
            else:
                g = gpd.GeoDataFrame(pd.concat([g, g_tmp], ignore_index=True))
            
        g['contour'] = g['contour'].astype('float64')
        
        return g

    def max_depth_contours(self, name='MaxHeights', cntrs=0.1, vmin=0.1):
        
        maxh = self.max_depth(vmin=vmin)

        if maxh is not None:
            maxh = maxh['maximum_depth']
            if type(cntrs)==np.ndarray:
                cntrs = cntrs.tolist()
            else:
                if cntrs=='Jenks':
                    cntrs = jenkspy.jenks_breaks(self._raster_flatten(maxh), nb_class=10)
                    cntrs = [c for c in cntrs if c>=vmin]
                    cntrs = cntrs[:-1]
                if type(cntrs) is not list:
                    cntrs = [cntrs]
            
            cntrs.sort()
        
            g = self._raster_contour(maxh, name, cntrs)
            return g
        else:
            return None
    
    def max_speed_contours(self,name='MaxSpeeds',cntrs=1, vmin=None):
        
        maxspd = self.max_speed(vmin=vmin)

        if maxspd is not None:
            maxspd = maxspd['maximum_speed']
            if type(cntrs)==np.ndarray:
                cntrs = cntrs.tolist()
            else:
                if cntrs=='Jenks':
                    cntrs = jenkspy.jenks_breaks(self._raster_flatten(maxspd), nb_class=10)
                    cntrs = [c for c in cntrs if c>=vmin]
                    cntrs = cntrs[:-1]
                if type(cntrs) is not list:
                    cntrs = [cntrs]
            
            cntrs.sort()
        
            g = self._raster_contour(maxspd, name, cntrs)
            return g
        else:
            return None

    def inundation_time_contours(self,name='InundationTime',cntrs=0,vmin=0):
        
        itime = self.inundation_time(vmin=vmin)

        if itime is not None:
            if type(cntrs)==np.ndarray:
                cntrs = cntrs.tolist()
            else:
                if cntrs=='Jenks':
                    cntrs = jenkspy.jenks_breaks(self._raster_flatten(itime), nb_class=10)
                    cntrs = [c for c in cntrs if c>=vmin]
                    cntrs = cntrs[:-1]
                if type(cntrs) is not list:
                    cntrs = [cntrs]
            
            cntrs.sort()
            
            g = self._raster_contour(time, name, cntrs)
            
            return g
        else:
            return None
    
    def save_gtiff(self, fileIn, fileOut=None, crs=None, **kwargs):

        fileIn = self._valid_input_file(fileIn)

        raster = self.raster(fileIn, crs=crs)

        if fileOut is None:
            fname = fileIn.replace('.txt', '.tif')
            fileOut = os.path.join(self.dir, fname)
        else:
            fileOut = os.path.join(self.dir, fileOut)

        print('Writing file to {}'.format(fileOut))
        raster.rio.to_raster(fileOut, **kwargs)
        return
    
    def plot(self, result, variable,
                 crs=webmerc,
                 ax=None,
                 vmin=0.1,
                 vmax=None,
                 vcut=None,
                 interpolation='nearest',
                 cmap=plt.cm.viridis,
                 cax=None,
                 zorder=1,
                 orientation="vertical",
                 title=None):

        _ = self._valid_input_file(result)
        filetype = self._file_type(result)

        self._valid_variable(variable)

        fmt = _get_LF_output_fmt(variable, filetype=filetype)

        raster = self.raster(result, crs=crs, nodata=np.nan)

        dataArray = raster[variable]

        if vmax is None:
            maxval = np.nanmax(dataArray.data)
            vmax = _nice_round(maxval)
        
        if vmin is not None:
            data = np.ma.masked_less(dataArray.data, vmin)
        
        if vcut is not None:
            data = np.ma.masked_inside(data, vcut[0], vcut[1])

        if ax is None:
            fig, ax = plt.subplots()
        
        im = ax.imshow(data,
                       interpolation=interpolation,
                       cmap=cmap,
                       extent=[min(dataArray.x), max(dataArray.x), min(dataArray.y), max(dataArray.y)],
                       zorder=1,
                       vmin=vmin,
                       vmax=vmax)

        if cax is not None:
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
        
        cbar = plt.colorbar(im, cax=cax, orientation=orientation)
        cbar.ax.set_ylabel(fmt['short_name'].replace('_',' ') 
                            + ' ({unit})'.format(unit=fmt['units']))
        
        ax.get_xaxis().set_visible(False) 
        ax.get_yaxis().set_visible(False)

        return ax, im, cbar