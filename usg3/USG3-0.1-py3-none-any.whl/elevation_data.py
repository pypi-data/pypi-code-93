<<<<<<< HEAD

"""
This package calculates elevation of given geometric points 
The geometric points must have come from a shape file

It returns a geopandas dataframe as well as dataframe 

"""

=======
>>>>>>> 5008b8b2173e1144705e22b428283a3ac74ca6ac
import pylas 
import laspy
from shapely.geometry import Point
import pandas as pd
import numpy as np
import os
import sys
import logging
import geopandas as gpd

logging.basicConfig(filename='../logs/generate.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

def get_elevation(laz_file,las_file,output_path,crs):
    
    print(" #### Accessing elevation function #### \n")
    
    #read laz file
    try:
        print("#### Reading Laz file ####")
        laz=pylas.read(laz_file)
        print("##### Done ####")
    except FileNotFoundError as f:
        
        print(" !!! The laz file file doesn't exist !!!! ")
        sys.exit(1)
    #convert laz file to las file equivalent and write to las file
    
    print("#### Converting laz to las #### \n ")
    las=pylas.convert(laz)
    print("#### Writing las file #### \n")
    las.write(las_file)
    
    try:
        print("#### Reading las file #### \n")
        lasfile=laspy.read(las_file)
    except Exception as e:
        print(" !!! Error !!!!! \n")
<<<<<<< HEAD
        print (" !!! An exception occurred Error: {} ".format(e.__class__))
=======
        print (" !!! An excetion occurred Error: {} ".format(e.__class__))
>>>>>>> 5008b8b2173e1144705e22b428283a3ac74ca6ac
        logging.error(" !!! Error Program Failed !!!!! \n")
        logging.error("Safely exiting the program")
        print("Safely exiting the program")
        sys.exit(1)
    
    
    
    with laspy.open(las_file) as f:
        print(f"Point format:       {f.header.point_format}")
        print(f"Number of points:   {f.header.point_count}")
        print(f"Number of vlrs:     {len(f.header.vlrs)}")
    
    #get points and 
    print("#### Converting to GeoPandas DataFrame #### \n ")
    lasfile_points=np.array((lasfile.x,lasfile.y,lasfile.z,lasfile.intensity,lasfile.raw_classification,lasfile.scan_angle_rank)).transpose()
    
    print("#### Generating columns #### \n")
    lasfile_df=pd.DataFrame(lasfile_points)
    lasfile_df.columns=['X','Y','Z','intensity','classification','scan_angle']
    
    #convert to geodataframe
    geoDF=lasfile_df[['X','Y','Z']]
    
    print("#### Finishing up on your geopandas file #### \n")
    geometry=[Point(xy)for xy in zip(pd.to_numeric(geoDF['X']),pd.to_numeric(geoDF['Y']))]
    geoDF=gpd.GeoDataFrame(geoDF,crs=crs,geometry=geometry)
    geoDF=geoDF[['Z','geometry']]
    
    
    geoDF.columns=['elevation_m','Geometry']
    
    print("#### Done..all set #### \n")
    print("#### Collect your file #### \n")
    
    return geoDF,lasfile_df
    
    
    

                                        
        
    