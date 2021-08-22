<<<<<<< HEAD

"""
This function takes classification values as input and process an ept file with the filter as the classification

"""


=======
>>>>>>> 5008b8b2173e1144705e22b428283a3ac74ca6ac
import pdal
import json
import os
import sys
import logging



#### we intialize the dataset location present in aws
dataset_path='https://s3-us-west-2.amazonaws.com/usgs-lidar-public/'
###we select iowa region to gather info from it
selected_region='IA_FullState'

bounds="([-10425171.940, -10423171.940], [5164494.710, 5166494.710])"

full_path=dataset_path+selected_region+"ept.json"

output_file_laz="iowa.laz"
output_file_tif="iowa.tif"
pipeline="../jsons/user.json"

logging.basicConfig(filename='..\logs\classification.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)



def gather_input():
    try:
        print(" ===== Welcome to the API fetch module === \n ")
        print(" ==== Insert region you would like to search ==== \n")
        region=input()
        full_path=dataset_path+region+"/ept.json"
        print(" ===== Insert the regions bound ====== \n")
        bound=input()
        print(" ==== Insert Output filename for laz file ===== \n ")
        output_file_laz=input()
        output_file_laz="../laz/"+output_file_laz+".laz"
        print(" === Insert output filename for tif file ===== \n  ")
        output_file_tif=input()
        output_file_tif="../tif/"+output_file_tif+".tif"
        print(" ==== Insert filter classification ===== \n ")
        classification=input()
    except Exception as e:
        print(" !!! Error !!!!! \n")
        print (" !!! An excetion occurred Error: {} ".format(e.__class__))
        logging.error(" !!! Error Program Failed !!!!! \n")
        logging.error("Safely exiting the program")
        print("Safely exiting the program")
        sys.exit(1)
    
    
    print("This is the input region serch")
    print(" ###### {} : region \n {} :bounds {} :filter".format(region,bound,classification))
    
    return bound,full_path,output_file_laz,output_file_tif,classification
    

def get_raster_terrain(bounds,full_path,output_file_laz,output_file_tif,classification,pipeline):
    
    

    print(" ***** Reading pipleine file ****** ")
    try:
        with open(pipeline) as json_file:
            file_json=json.load(json_file)
    except FileNotFoundError as f:
        print(" !!! The specified pipeline json file doesn't exist !!!! ")
    

    print(" ........Imputing Bounds ........,\n")
    file_json['pipeline'][0]['bounds']=bounds
    print(" ........Imputing Region ........ \n")
    file_json['pipeline'][0]['filename']=full_path
    
    print(" ........Filling outputpath file.........\n")
    file_json['pipeline'][5]['filename']=output_file_laz
    print(" ........Imputing tif filepath .........")
    file_json['pipeline'][6]['filename']=output_file_tif
    print(".......Imputing classification ........ \n")
    file_json['pipeline'][1]['limits']=classification
    
    print(" *** Entering pipeline ***** ")

    pipeline=pdal.Pipeline(json.dumps(file_json))

    print("......Executing Pipeline.....")
    pipe_execute=pipeline.execute()
    metadata=pipeline.metadata
    
if (__name__== '__main__'):

    pipeline="../jsons/user.json"
    bounds,full_path,output_file_laz,output_file_tif,classification=gather_input()
    get_raster_terrain(bounds,full_path,output_file_laz,output_file_tif,classification,pipeline)

