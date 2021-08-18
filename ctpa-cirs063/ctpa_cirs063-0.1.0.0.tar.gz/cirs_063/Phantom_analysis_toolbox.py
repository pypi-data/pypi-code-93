import pydicom
import cv2
import scipy
import numpy as np
import os
import scipy.signal
import matplotlib.pyplot as plt
import math

class Phantom_analysis_toolbox():
    def __init__(self, used_path):
        self.path = used_path
        self.dcm_reader()
        self.pixel_size_calc()
        self.slice_thickness = self.header.SliceThickness
        
        pass
    
    def dcm_reader(self):
        #read dcm_files from path
        #path certainly contains DCM files, as tested by dcm_list_builder function
        dcm_path = self.path
        
        dcm_files = []
        for (dirpath, dirnames, filenames) in os.walk(dcm_path,topdown=False):
            for filename in filenames:
                try:
                    if not filename == 'DIRFILE':   
                        dcm_file = str('\\\\?\\' + os.path.join(dirpath, filename))
                        pydicom.read_file(dcm_file, stop_before_pixels = True)
                        dcm_files.append(dcm_file)
                except:
                    pass
    
        read_RefDs = True
        while read_RefDs:
            for index in range(len(dcm_files)):
                try:
                    RefDs = pydicom.read_file(dcm_files[index], stop_before_pixels = False)
                    read_RefDs = False
                    break
                except:
                    pass
        
        slice_thick_ori = RefDs.SliceThickness
        
        ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(dcm_files))
        dcm_array = np.zeros([ConstPixelDims[0],ConstPixelDims[1],len(dcm_files)],\
                              dtype=RefDs.pixel_array.dtype) 
    
        instances = []    
        for filenameDCM in dcm_files:
            try:
                ds = pydicom.read_file(filenameDCM, stop_before_pixels = True)
                instances.append(int(ds.InstanceNumber))
            except:
                pass
        
        instances.sort()

        index = 0
        for filenameDCM in dcm_files:
            try:
                ds = pydicom.read_file(filenameDCM)
                dcm_array[:,:,instances.index(ds.InstanceNumber)] = ds.pixel_array
                if ds.InstanceNumber in instances[:2]:
                    if ds.InstanceNumber == instances[0]:
                        loc_1 = ds.SliceLocation
                    else:
                        loc_2 = ds.SliceLocation
                index += 1
            except:
                pass
            
        try:
            RefDs.SliceThickness = abs(loc_1 - loc_2)
        except:
            pass
            
            
        dcm_array = dcm_array * RefDs.RescaleSlope + RefDs.RescaleIntercept
        
        self.header = RefDs
        self.array = dcm_array
        self.slice_thick_ori = slice_thick_ori
        return None
    
    def pixel_size_calc(self):
        try:
            self.pixel_size = self.header.PixelSpacing[0]
        except:
            FOV = self.header.ReconstructionDiameter
            matrix_size = self.header.Rows
        
            self.pixel_size = FOV / matrix_size            
        return None
    
    @staticmethod
    def dcm_filtering(array, image_kernel = 3):
        if image_kernel % 2 == 0:
            image_kernel += 1
            
        if len(array.shape) == 2:
            array_filtered = scipy.signal.medfilt2d(array, image_kernel)
        else:
            array_filtered = np.zeros_like(array)
            for index_slice in range(array.shape[2]):
                array_filtered[:,:,index_slice] = scipy.signal.medfilt2d(array[:,:,index_slice], image_kernel)
        
        return array_filtered
    
    @staticmethod
    def arr_connected_components(array, connections = 4):
        output = cv2.connectedComponentsWithStats(array,\
                                                  connections,cv2.CV_32S)
            
        return output
    
    @staticmethod
    def dcm_threshold(array, threshold, multiplier = 1): 
        if len(array.shape) == 2:
            tmp_array = array
            tmp_array[tmp_array <= threshold * multiplier] = 0
            tmp_array[tmp_array >= threshold * multiplier] = 1
                
            
        else:
            for index in range(array.shape[2]):
                tmp_array = array[:,:,index]
                tmp_threshold = threshold[index] * multiplier
         
                tmp_array[tmp_array <= tmp_threshold] = 0
                tmp_array[tmp_array >= tmp_threshold] = 1
         
                array[:,:,index] = tmp_array
            
        array = array.astype(dtype = np.uint8)
     
        return array

    @staticmethod
    def pop_noncircular_objects(array, sphere_dict, sphere_est = 0.4):
        poppable_keys = []
        
        for key in sphere_dict.keys():
            start_coordinate = [sphere_dict[key][0], sphere_dict[key][1]]
            
            x_right = 0
            while array[start_coordinate[0], start_coordinate[1] + x_right] == 1:
                x_right += 1
            
            x_left = 0
            while array[start_coordinate[0], start_coordinate[1] - x_left] == 1:
                x_left += 1
            
            y_top = 0
            while array[start_coordinate[0] + y_top, start_coordinate[1]] == 1:
                y_top += 1
            
            y_bottom = 0
            while array[start_coordinate[0] - y_bottom, start_coordinate[1]] == 1:
                y_bottom += 1
                
            x_dist = x_right + x_left
            y_dist = y_top + y_bottom
            
            if x_dist not in range(int((1 - sphere_est)*y_dist),\
                                   int((1 + sphere_est)*y_dist)):
                poppable_keys.append(key)
            else:
                pass
            
        for key in poppable_keys:
                sphere_dict.pop(key)
                
        return sphere_dict
    
    @staticmethod
    def create_circular_mask(h, w, center_circle, radius_circle):

        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center_circle[0])**2 + (Y-center_circle[1])**2)
    
        mask = dist_from_center <= radius_circle
        
        return mask
        
    
    @classmethod
    def find_circle(cls, array, threshold, physic_size, physic_size_est = 0.5, plot_centers = False):
        array_ori = array.copy()
        
        array_threshold = cls.dcm_threshold(array.copy(), threshold)
        array_filtered = cls.dcm_filtering(array_threshold, image_kernel = 5)
        
        output = cls.arr_connected_components(array_filtered, connections = 4)
        
        circle_centers = {}
        #add all centers if larger in range of physical area of spheres
        for index in range(1,output[0]):
            physical_size = physic_size
            measured_size = output[2][index][4]
            if measured_size in range (int(physical_size * (1 - physic_size_est)), int(physical_size * (1 + physic_size_est))):
                circle_centers[index] = [round(output[3][index][1]), round(output[3][index][0])]
                
        circle_centers = cls.pop_noncircular_objects(array_filtered, circle_centers)
               
        if plot_centers:
            for key in circle_centers.keys():
                # array_ori[sphere_centers[key][0], sphere_centers[key][1]] = 2 * array_ori.max()
                mask = cls.create_circular_mask(cls.header.Columns, cls.header.Rows, [circle_centers[key][1], circle_centers[key][0]], 5)
                mask = mask * np.ones_like(mask) * 2 * array_ori.max()
                array_ori += mask
        
            plt.imshow(array_ori)
            plt.show()
        
        if len(circle_centers) == 1:
            for key in circle_centers.keys():
                circle_centers = circle_centers[key]
        
        
        return circle_centers
        
    @staticmethod 
    def distance_between_points(coor1, coor2):
        x1 = coor1[0]
        x2 = coor2[0]
        y1 = coor1[1]
        y2 = coor2[1]
        
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        return distance
    
    @classmethod 
    def calc_mean_SD(cls, array, center, ROI_radius):
        array = array.copy()
        mask = cls.create_circular_mask(array.shape[0], array.shape[1], center, ROI_radius)
        
        flat_mask = mask.flatten()
        flat_masked_array = (mask * array).flatten()
        
        ROI_array = flat_masked_array[flat_mask]
        
        mean = round(ROI_array.mean(), 2)
        SD = round(ROI_array.std(), 2)
        
        return mean, SD
    
    