
import ctypes
from ctypes import *
from algorithmLib.Function import project_root_path
from algorithmLib.formatConvert.wav_pcm import get_data_array

def resample(infile,target_amplerate):
    data,fs = get_data_array(infile)
    if fs == target_amplerate:
        return infile
    #uint64_t Resample_s16(const int16_t *input, int16_t *output, int inSampleRate, int outSampleRate, uint64_t inputSize,uint32_t channels)
    mydll = ctypes.windll.LoadLibrary(project_root_path() + 'algorithmLib/resample/resampler.dll')
    outfile = infile[:-4] +'_' +str(target_amplerate) + '.wav'
    infile_ref = c_char_p(bytes(infile.encode('utf-8')))
    outfile_ref = c_char_p(bytes(outfile.encode('utf-8')))
    mydll.resample2file(infile_ref,outfile_ref,target_amplerate)
    return outfile
    pass

if __name__ == '__main__':
    dst = r'E:\files\out8000.wav'
    sam = 8000
    print(resample(dst,sam))
