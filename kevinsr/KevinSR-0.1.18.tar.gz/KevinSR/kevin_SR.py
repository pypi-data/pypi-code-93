import os
import numpy as np
from scipy.ndimage import zoom
from scipy.ndimage import distance_transform_edt as dist_field


def mask_interpolation(mask,factor, **kwargs):

    """ Resizing the mask through interpolation by building the distance field.

        Randomly sampling factor and multi-categories are considered. 

        Implemented by Kuan (Kevin) Zhang, Ph.D., Radiology Informatics Laboratory, Mayo Clinic.


        This implementation follows:
        How to properly interpolate masks for deep learning in medical imaging?
 
        Args:
            mask (np.array): The initial mask matrix in the shape: (slices, x, y)
            factor (tuple): The sampling factor of resizing in the shape: (fx, fy, fz)
      
        Output:
            The interpolated mask matrix to return.

    """

     # Check the number of mask types contained in the input.
#    mask_types = np.unique(mask).size -1
    mask_types = int(mask.max())

    if mask_types <1:
        raise ValueError("Input masks need to include more than one category!")

    if mask_types >1:

        # Creat a list for the multi-category lables.
        mask_mul = []


        # Conver the mask values into binary for each type.
        for i in range(mask_types):
            mask_mul.append(np.where(mask == i+1,1,0))

        mask_dist = mask_mul.copy()

        for i in range(mask_types):
            for z in range(mask.shape[-1]):

                # The inner distance field to the edge: 
                dist_field_inner = dist_field(mask_mul[i][:,:,z])

                # The outer distance field to the edge:
                dist_field_outer = dist_field(np.logical_not(mask_mul[i][:,:,z]))

                mask_dist[i][:,:,z] = dist_field_inner - dist_field_outer
      
            mask_dist[i] = zoom(mask_dist[i],factor,order =1)
        #    mask_dist[i] = zoom(mask_dist[i],factor,**kwargs)


        # Apply the threshold on the interpolated mask values.
        # The threshold is set as 0.0.  
        mask_new = np.zeros(mask.shape)
        for i in range(mask_types):
            mask_new = np.where(mask_dist[i] >0.0, i+1, 0)

        return mask_new

    else:

        # For the binary mask type.
        mask_dist = np.zeros(mask.shape)

        for z in range(mask.shape[-1]):

            # The inner distance field to the edge:
            dist_field_inner = dist_field(mask[:,:,z])

            # The outer distance field to the edge:
            dist_field_outer = dist_field(np.logical_not(mask[:,:,z]))

            mask_dist[:,:,z] = dist_field_inner - dist_field_outer

        mask_dist = zoom(mask_dist,factor,order =1)
        #mask_dist = zoom(mask_dist,factor,**kwargs)

        return np.where(mask_dist>0.0, 1,0)
        
