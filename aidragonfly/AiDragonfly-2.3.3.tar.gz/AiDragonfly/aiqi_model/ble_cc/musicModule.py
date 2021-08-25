#! /usr/bin/env python
# -*- coding: utf-8 -*-

# import asyncio
# from AiDragonfly import df
# from AiDragonfly import constantModule

# import asyncio
# from . import df
# from . import constantModule

import asyncio
import AiDragonfly.aiqi_main as df
import AiDragonfly.aiqi_model.ble_cc.constantModule as constantModule

_version = 0
def sound(sound): #主控一般音效
    protocol = [0x55, 0x02, 0x02, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
    protocol[4] = sound
    xor = df._data_xor_check(protocol[0:-1])
    protocol[-2] = xor
    loop = asyncio.get_event_loop()
    loop.run_until_complete(df.sendDate(protocol,df.ONEBOT))


class musical_instruments_manage(object): #主控音效管理类
    def _set_data(self,index_number,scale,channel):
        midi_protocol = [0x55, 0x03, 0x01, 0x01, 0x00, 0x00, 0x7F, 0x00, 0x00, 0x00, 0x00
            , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
        midi_protocol[4] = index_number
        midi_protocol[5] = scale
        midi_protocol[7] = channel
        xor = df._data_xor_check(midi_protocol[0:-1])
        midi_protocol[-2] = xor
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.sendDate(midi_protocol, df.ONEBOT))

    def piano(self,midi,channel):
        if channel == 9 or channel > 15 or channel < 0:
            print('Data Range Error')
            print('channel:[0 ~ 8]、[10 ~ 15]')
            return
        self._set_data(constantModule.INSTRUMENTS_PIANO, midi, channel)

    def music_box(self,midi,channel):
        if channel == 9 or channel > 15 or channel < 0:
            print('Data Range Error')
            print('channel:[0 ~ 8]、[10 ~ 15]')
            return
        self._set_data(constantModule.INSTRUMENTS_MUSIC_BOX, midi, channel)

    def bass(self,midi,channel):
        if channel == 9 or channel > 15 or channel<0:
            print('Data Range Error')
            print('channel:[0 ~ 8]、[10 ~ 15]')
            return
        self._set_data(constantModule.INSTRUMENTS_BASS, midi, channel)

    def guitar(self,midi,channel):
        if channel == 9 or channel > 15 or channel < 0:
            print('Data Range Error')
            print('channel:[0 ~ 8]、[10 ~ 15]')
            return
        self._set_data(constantModule.INSTRUMENTS_GUITAR, midi, channel)

    def saxophone(self,midi,channel):
        if channel == 9 or channel > 15 or channel < 0:
            print('Data Range Error')
            print('channel:[0 ~ 8]、[10 ~ 15]')
            return
        self._set_data(constantModule.INSTRUMENTS_SAXOPHONE, midi, channel)

    def flute(self,midi,channel):
        if channel == 9 or channel > 15 or channel < 0:
            print('Data Range Error')
            print('channel:[0 ~ 8]、[10 ~ 15]')
            return
        self._set_data(constantModule.INSTRUMENTS_FLUTE, midi, channel)

    def xylophone(self,midi,channel):
        if channel == 9 or channel > 15 or channel < 0:
            print('Data Range Error')
            print('channel:[0 ~ 8]、[10 ~ 15]')
            return
        self._set_data(constantModule.INSTRUMENTS_XYLOPHONE, midi, channel)

    def violin(self,midi,channel):
        if channel == 9 or channel > 15 or channel < 0:
            print('Data Range Error')
            print('channel:[0 ~ 8]、[10 ~ 15]')
            return
        self._set_data(constantModule.INSTRUMENTS_VIOLIN, midi, channel)

    def harp(self,midi,channel):
        if channel == 9 or channel > 15 or channel < 0:
            print('Data Range Error')
            print('channel:[0 ~ 8]、[10 ~ 15]')
            return
        self._set_data(constantModule.INSTRUMENTS_HARP, midi, channel)

    def percussion(self,percussion):
        self._set_data(constantModule.INSTRUMENTS_PERCUSSION, percussion, 9)


midi = musical_instruments_manage()


def set_volume(volume): #设置主控音量大小
    volume_protocol = [0x55, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]
    if volume > 12 or volume < 0:
        print('Data Range Error')
        print('volume:[0 ~ 12]')
        return
    volume_protocol[4] = volume
    xor = df._data_xor_check(volume_protocol[0:-1])
    volume_protocol[-2] = xor
    loop = asyncio.get_event_loop()
    loop.run_until_complete(df.sendDate(volume_protocol, df.ONEBOT))


def set_record(record): #设置主控录音
    global _version
    recording_protocol = [0x55, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        , 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA]

    if _version >= 517:
        if record == constantModule.RECORD_START:
            print('\033[1;31m Please start recording,supports up to 80 seconds of recording \033[0m')
        elif record == constantModule.RECORD_PLAY:
            print('\033[1;31m The recording starts playing \033[0m')
        elif record == constantModule.RECORD_END:
            print('\033[1;31m End of the recording \033[0m')

        recording_protocol[4] = record
        xor = df._data_xor_check(recording_protocol[0:-1])
        recording_protocol[-2] = xor
        loop = asyncio.get_event_loop()
        loop.run_until_complete(df.sendDate(recording_protocol, df.ONEBOT))
    else:
        print('\033[1;31m Please update the firmware to the latest version \033[0m')



