import h2o
import pandas as pd
from os import path
import numpy as np
from osgeo import gdal, osr
from typing import Tuple
from scipy.interpolate import interp1d
gdal.UseExceptions()
gdal_driver = gdal.GetDriverByName('GTiff')
invalid = np.array(np.nan)

from physicalrisk.handler.build_prediction_data import Data_Handler
from physicalrisk.handler.printMessageHandler.formatePrint import Formatter
from physicalrisk.handler.database import DataQ
from physicalrisk.handler.AWSdata import aws

property_type = DataQ("select * from crrem.vw_property_type").data

class Building:
    def __init__(self, lon, lat, prop_type_code):
        #epc = DataQ(f"""select * from public.epcsourcedata where "BUILDING_REFERENCE_NUMBER" = {building_id} """).data
#         self.lon_lat = [epc['PostcodeLongitude'], epc['PostcodeLatitude']]
#         self.prop_type_code = epc['PROPERTY_TYPE_CODE']
#         self.floor_height = epc['FLOOR_HEIGHT']
        self.lon_lat = [lon, lat]
        self.prop_type_code = prop_type_code

    def predict_and_output(self, Longititude_Latitude: list, scenario):

        Construct_Features = Data_Handler()
        df_to_predict = Construct_Features.build_prediction_data(self.lon_lat, scenario)
        self.flood_depth = Construct_Features.flood_depth(self.lon_lat)
        
        h2o.init(log_level="ERRR")
        h2o_auto_model = h2o.import_mojo("Physical_Risk_Model_ML/GBM_grid__1_AutoML_20210810_210013_model_4.zip")

        Formatter.green(f'Starting H2O_Auto_ML Prediction')

        h2odf_to_predict = h2o.H2OFrame(df_to_predict)
        result = h2o_auto_model.predict(h2odf_to_predict)
        result_df = h2o.as_list(result)
        probability = result_df['predict'].iloc[0]
        return probability

    def flood_depth(self):
        Construct_Features = Data_Handler()
        flood_depth = Construct_Features.flood_depth(self.lon_lat)
        return flood_depth
    
    def VAR(self,scenario):
        #calculate flood damage
        flood_damage_type = property_type[property_type['prop_type_code']==self.prop_type_code]['prop_group_name'].squeeze()
        damage = DataQ("select * from physical.vw_flood_damage").data
        damage = damage[damage['prop_use_group_name']==flood_damage_type]
        x = damage['flood_depth']
        y = damage['flood_damage']
        f = interp1d(x, y, kind='quadratic')
        flood_damage = float(f(self.flood_depth()))

        probability = self.predict_and_output(self.lon_lat,scenario)
        VAR = flood_damage*probability
        return VAR