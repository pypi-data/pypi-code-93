from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.core.window import Window
from kivy.clock import Clock

import threading
import yaml
import sys
import copy
from collections import defaultdict

from transitions.extensions import HierarchicalMachine as Machine

from .music_file import MusicFile
from .mixer import Mixer
from .helpers import Config, gain, error_print, warn_print
from .action import Action

class Mapping(RelativeLayout):
    STATES = [
        'initial',
        'configuring',
        'configured',
        'loading',
        'loaded'
    ]

    TRANSITIONS = [
        {
            'trigger': 'configure',
            'source': 'initial',
            'dest': 'configuring'
        },
        {
            'trigger': 'success',
            'source': 'configuring',
            'dest': 'configured',
            'after': 'load'
        },
        {
            'trigger': 'load',
            'source': 'configured',
            'dest': 'loading'
        },
        {
            'trigger': 'success',
            'source': 'loading',
            'dest': 'loaded'
        },
        {
            'trigger': 'reload',
            'source': 'loaded',
            'dest': 'configuring'
        }
    ]

    master_volume = NumericProperty(100)
    ready_color = ListProperty([1, 165/255, 0, 1])
    state = StringProperty("")

    def __init__(self, **kwargs):
        self.keys = []
        self.running = []
        self.wait_ids = {}
        self.open_files = {}
        self.is_leaving_application = False

        Machine(model=self, states=self.STATES,
                transitions=self.TRANSITIONS, initial='initial',
                auto_transitions=False, queued=True)
        super(Mapping, self).__init__(**kwargs)
        self.keyboard = Window.request_keyboard(self.on_keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keyboard_down)

        self.configure(initial=True)

    def on_enter_configuring(self, initial=True):
        if Config.builtin_mixing:
            self.mixer = Mixer()
        else:
            self.mixer = None

        try:
            self.key_config, self.open_files = self.parse_config()
        except Exception as e:
            error_print("Error while loading configuration: {}".format(e),
                    with_trace=False, exit=initial)

        self.success()

    def on_enter_loading(self):
        for key in self.keys:
            key.reload()
        self.success()

    # Kivy events
    def add_widget(self, widget, index=0):
        if type(widget).__name__ == "Key" and widget not in self.keys:
            self.keys.append(widget)
        return super(Mapping, self).add_widget(widget, index)

    def remove_widget(self, widget, index=0):
        if type(widget).__name__ == "Key" and widget in self.keys:
            self.keys.remove(widget)
        return super(Mapping, self).remove_widget(widget, index)

    def on_keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = self.find_by_key_code(keycode)
        if self.allowed_modifiers(modifiers) and key is not None:
            modifiers.sort()
            threading.Thread(name="MSKeyAction", target=key.run,
                    args=['-'.join(modifiers)]).start()
        elif 'ctrl' in modifiers and (keycode[0] == 113 or keycode[0] == '99'):
            self.leave_application()
            sys.exit()
        elif 'ctrl' in modifiers and keycode[0] == 114 and self.is_loaded():
            self.reload(initial=False)
        return True

    def leave_application(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.stop_all_running()
        self.is_leaving_application = True
        for music in self.open_files.values():
            music.stop()
        for thread in threading.enumerate():
            if thread.getName()[0:2] == "MS":
                thread.join()
            elif thread.__class__ == threading.Timer:
                thread.cancel()
                thread.join()

    # Helpers
    def allowed_modifiers(self, modifiers):
        allowed = []
        return len([a for a in modifiers if a not in allowed]) == 0

    def find_by_key_code(self, key_code):
        if "Key_" + str(key_code[0]) in self.ids:
            return self.ids["Key_" + str(key_code[0])]
        return None

    def all_keys_ready(self):
        partial = False
        for key in self.keys:
            if not key.is_loaded_or_failed():
                return "not_ready"
            partial = partial or key.is_failed()

        if partial:
            return "partial"
        else:
            return "success"

    # Callbacks
    def key_loaded_callback(self):
        if hasattr(self, 'finished_loading'):
            return

        opacity = int(Config.load_all_musics)

        result = self.all_keys_ready()
        if result == "success":
            self.ready_color = [0, 1, 0, opacity]
            self.finished_loading = True
        elif result == "partial":
            self.ready_color = [1, 0, 0, opacity]
            self.finished_loading = True
        else:
            self.ready_color = [1, 165/255, 0, opacity]

    ## Some global actions
    def stop_all_running(self, except_key=None, key_start_time=0):
        running = self.running
        self.running = [r for r in running\
                if r[0] == except_key and r[1] == key_start_time]
        for (key, start_time) in running:
            if (key, start_time) != (except_key, key_start_time):
                key.interrupt()

    # Master volume methods
    @property
    def master_gain(self):
        return gain(self.master_volume)

    def set_master_volume(self, value, delta=False, fade=0):
        [db_gain, self.master_volume] = gain(
                value + int(delta) * self.master_volume,
                self.master_volume)

        for music in self.open_files.values():
            music.set_gain_with_effect(db_gain, fade=fade)

    # Wait handler methods
    def add_wait(self, action_or_wait, wait_id=None):
        if wait_id is not None:
            self.wait_ids[wait_id] = [action_or_wait]
        else:
            if None not in self.wait_ids:
                self.wait_ids[None] = []
            self.wait_ids[None].append(action_or_wait)

    def matching_wait_ids(self, wait_id=None):
        if wait_id is None:
            matching_ids = list(self.wait_ids.keys())
        elif wait_id in self.wait_ids:
            matching_ids = [wait_id]
        else:
            matching_ids = []
        return matching_ids

    def interrupt_wait(self, wait_id=None):
        for _wait_id in self.matching_wait_ids(wait_id=wait_id):
            action_or_waits = self.wait_ids[_wait_id]
            del(self.wait_ids[_wait_id])
            for action_or_wait in action_or_waits:
                if isinstance(action_or_wait, Action):
                    action_or_wait.interrupt()
                else:
                    action_or_wait.set()

    def pause_wait(self, wait_id=None):
        for _wait_id in self.matching_wait_ids(wait_id=wait_id):
            action_or_waits = self.wait_ids[_wait_id]
            for action_or_wait in action_or_waits:
                if isinstance(action_or_wait, Action):
                    action_or_wait.pause()

    def unpause_wait(self, wait_id=None):
        for _wait_id in self.matching_wait_ids(wait_id=wait_id):
            action_or_waits = self.wait_ids[_wait_id]
            for action_or_wait in action_or_waits:
                if isinstance(action_or_wait, Action):
                    action_or_wait.unpause()

    def reset_wait(self, wait_id=None):
        for _wait_id in self.matching_wait_ids(wait_id=wait_id):
            action_or_waits = self.wait_ids[_wait_id]
            for action_or_wait in action_or_waits:
                if isinstance(action_or_wait, Action):
                    action_or_wait.reset()

    # Methods to control running keys
    def start_running(self, key, start_time):
        self.running.append((key, start_time))

    def keep_running(self, key, start_time):
        return (key, start_time) in self.running

    def finished_running(self, key, start_time):
        if (key, start_time) in self.running:
            self.running.remove((key, start_time))

    # YML config parser
    def parse_config(self):
        def update_alias(prop_hash, aliases, key):
            if isinstance(aliases[key], dict):
                for alias in aliases[key]:
                    prop_hash.setdefault(alias, aliases[key][alias])
            else:
                warn_print("Alias {} is not a hash, ignored".format(key))

        def include_aliases(prop_hash, aliases):
            if 'include' not in prop_hash:
                return

            included = prop_hash['include']
            del(prop_hash['include'])
            if isinstance(included, str):
                update_alias(prop_hash, aliases, included)
            elif isinstance(included, list):
                for included_ in included:
                    if isinstance(included_, str):
                        update_alias(prop_hash, aliases, included_)
                    else:
                        warn_print("Unkown alias include type, ignored: "
                            "{} in {}".format(included_, included))
            else:
                warn_print("Unkown alias include type, ignored: {}"
                        .format(included))

        def check_key_property(key_property, key):
            if 'description' in key_property:
                desc = key_property['description']
                if not isinstance(desc, list):
                    warn_print("description in key_property '{}' is not "
                            "a list, ignored".format(key))
                    del(key_property['description'])
            if 'color' in key_property:
                color = key_property['color']
                if not isinstance(color, list)\
                        or len(color) != 3\
                        or not all(isinstance(item, int) for item in color)\
                        or any(item < 0 or item > 255 for item in color):
                    warn_print("color in key_property '{}' is not "
                            "a list of 3 valid integers, ignored".format(key))
                    del(key_property['color'])

        def check_key_properties(config):
            if 'key_properties' in config:
                if isinstance(config['key_properties'], dict):
                    return config['key_properties']
                else:
                    warn_print("key_properties config is not a hash, ignored")
                    return {}
            else:
                return {}

        def check_mapped_keys(config):
            if 'keys' in config:
                if isinstance(config['keys'], dict):
                    return config['keys']
                else:
                    warn_print("keys config is not a hash, ignored")
                    return {}
            else:
                return {}

        def check_mapped_key(actions, key):
            if not isinstance(actions, list):
                warn_print("key config '{}' is not an array, ignored"
                        .format(key))
                return []
            else:
                return actions

        def append_actions_to_key(mapped_key, actions, aliases, seen_files, music_properties, key_properties):
            for index, action in enumerate(check_mapped_key(actions, mapped_key)):
                if not isinstance(action, dict) or\
                        not len(action) == 1 or\
                        not isinstance(list(action.values())[0] or {}, dict):
                    warn_print("action number {} of key '{}' is invalid, "
                            "ignored".format(index + 1, mapped_key))
                    continue
                append_action_to_key(action, mapped_key, aliases, seen_files, music_properties, key_properties)

        def append_action_to_key(action, mapped_key, aliases, seen_files, music_properties, key_properties):
            action_name = list(action)[0]
            action_args = {}
            if action[action_name] is None:
                action[action_name] = {}

            include_aliases(action[action_name], aliases)

            for argument in action[action_name]:
                if argument == 'file':
                    filename = str(action[action_name]['file'])
                    if filename not in seen_files:
                        music_property = check_music_property(
                                music_properties[filename],
                                filename)

                        if filename in self.open_files:
                            self.open_files[filename]\
                                    .reload_properties(**music_property)

                            seen_files[filename] =\
                                    self.open_files[filename]
                        else:
                            seen_files[filename] = MusicFile(
                                    filename, self, **music_property)

                    if filename not in key_properties[mapped_key]['files']:
                        key_properties[mapped_key]['files'] \
                                .append(seen_files[filename])

                    action_args['music'] = seen_files[filename]
                else:
                    action_args[argument] = action[action_name][argument]

            key_properties[mapped_key]['actions'] \
                    .append([action_name, action_args])

        def check_music_property(music_property, filename):
            if not isinstance(music_property, dict):
                warn_print("music_property config '{}' is not a hash, ignored"
                        .format(filename))
                return {}
            if 'name' in music_property:
                music_property['name'] = str(music_property['name'])
            if 'gain' in music_property:
                try:
                    music_property['gain'] = float(music_property['gain'])
                except ValueError as e:
                    del(music_property['gain'])
                    warn_print("gain for music_property '{}' is not "
                            "a float, ignored".format(filename))
            return music_property

        stream = open(Config.yml_file, "r", encoding='utf8')
        try:
            config = yaml.safe_load(stream)
        except Exception as e:
            raise Exception("Error while loading config file: {}".format(e)) from e
        stream.close()

        if not isinstance(config, dict):
            raise Exception("Top level config is supposed to be a hash")

        if 'aliases' in config and isinstance(config['aliases'], dict):
            aliases = config['aliases']
        else:
            aliases = defaultdict(dict)
            if 'aliases' in config:
                warn_print("aliases config is not a hash, ignored")

        music_properties = defaultdict(dict)
        if 'music_properties' in config and\
                isinstance(config['music_properties'], dict):
            music_properties.update(config['music_properties'])
        elif 'music_properties' in config:
            warn_print("music_properties config is not a hash, ignored")

        seen_files = {}

        common_key_properties = {}
        if 'common' in config['key_properties'] and\
                isinstance(config['key_properties'], dict):
            common_key_properties = config['key_properties']['common']
            include_aliases(common_key_properties, aliases)
            check_key_property(common_key_properties, 'common')
        elif 'common' in config['key_properties']:
            warn_print("'common' key in key_properties is not a hash, ignored")

        key_properties = defaultdict(lambda: {
                "actions":    [],
                "properties": copy.deepcopy(common_key_properties),
                "files":      []
            })

        for key in check_key_properties(config):
            if key == 'common':
                continue

            key_prop = config['key_properties'][key]

            if not isinstance(key_prop, dict):
                warn_print("key_property '{}' is not a hash, ignored"
                        .format(key))
                continue

            include_aliases(key_prop, aliases)
            check_key_property(key_prop, key)

            key_properties[key]["properties"].update(key_prop)
            if 'actions' in key_prop:
                append_actions_to_key(key, key_prop['actions'], aliases, seen_files, music_properties, key_properties)

        for mapped_key in check_mapped_keys(config):
            append_actions_to_key(mapped_key, config['keys'][mapped_key], aliases, seen_files, music_properties, key_properties)

        return (key_properties, seen_files)


