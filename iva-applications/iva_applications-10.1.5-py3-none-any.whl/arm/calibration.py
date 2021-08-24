"""Calibration utils for ARM Networks trained on Speech Commands dataset."""
import numpy as np
from iva_applications.arm.preprocess import Preprocessor


def save_calibration_tensor(wav_file: str, clip_duration_ms: int = 1000, clip_stride_ms: int = 30):
    """Create calibration tensors for Basic LSTM."""
    preprocessor = Preprocessor()
    sample_rate, data = preprocessor.decode_wav_file(wav_file)
    data_samples = data.shape[0]
    clip_duration_samples = int(clip_duration_ms * sample_rate / 1000)
    clip_stride_samples = int(clip_stride_ms * sample_rate / 1000)
    audio_data_end = data_samples - clip_duration_samples
    tensors = []
    # Inference along audio stream.
    for audio_data_offset in range(0, audio_data_end, clip_stride_samples):
        input_start = audio_data_offset
        input_end = audio_data_offset + clip_duration_samples
        tensor = preprocessor.wav_to_tensor(np.expand_dims(data[input_start:input_end], axis=-1), sample_rate)
        tensors.append(tensor)
    calibration_tensor = np.stack(tensors, axis=1)
    calibration_tensor = np.squeeze(calibration_tensor)
    np.save('calibration_tensors_arm_L.npy', calibration_tensor)
