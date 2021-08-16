import codefast as cf
from codefast.argparser import ArgParser


class Audios:
    def __init__(self):
        stereo_mp3 = 'https://mgvai-conversation.oss-cn-zhangjiakou.aliyuncs.com/backend/41.mp3'
        mono_mp3 = 'https://mgvai-conversation.oss-cn-zhangjiakou.aliyuncs.com/backend/41_left.mp3'
        mono_wav = 'https://mgvai-conversation.oss-cn-zhangjiakou.aliyuncs.com/backend/41_left.wav'
        mono_tiejia = 'https://megaview.oss-cn-zhangjiakou.aliyuncs.com/videos/18_ab05cb47515d3756862485b3b8f1ebb1.wav'
        stereo_iterget = 'https://megaview.oss-cn-zhangjiakou.aliyuncs.com/videos/15_6cff9a511e8cf3609a64b2bb8eb4548b.mp3'
        for _type, _url in [('stereo', stereo_mp3), ('mono', mono_mp3),
                            ('mono', mono_wav), ('stereo-iterget', stereo_iterget),
                            ('mono-tiejia', mono_tiejia)]:
            print('{:<20} {:<10}'.format(_type, _url))

    def __call__(self):
        ...


def entry():
    ap = ArgParser()
    ap.input('-ad',
             '-audio',
             sub_args=[],
             description='Display audio demos. Usage: demo -audio')
    ap.parse()

    if ap.audio:
        Audios()

    else:
        ap.help()
