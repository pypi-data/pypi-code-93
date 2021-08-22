<<<<<<< HEAD
"""

This package invokes an ept pipeline an uses user defined specifications to build the pipeline  
 
 """



=======
>>>>>>> 5008b8b2173e1144705e22b428283a3ac74ca6ac
import pdal
import json
import os
import sys
import logging
<<<<<<< HEAD
=======
from glob import glob
>>>>>>> 5008b8b2173e1144705e22b428283a3ac74ca6ac

#### we intialize the dataset location present in aws
dataset_path='https://s3-us-west-2.amazonaws.com/usgs-lidar-public/'
###we select iowa region to gather info from it
selected_region='IA_FullState'
logging.basicConfig(filename='..\logs\generate.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)



bounds="([-10425171.940, -10423171.940], [5164494.710, 5166494.710])"

full_path=dataset_path+selected_region+"ept.json"

output_file_laz="iowa.laz"
output_file_tif="iowa.tif"
pipeline="../jsons/user.json"

def gather_input():
    logging.info(" ##### Initialize gather input function ##### \n")
    
    print(" ===== Welcome to the API fetch module === \n ")
    print(" ==== Insert region you would like to search ==== \n")
    
    
    region=input()
    logging.info("#### Read Region ##### ")
    full_path=dataset_path+region+"/ept.json"
    
    
    print(" ===== Insert the regions bound ====== \n")
    bound=input()
    logging.info("#### Read bound ##### \n")
    
    print(" ==== Insert Output filename for laz file ===== \n ")
    output_file_laz=input()
    output_file_laz="../laz/"+output_file_laz+".laz"
    logging.info("#### Read lazfile ##### \n")
    
    
    print(" === Insert output filename for tif file ===== \n  ")
    output_file_tif=input()
    output_file_tif="../tif/"+output_file_tif+".tif"
    logging.info("#### Read Tiff file ##### \n ")
    
    print(" === Insert output filename for csv file ===== \n  ")
    output_file_csv=input()
    output_file_csv="../geojson/"+output_file_csv+".csv"
    logging.info("#### Read csv file ##### \n ")
    
    print("This is the input region serch")
    print(" ###### {} : region \n {} :bounds".format(region,bound))
    
    return bound,full_path,output_file_laz,output_file_tif,output_file_csv
    

def get_raster_terrain(bounds,full_path,output_file_laz,output_file_tif,output_file_csv,pipeline):
    
    

    print(" ***** Reading pipleine file ****** ")
    try:
        with open(pipeline) as json_file:
            file_json=json.load(json_file)
        print(" ##### Succesfuly read json file ###### ")   
    except FileNotFoundError as f:
        print(" !!! The specified pipeline json file doesn't exist !!!! ")
        logging.error("#### File Not found error ##### ")
        sys.exit(1)
    
    try:
        print(" ........Imputing Bounds ........,\n")
        file_json['pipeline'][0]['bounds']=bounds
        print(" ........Imputing Region ........ \n")
        file_json['pipeline'][0]['filename']=full_path
        print(" ........Filling outputpath file.........\n")
        file_json['pipeline'][5]['filename']=output_file_laz
        print(" ........Imputing tif filepath .........")
        file_json['pipeline'][6]['filename']=output_file_tif
        
        print(" ........Imputing tif filepath .........")
        file_json['pipeline'][7]['filename']=output_file_csv

        print(" ##### Successfully changed pipeline values ##### ")
        logging.info(" ##### Successfully changed pipeline values ##### ")
    except Exception as e:
        print(" !!! Error !!!!! \n")
        print (" !!! An excetion occurred Error: {} ".format(e.__class__))
        logging.error(" !!! Error Program Failed !!!!! \n")
        logging.error("Safely exiting the program")
        print("Safely exiting the program")
        sys.exit(1)
    
    print("Processing pipeline")
    pipeline=pdal.Pipeline(json.dumps(file_json))

     
    print("###### executinng pipeline ###")
    pipe_execute=pipeline.execute()
    metadata=pipeline.metadata


<<<<<<< HEAD
=======
def get_shp_from_tif(tif_path:str, shp_file_path:str) -> None:
    raster = rasterio.open(tif_path)
    bounds = raster.bounds

    df = gpd.GeoDataFrame({"id":1,"geometry":[box(*bounds)]})
   
    # save to file
    df.to_file(shp_file_path)
    print('Saved..')

>>>>>>> 5008b8b2173e1144705e22b428283a3ac74ca6ac

if (__name__== '__main__'):

    pipeline="../jsons/user.json"
    bounds,full_path,output_file_laz,output_file_tif,output_file_csv=gather_input()
    get_raster_terrain(bounds,full_path,output_file_laz,output_file_tif,output_file_csv,pipeline)




