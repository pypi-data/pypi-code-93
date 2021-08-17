# -*- coding:utf-8 -*-
#!/usr/bin/env python

## recordtest.py
##
## This is an example of a simple sound capture script.
##
## The script opens an ALSA pcm device for sound capture, sets
## various attributes of the capture, and reads in a loop,
## writing the data to standard out.
##
## To test it out do the following:
## python recordtest.py out.raw # talk to the microphone
## aplay -r 8000 -f S16_LE -c 1 out.raw

#!/usr/bin/env python

from __future__ import print_function

import sys
import time
import getopt
import wave
import alsaaudio
import numpy as np

def usage():
    print('usage: recordtest.py [-d <device>] <file>', file=sys.stderr)
    sys.exit(2)


if __name__ == '__main__':

    device = 'default'

    opts, args = getopt.getopt(sys.argv[1:], 'd:')
    for o, a in opts:
        if o == '-d':
            device = a

    if not args:
        usage()

    f = wave.open(args[0], 'wb')

    # Open the device in nonblocking capture mode. The last argument could
    # just as well have been zero for blocking mode. Then we could have
    # left out the sleep call in the bottom of the loop
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, device=device)

    # Set attributes: Mono, 44100 Hz, 16 bit little endian samples
    inp.setchannels(1)
    inp.setrate(16000)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

    f.setnchannels(1)
    f.setsampwidth(2)    #PCM_FORMAT_S16_LE
    f.setframerate(16000)


    print('%d channels, %d sampling rate\n' % (f.getnchannels(),
                                               f.getframerate()))
    # The period size controls the internal number of frames per period.
    # The significance of this parameter is documented in the ALSA api.
    # For our purposes, it is suficcient to know that reads from the device
    # will return this many frames. Each frame being 2 bytes long.
    # This means that the reads below will return either 320 bytes of data
    # or 0 bytes of data. The latter is possible because we are in nonblocking
    # mode.
    inp.setperiodsize(160)

    # loops = 1000000
    # while loops > 0:
    #     loops -= 1
    #     # Read data from device
    #     l, data = inp.read()
    #
    #     if l:
    #         f.writeframes(data)
    #         time.sleep(.001)
    recording = False
    frames = []
    THRESHOLD = 1000
    # 遗弃前12帧
    for i in range(0, 5):
        l, data = inp.read()
        time.sleep(.051)

    while (True):
        if not recording:
            print('检测中... ')
            # 采集小段声音
            frames = []
            for i in range(0, 4):
                l, data = inp.read()
                if l > 0:
                    time.sleep(.01)
                    print("some sound ")
                    frames.append(data)
                    a = np.fromstring(data, dtype='int16')
                    print(np.abs(a).mean())
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            large_sample_count = np.sum(audio_data >= THRESHOLD * 0.6)
            time.sleep(.051)
            # 如果有符合条件的声音，则开始录制
            if large_sample_count >= THRESHOLD * 0.8:
                print("检测到信号")
                recording = True
            print(large_sample_count)
        else:
            nowavenum = 0
            while True:
                print("持续录音中...")
                subframes = []
                for i in range(0, 5):
                    l, data = inp.read()
                    if l > 0:
                        time.sleep(.001)
                        subframes.append(data)
                        frames.append(data)
                        a = np.fromstring(data, dtype='int16')
                        print(np.abs(a).mean())
                audio_data = np.frombuffer(b''.join(subframes), dtype=np.int16)
                if audio_data.size != 0:
                    temp = np.max(audio_data)
                    if temp <= THRESHOLD * 0.8:
                        nowavenum += 1
                    else:
                        nowavenum = 0

                    if nowavenum >= 2:
                        print("等待超时，开始保存")
                        frames.pop()
                        f.writeframes(b''.join(frames))
                        f.close()
                        break
            break
