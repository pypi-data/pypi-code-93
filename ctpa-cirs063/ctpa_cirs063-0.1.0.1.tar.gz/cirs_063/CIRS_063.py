# main document for CT phantom analysis

import pydicom
# import SimpleITK as sitk
import os
import numpy as np
# import scipy
import matplotlib.pyplot as plt
# import cv2
import math
import statistics
from cirs_063.Phantom_analysis_toolbox import Phantom_analysis_toolbox as pat

  

    
class CIRS_063_analyser(pat):
    def __init__(self, used_path):
        super().__init__(used_path)
        
        self.large_insert_size = math.pi * (30/2)**2 / self.pixel_size**2
        self.large_insert_HU = 550
        self.small_insert_size = math.pi * (10/2)**2 / self.pixel_size**2
        self.small_insert_HU = 500
        self.air_insert_HU = -800
        self.large_insert_ROI = int((20/2) / self.pixel_size)
        self.small_insert_ROI = int((7/2) / self.pixel_size)
        self.WAD_output = {}
        
        if (self.array.shape[2] * self.slice_thickness) < 25:
            raise ValueError("Detection of central slice has to be defined")
        else:
            self.CIRS_063_center_slice()
            
        self.CIRS_063_object_locater(plot_centers = False)
        self.CIRS_063_measurements()
        

        return None
    
    
    def CIRS_063_center_slice(self):
        array = self.array.copy()
        
        center_slices = []
        for slice_index in range(array.shape[2]):

            sphere_centers = pat.find_circle(self.array[:,:,slice_index],\
                                             self.small_insert_HU,\
                                                 self.small_insert_size)
            
            if len(sphere_centers) > 0:
                center_slices.append(slice_index)

        self.center_slice = int(statistics.median(center_slices))
        self.center_min_max = [min(center_slices), max(center_slices)]       
        
        return None
    
    @staticmethod
    def calc_polar_angle(delta_x, delta_y):
        angle = math.atan(delta_y / delta_x)
                
        return angle
    
    
    def high_dens_param(self):
        #locate large high density object
        large_center = pat.find_circle(self.array[:,:,self.center_slice],\
                                                  self.large_insert_HU, self.large_insert_size)
            
        #locate small high density object
        small_center = pat.find_circle(self.array[:,:,self.center_slice],\
                                                  self.small_insert_HU, self.small_insert_size)
             
        #locate center air-object
        air_center = pat.find_circle(-self.array[:,:,self.center_slice],\
                                                  -self.air_insert_HU, self.large_insert_size)
        
        large_dist = pat.distance_between_points(large_center, air_center)
        small_dist = pat.distance_between_points(small_center, air_center)
        
        average_dist = (large_dist + small_dist) / 2
        
        angle_offset = self.calc_polar_angle(small_center[0] - air_center[0],\
                                        small_center[1] - air_center[1])
        
        return air_center, average_dist, angle_offset
    
    
    def calc_object_centers(self, center, radius, angle_offset):
        radius_inner = radius
        radius_outer = radius + (55 / self.pixel_size)
        radius_outer_4 = radius + (50 / self.pixel_size) 
        
        angles = []
        for index in range(8):
            angles.append(index * math.pi / 4 - angle_offset - math.pi / 2)
            
        inner_object_centers = []
        outer_object_centers = []
        for angle in angles:
            inner_object_centers.append([round(center[0] + (radius_inner * math.cos(angle))),\
                                         round(center[1] + (radius_inner * math.sin(angle)))])
            outer_object_centers.append([round(center[0] + (radius_outer * math.cos(angle))),\
                                         round(center[1] + (radius_outer * math.sin(angle)))])
                
        outer_object_centers[4] = [round(center[0] + (radius_outer_4 * math.cos(angles[4]))),\
                                   round(center[1] + (radius_outer_4 * math.sin(angles[4])))]
        
        self.inner_object_centers = inner_object_centers
        self.outer_object_centers = outer_object_centers
        
        return None
    
    @staticmethod 
    def add_mask(columns, rows, obj_center, mask_in, array_max, mask_size = 3):
        
        mask_new = pat.create_circular_mask(columns, rows, obj_center , mask_size)
        mask_new = mask_new * np.ones_like(mask_new) * 2 * array_max
        
        mask_out = mask_in + mask_new
        
        return mask_out
    
    
    @staticmethod
    def object_dict_init(inner_obj, outer_obj):
        object_dict = {}
        
        dict_keys_inner = ['inner_top', 'inner_upper_right', 'inner_right', 'inner_lower_right',\
                           'inner_bottom', 'inner_lower_left', 'inner_left', 'inner_upper_left']
        dict_keys_outer = ['outer_top', 'outer_upper_right', 'outer_right', 'outer_lower_right',\
                           'outer_bottom', 'outer_lower_left', 'outer_left', 'outer_upper_left']
        
        for index in range(len(dict_keys_inner)):
            object_dict[dict_keys_inner[index]] = [inner_obj[index]]
        
        for index in range(len(dict_keys_outer)):
            object_dict[dict_keys_outer[index]] = [outer_obj[index]]    
            
        return object_dict  

    
    def CIRS_063_object_locater(self, plot_centers = False):
        center, radius, angle_offset = self.high_dens_param()
        
        self.calc_object_centers(center, radius, angle_offset)
        
        array = self.array[:,:,self.center_slice].copy()
            
        mask = np.zeros_like(array)
        mask = self.add_mask(self.header.Columns, self.header.Rows, center, mask, array.max()) 
        
        for obj_center in self.inner_object_centers:
            mask = self.add_mask(self.header.Columns, self.header.Rows, obj_center, mask, array.max())
            
        for obj_center in self.outer_object_centers:
            mask = self.add_mask(self.header.Columns, self.header.Rows, obj_center, mask, array.max())
        
        if plot_centers:
            plt.subplot(131)
            plt.imshow(array)
            plt.subplot(132)
            plt.imshow(mask)
            plt.subplot(133)
            plt.imshow(array + mask)
            plt.show()
            
        self.objects = self.object_dict_init(self.inner_object_centers,\
                                             self.outer_object_centers)
        self.WAD_output['image'] = array + mask
        
        del self.inner_object_centers
        del self.outer_object_centers

        return None
    
    
    def CIRS_063_measurements(self):
        # measure mean and SD for each of the objects
        
        for key in self.objects.keys():
            if key != 'image':
                center = self.objects[key][0]
                if 'inner_top' in key:
                    size_obj = self.small_insert_ROI
                else:
                    size_obj = self.large_insert_ROI
                    
                mean, SD = pat.calc_mean_SD(self.array[:,:,self.center_slice],\
                                                center, size_obj)
                
                self.objects[key].append(mean)
                self.objects[key].append(SD)
                self.WAD_output[key + '_mean'] = mean
                self.WAD_output[key + '_SD'] = SD
                
        return None
        
        
def dcm_list_builder(path, test_text = ""):
    # function to get list of dcm_files from dcm directory
    dcm_path_list = []
    for (dirpath, dirnames, filenames) in os.walk(path,topdown=True):
        if dirpath not in dcm_path_list:
            for filename in filenames:
                try:
                    tmp_str = str('\\\\?\\' + os.path.join(dirpath, filename))
                    pydicom.read_file(tmp_str, stop_before_pixels = True)
                    if dirpath not in dcm_path_list:
                        dcm_path_list.append(dirpath)
                except:
                    pass
            else:
                pass
    return dcm_path_list