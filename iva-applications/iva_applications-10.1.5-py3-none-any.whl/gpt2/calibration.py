"""Creation of calibration tensors for GPT2."""
import os
import numpy as np
from iva_applications.gpt2.preprocess import text_preprocessing


def save_calibration_tensors(save_dir: str, path_to_csv: str) -> None:
    """
    Doing all the steps to produce calibration tensors.

    Tokenizing our 100 sentences and creating corresponding attention masks.
    Then we convert our tokens into word embeddings and extend our attention masks.
    Last step is the saving calibration tensors

    Parameters
    ----------
    save_dir
        directory for saving tensors
    path_to_csv
        path to csv file with raw texts
    Returns
    -------
    None

    """
    final_embeddings, final_extended_masks, _ = text_preprocessing(path_to_csv, True)
    np.save(os.path.join(save_dir, 'calibration_tensor_gpt2_embeddings'), final_embeddings)
    np.save(os.path.join(save_dir, 'calibration_tensor_gpt2_masks'), final_extended_masks)
