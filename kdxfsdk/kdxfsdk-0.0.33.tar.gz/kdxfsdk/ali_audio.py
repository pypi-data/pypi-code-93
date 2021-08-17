# -*- coding:utf-8 -*-
from __future__ import print_function

import os
from snowboy import snowboydecoder
from robot import utils, Player, constants, logging

logger = logging.getLogger(__name__)


class Audio(object):
    def __init__(self):
        self.interrupted = False
        self.record_file = ""

    def detected_callback(self):
        def start_record():
            utils.setRecordable(True)
            logger.info('开始录音')

        # first disable audio record.
        utils.setRecordable(False)
        # no after player played the startup beep.
        Player.play(constants.getData('beep_hi.wav'), onCompleted=start_record, wait=True)

    def audioRecorderCallback(self, fname):
        self.interrupted = True
        self.record_file = fname

    def _interrupt_callback(self):
        return self.interrupted

    def start_record(self):
        detector = snowboydecoder.HotwordDetector("/tmp/snowboy/resources/zijinshan.pmdl", sensitivity=0.5, audio_gain=1)
        detector.start(detected_callback=self.detected_callback,
                       audio_recorder_callback=self.audioRecorderCallback,
                       interrupt_check=self._interrupt_callback,
                       )
        return self.record_file

    # 这个其实是wav，为了跟之前的接口保持一致。
    def play(self, file_name):
        Player.play(file_name, wait=True)

    def wav_to_pcm(self, wav_file):
        pcm_file = "%s.pcm" % (wav_file.split(".")[0])
        os.system("ffmpeg -y  -i %s  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 %s" % (
            wav_file, pcm_file))
        return pcm_file
    #
    # def play_pcm(self, pcm_file):
    #     # os.close(sys.stderr.fileno())
    #     with open(pcm_file, 'rb') as pcmfile:
    #         pcmdata = pcmfile.read()
    #     with wave.open('speach.wav', 'wb') as wavfile:
    #         wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
    #         wavfile.writeframes(pcmdata)
    #     self.play_wav('speach.wav')


if __name__ == "__main__":
    audio = Audio()
    filename = audio.start_record()
    print(filename)
