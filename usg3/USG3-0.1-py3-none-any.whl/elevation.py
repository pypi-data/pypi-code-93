###This calculates the elevation of a place

import geopandas as gpd
import earthpy as et
import shapely
from shapely.geometry import Point
from shapely.geometry import shape 
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import rasterio
import pandas as pd


def elevation(shpfile,tiffile):
    area=gpd.read_file(shpfile)
    ##we get the longitudes and latitudes
    identifier=area.id
    geo=area['geometry']
    long=area.iloc[0].geometry.centroid.x
    lat=area.iloc[0].geometry.centroid.y
    rasters=rasterio.open(tiffile)
    row,col=rasters.index(long,lat)
    
    elevationn=rasters.read(1)
    point_elevation=elevationn[row,col]
    
    df=pd.DataFrame([[identifier,long,lat,point_elevation,geo]],columns=['Identifier','Longititude','Latitude','Elevation','geometry'])
    print (df)
    return point_elevation

pointelevation=elevation('../shp/combi.shp','../tif/iowaclassified.tif')
print(pointelevation)    

