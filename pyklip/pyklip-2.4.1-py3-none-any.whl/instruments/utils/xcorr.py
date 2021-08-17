import numpy as np
import scipy
import pyklip.klip

def _img_xcorr_shift(shift, frame1, frame2, mask=None):
    """
    Compute the negative of the xcorr between frame1 and frame2 given shift:
    
    Args:
        shift: [dx, dy] in pixels to shift frame2
        frame1: refernce frame of shape (Y, X)
        frame2: frame to align of shape (Y, X)
        mask: shape of (Y, X) where =1 for good pixels and =0 for bad pixels
        
    Return:
        negative of xcorr between frame1 and the shifted frame2
    """
    dx, dy = shift
    oldcenter = [frame2.shape[1], frame2.shape[0]]
    frame2_shifted = pyklip.klip.align_and_scale(frame2, [oldcenter[0] + dx, oldcenter[1] + dy], oldcenter)
    if mask is not None:
        good = np.where(mask > 0)
        frame1 = frame1[good]
        frame2_shifted = frame2_shifted[good]
    
    return -np.nansum(frame1*frame2_shifted)


def find_best_shift(frame, ref_frame, guess_center=None, inner_mask=5, outer_mask=None):
    """
    Finds the best shift based on xcorr
    
    Args:
        frame: frame to find offset of. Shape of (Y, X)
        ref_frame: reference frame to align frame to. Shape of (Y, X)
        
    Return:
        (dx, dy): best shift to shift frame to match reference frame
    """
    if guess_center is None:
        guess_center = np.array([frame.shape[1]/2., frame.shape[0]/2.])
    
    if outer_mask is None:
        outer_mask = frame.shape[0]/2 - 10
    
    # make mask
    y, x = np.indices(frame.shape)
    r = np.sqrt((x-guess_center[0])**2 + (y-guess_center[1])**2)
    mask = np.ones(frame.shape)
    bad = np.where((r < inner_mask) | (r > outer_mask))
    mask[bad] = 0
    
    result = scipy.optimize.minimize(_img_xcorr_shift, (0,0), args=(ref_frame, frame, mask), method="Nelder-Mead")
    
    return result.x

