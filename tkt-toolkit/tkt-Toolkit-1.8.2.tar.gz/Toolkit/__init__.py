__title__ = 'tkt-Toolkit'
__author__ = 'Suprime'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020-2021 Suprime'
__version__ = '1.8.2'

import time,socket,json,os,piexif.helper
from . import TTA,Crypto,SpeechRecongition,texttospeech,translator, parse,tracking
from .errors import *
from win32com.client import Dispatch

here = os.path.dirname(os.path.abspath(__file__))

Tracking = tracking
Parse = parse
TTapi = TTA.TikTokApi

class SpeechRecognition:
    """
    Requires Pyaudio that you have to install
    using 'pipwin install pyaudio'.
    Records or reads audio and transforms it to text.
    Can also list Microphones.
    """
    def __init__(self,show_msg:bool=True):
        self.show_msg = show_msg
    def from_Microphone(self):
        return SpeechRecongition.recon.recon_from_mic(self.show_msg)
    def from_Wav_File(self,wav_file: str, show_msg: bool = True):
        open(wav_file)
        return SpeechRecongition.recon.recon_from_file(wav_file, show_msg)
    def list_Microphones(self):
        for EE in SpeechRecongition.recon.get_mics(self.show_msg): yield EE

class Toolkit:
    def __init__(self):
        self.active = True
        self.version = __version__
    class Crypto:
        """
        Uses the cryptography package and xor to
        encrypt/decrypt 'Text'. Encrypt returns a tuple
        """
        def __init__(self):
            self.active = True
            self.version = "1.1"
        def encrypt(self,Text:bytes):
            return Crypto.crypto.encrypt(Text)
        def decrypt(self,Text:bytes,Key:bytes):
            return Crypto.crypto.decrypt(Key,Text)
    def del_all(self,dir : str,log:bool=True):
        """
        Clears the folders and then deletes
        them, using os.listdir,os.remove,os.rmdir
        """
        parse.using.del_files(dir,log)
        parse.using.del_folders(dir,log)
        return None
    def getip(self):
        """
        Gets the users IP using the python
        built-in socket package.
        """
        return socket.gethostbyname(socket.gethostname())
    def texttospeech(self,Content:str, Lang:str, Axc:str="com",using_dir:str=''):
        """
        Creates a file in the 'using_dir' and
        plays it.
        """
        texttospeech.tts(Content,Axc,Lang,using_dir)
        return None
    def translate(self,Text:str,Dest,From='auto'):
        """
        Translate 'Text' from 'From' to 'Dest',
        set 'Dest' to "auto" if you don't know
        the language.

        Returns 2 values:
        1 : Translated Text
        2 : Tuple:
            1 : Text Language
            2 : Translated Language
            3 : Text
        """
        return translator.Translate(Text,Dest,From)
    def weather(self,city:str, key:str):
        """
        Gets the weather from openweathermap.org,
        uses the standard free to use api.
        """
        api_key = key
        uul = ("https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + api_key)
        url = uul
        response = parse.x.get(url).text
        data = json.loads(response)
        return data
    def get_color(self,rgb: tuple = None, hex: str = None):
        """
        Gets the color-data of one 'hex'/'rgb' color
        """
        if rgb == None and hex == None:
            raise ValueError('Not enough values.')
        elif not rgb == None and not hex == None:
            raise ValueError('Too many values.')
        elif not rgb == None and hex == None:
            R = 1
        elif rgb == None and not hex == None:
            R = 2
        else:
            raise InternalError
        if R == 1:
            req = parse.Q.build_main + parse.Q.build_rgb + str(rgb)
        elif R == 2:
            req = parse.Q.build_main + parse.Q.build_hex + str(hex.replace('#', '', 1))
        else:
            raise InternalError
        resp = (parse.x.get(req).text)
        return parse.using.pull_values(resp)
    def calc(self,calc):
        exec(f'global __COMP_CALC_END__\n__COMP_CALC_END__=({calc})')
        return __COMP_CALC_END__
    def do_for(self,n_seconds: int, func):
        """
        Runs 'func' for 'n_seconds'
        """
        t_end = time.time() + n_seconds
        while time.time() < t_end: func()
        return None
    def is_URLsafe(self,string: str, allowSub: bool = False):
        """
        Checks if 'string' is URL-safe, enable
        'allowSub' to not affect "/" characters.
        """
        for i in parse.Q.urlSafeChars:
            if i in string: return False
        if not allowSub:
            if "/" in string: return False
        return True
    def read_metadata(self,filename:str):
        exif_dict = piexif.load(filename)
        user_comment = piexif.helper.UserComment.load(exif_dict["Exif"][piexif.ExifIFD.UserComment])
        d = json.loads(user_comment)
        return d
    def write_metadata(self,filename:str,json_data:str):
        exif_dict = piexif.load(filename)
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(
            json.dumps(json_data),
            encoding="unicode"
        )
        piexif.insert(
            piexif.dump(exif_dict),
            filename
        )
        return None
    def create_shortcut(self,target:str,output:str):
        path = output
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = target
        shortcut.IconLocation = target
        shortcut.save()
        return None

tkt=Toolkit