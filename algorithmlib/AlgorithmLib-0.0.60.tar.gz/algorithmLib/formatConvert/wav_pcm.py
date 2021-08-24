# -*- coding: UTF-8 -*-
import os
import time
import wave
import numpy as np


def wav2pcm(wavfile, data_type=np.int16):
    """
    :param wavfile:
    :param data_type:
    :return:
    """
    suffix = os.path.splitext(wavfile)[-1]
    if suffix == '.pcm':
        return wavfile
    if suffix != '.wav':
        raise TypeError('wrong format! not wav file!' + str(suffix))
    newFileName = wavfile[:-4] + '.pcm'
    f = open(wavfile, "rb")
    f.seek(0)
    f.read(44)
    data = np.fromfile(f, dtype= data_type)
    data.tofile(newFileName)
    f.close()
    return newFileName
    #os.remove(wavfile)


def pcm2wav(pcm_file, channels=1, bits=16, sample_rate=16000):
    """
    :param pcm_file:
    :param channels:
    :param bits:
    :param sample_rate:
    :return:
    """
    suffix = os.path.splitext(pcm_file)[-1]
    if suffix == '.wav':
        return pcm_file
    if suffix != '.pcm':
        raise TypeError('wrong format! not pcm file!' + str(suffix))
    newFileName = pcm_file[:-4] + '.wav'
    pcmf = open(pcm_file, 'rb')
    pcmdata = pcmf.read()
    pcmf.close()
    if bits % 8 != 0:
        raise ValueError("bits % 8 must == 0. now bits:" + str(bits))
    wavfile = wave.open(newFileName, 'wb')
    wavfile.setnchannels(channels)
    wavfile.setsampwidth(bits // 8)
    wavfile.setframerate(sample_rate)
    wavfile.writeframes(pcmdata)
    wavfile.close()
    time.sleep(1)
    #os.remove(pcm_file)
    return newFileName


def get_data_array(filename):
    """

    """
    f = wave.open(filename, "rb")
    # 读取格式信息
    # 一次性返回所有的WAV文件的格式信息，它返回的是一个组元(tuple)：声道数, 量化位数（byte单位）, 采样频率, 采样点数, 压缩类型, 压缩类型的描述。wave模块只支持非压缩的数据，因此可以忽略最后两个信息
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    # 读取波形数据
    # 读取声音数据，传递一个参数指定需要读取的长度（以取样点为单位）
    str_data = f.readframes(nframes)
    f.close()
    return np.frombuffer(str_data, dtype=np.int16),framerate


if __name__ == '__main__':
    cle = r'E:\files\cle_malePolqaWB.wav'
    wav2pcm(cle)