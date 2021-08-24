"""Dequantize int8 data to float32."""
import pickle
import numpy as np


def get_output_scale(fpga_data_path: str) -> np.ndarray:
    """
    Get float16 scale based on int16 scale and int8 shift.

    Parameters
    ----------
    fpga_data_path: path to fpga_data.pickle file

    Returns
    -------
    int16 scale, int8 shift.
    """
    with open(fpga_data_path, 'rb') as file:
        data = pickle.load(file)
    output_node_data = data['output_node_1']
    scale = output_node_data['pos_scale']
    shift = output_node_data['pos_shift']
    return scale * 2. ** shift


def dequantize(data: np.ndarray, scale: np.float16) -> np.ndarray:
    """
    Scale data based on float16 scale.

    Parameters
    ----------
    data: data to scale.
    scale: float16 scale.

    Returns
    -------
    Scaled data.
    """
    return data * scale
