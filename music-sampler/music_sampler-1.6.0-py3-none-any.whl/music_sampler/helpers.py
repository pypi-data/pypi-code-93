# -*- coding: utf-8 -*-
import argparse
import sys
import os
import math
import sounddevice as sd
import logging
import gettext
import yaml
gettext.install('music_sampler')
Logger = logging.getLogger("kivy")

from . import sysfont

class Config:
    pass

def find_font(name, style=sysfont.STYLE_NONE):
    if getattr(sys, 'frozen', False):
        font = sys._MEIPASS + "/fonts/{}_{}.ttf".format(name, style)
    else:
        font = sysfont.get_font(name, style=style)
        if font is not None:
            font = font[4]
    return font

def register_fonts():
    from kivy.core.text import LabelBase

    ubuntu_regular = find_font("Ubuntu", style=sysfont.STYLE_NORMAL)
    ubuntu_bold = find_font("Ubuntu", style=sysfont.STYLE_BOLD)
    symbola = find_font("Symbola")

    if ubuntu_regular is None:
        error_print("Font Ubuntu regular could not be found, "
                "please install it.", exit=True)
    if symbola is None:
        error_print("Font Symbola could not be found, please install it.",
                exit=True)
    if ubuntu_bold is None:
        warn_print("Font Ubuntu Bold could not be found.")

    LabelBase.register(name="Ubuntu",
            fn_regular=ubuntu_regular,
            fn_bold=ubuntu_bold)
    LabelBase.register(name="Symbola",
            fn_regular=symbola)


def path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS + "/"
    else:
        return os.path.dirname(os.path.realpath(__file__))


Configs = {
    'music_path': {
        'abbr': '-p',
        'default': '.',
        'help': _("Folder in which to find the music files"),
        'type': None
    },
    'latency': {
        'abbr': '-l',
        'default': 'high',
        'help': _("Latency: low, high or number of seconds"),
        'type': None
    },
    'language': {
        'abbr': '-L',
        'default': "fr",
        'help': _("Select another language"),
        'type': None
    },
    'device': {
        'abbr': '-d',
        'default': None,
        'help': _("Select this sound device"),
        'type': None
    },
    'blocksize': {
        'abbr': '-b',
        'default': 0,
        'help': _("Blocksize: If not 0, the number of frames to take\
                    at each step for the mixer"),
        'type': int
    },
    'frame_rate': {
        'abbr': '-f',
        'default': 44100,
        'help': _("Frame rate to play the musics"),
        'type': int
    },
    'channels': {
        'abbr': '-x',
        'default': 2,
        'help': _("Number of channels to use"),
        'type': int
    },
    'sample_width': {
        'abbr': '-s',
        'default': 2,
        'help': _("Sample width (number of bytes for each frame)"),
        'type': int
    },
    'builtin_mixing': {
        'default': False,
        'help_yes': _("Make the mixing of sounds manually\
                    (do it if the system cannot handle it correctly)"),
        'help_no': _("Don't make the mixing of sounds manually (default)"),
        'type': 'boolean'
    },
    'debug': {
        'abbr': '-d',
        'default': False,
        'help_yes': _("Print messages in console"),
        'help_no': _("Don't print messages in console (default)"),
        'type': 'boolean'
    },
    'focus_warning': {
        'default': True,
        'help_yes': _("Show a warning when focus is lost (default)"),
        'help_no': _("Don't show warning when focus is lost"),
        'type': 'boolean'
    },
    'load_all_musics': {
        'default': True,
        'help_yes': _("Load all the musics at launch time (default)"),
        'help_no': _("Don't load all the musics at launch time (use it if you \
            have memory problems)"),
        'type': 'boolean'
    },
    'list_devices': {
        'help': _("List available sound devices"),
        'type': 'action'
    },
}
Configs_order = [
    'debug',
    'music_path',
    'builtin_mixing',
    'latency',
    'blocksize',
    'frame_rate',
    'channels',
    'sample_width',
    'focus_warning',
    'language',
    'list_devices',
    'device',
    'load_all_musics',
]
def parse_args():
    argv = sys.argv[1 :]
    sys.argv = sys.argv[: 1]
    if "--" in argv:
        index = argv.index("--")
        kivy_args = argv[index+1 :]
        argv = argv[: index]

        sys.argv.extend(kivy_args)

    os.environ["KIVY_NO_CONFIG"] = 'true'
    sys.argv.extend(["-c", "kivy:log_level:warning"])
    sys.argv.extend(["-c", "kivy:log_dir:/tmp"])
    sys.argv.extend(["-c", "kivy:log_name:/tmp/music_sampler_%_.txt"])

    parser = argparse.ArgumentParser(
            argument_default=argparse.SUPPRESS,
            description=_("A Music Sampler application."))
    parser.add_argument("-V", "--version",
            action="version",
            help=_("Displays the current version and exits. Only use\
                    in bundled package"),
            version=show_version())
    parser.add_argument("-c", "--config",
            default="config.yml",
            required=False,
            help=_("Config file to load (default: config.yml)"))
    for argument in Configs_order:
        arg = Configs[argument]
        if arg['type'] != 'boolean' and arg['type'] != 'action':
            parser.add_argument(arg['abbr'], '--' + argument.replace('_', '-'),
                    type=arg['type'],
                    help=arg['help']+_(" (default: {})").format(arg['default']))
        elif arg['type'] == 'boolean':
            parser.add_argument('--' + argument.replace('_', '-'),
                    action='store_const', const=True,
                    help=arg['help_yes'])
            parser.add_argument('--no-' + argument.replace('_', '-'),
                    action='store_const', const=True,
                    help=arg['help_no'])
        else:
            parser.add_argument('--' + argument.replace('_', '-'),
                    action='store_const', const=True,
                    help=arg['help'])
    parser.add_argument('--',
            dest="args",
            help=_("Kivy arguments. All arguments after this are interpreted\
                    by Kivy. Pass \"-- --help\" to get Kivy's usage."))

    args = parser.parse_args(argv)

    Config.yml_file = args.config
    build_config(args)

    if Config.device is not None:
        sd.default.device = Config.device

    if Config.list_devices:
        print(sd.query_devices())
        sys.exit()

    if Config.debug:
        sys.argv.extend(["-c", "kivy:log_level:debug"])

    if Config.language != 'en':
        gettext.translation("music_sampler",
                localedir=path() + '/locales',
                languages=[Config.language]).install()
    if not Config.music_path.endswith("/"):
        Config.music_path = Config.music_path + "/"

def dump_config():
    max_size = max(max(map(len, Configs_order)), len('config'))
    info_print("{:<{}} : {}".format(
        "config", max_size, Config.yml_file))
    for item in Config.__dict__:
        if item in Configs_order:
            info_print("{:<{}} : {}".format(
                item, max_size, getattr(Config, item)))

def build_config(args):
    stream = open(Config.yml_file, "r", encoding='utf8')
    try:
        config = yaml.safe_load(stream)
    except Exception as e:
        error_print("Error while loading config file: {}".format(e))
        config = {}
    stream.close()
    if 'config' in config:
        config = config['config']
    else:
        config = {}

    for config_item in Configs_order:
        if Configs[config_item]['type'] != 'boolean' and \
                Configs[config_item]['type'] != 'action':
            t = Configs[config_item]['type'] or str
            if hasattr(args, config_item):
                setattr(Config, config_item, getattr(args, config_item))
            elif config_item in config:
                setattr(Config, config_item, t(config[config_item]))
            else:
                setattr(Config, config_item, Configs[config_item]['default'])
        elif Configs[config_item]['type'] == 'boolean':
            if hasattr(args, 'no_' + config_item) or hasattr(args, config_item):
                setattr(Config, config_item, hasattr(args, config_item))
            elif config_item in config:
                setattr(Config, config_item, config[config_item])
            else:
                setattr(Config, config_item, Configs[config_item]['default'])
        else:
            setattr(Config, config_item, hasattr(args, config_item))


def show_version():
    if getattr(sys, 'frozen', False):
        with open(path() + ".pyinstaller_commit", "r") as f:
            return f.read()
    else:
        return _("option '-V' can only be used in bundled package")

def duration_to_min_sec(duration):
    minutes = int(duration / 60)
    seconds = int(duration) % 60
    if minutes < 100:
        return "{:2}:{:0>2}".format(minutes, seconds)
    else:
        return "{}:{:0>2}".format(minutes, seconds)

def gain(volume, old_volume=None):
    if old_volume is None:
        return 20 * math.log10(max(volume, 0.1) / 100)
    else:
        return [
                20 * math.log10(max(volume, 0.1) / max(old_volume, 0.1)),
                max(volume, 0)]

def debug_print(message, with_trace=None):
    if with_trace is None:
        with_trace = (Logger.getEffectiveLevel() < logging.WARN)
    with_trace &= (sys.exc_info()[0] is not None)

    Logger.debug('MusicSampler: ' + message, exc_info=with_trace)

def error_print(message, exit=False, with_trace=None):
    if with_trace is None:
        with_trace = (Logger.getEffectiveLevel() < logging.WARN)
    with_trace &= (sys.exc_info()[0] is not None)

    # FIXME: handle it correctly when in a thread
    if exit:
        Logger.critical('MusicSampler: ' + message, exc_info=with_trace)
        sys.exit(1)
    else:
        Logger.error('MusicSampler: ' + message, exc_info=with_trace)

def warn_print(message, with_trace=None):
    if with_trace is None:
        with_trace = (Logger.getEffectiveLevel() < logging.WARN)
    with_trace &= (sys.exc_info()[0] is not None)

    Logger.warn('MusicSampler: ' + message, exc_info=with_trace)

def info_print(message, with_trace=None):
    if with_trace is None:
        with_trace = (Logger.getEffectiveLevel() < logging.WARN)
    with_trace &= (sys.exc_info()[0] is not None)

    Logger.info('MusicSampler: ' + message, exc_info=with_trace)

