from transitions.extensions import HierarchicalMachine as Machine
from .helpers import debug_print, error_print
from . import actions

class Action:
    STATES = [
        'initial',
        'loading',
        'failed',
        {
            'name': 'loaded',
            'children': ['stopped', 'running']
        },
        'destroyed'
    ]

    TRANSITIONS = [
        {
            'trigger': 'load',
            'source': 'initial',
            'dest': 'loading'
        },
        {
            'trigger': 'fail',
            'source': ['loading', 'loaded'],
            'dest': 'failed',
        },
        {
            'trigger': 'success',
            'source': 'loading',
            'dest': 'loaded_stopped',
        },
        {
            'trigger': 'reload',
            'source': 'loaded',
            'dest': 'loading',
        },
        {
            'trigger': 'run',
            'source': 'loaded_stopped',
            'dest': 'loaded_running',
            'after': 'finish_action',
        },
        {
            'trigger': 'finish_action',
            'source': 'loaded_running',
            'dest': 'loaded_stopped'
        },
        {
            'trigger': 'destroy',
            'source': '*',
            'dest': 'destroyed'
        }
    ]

    def __init__(self, action, key, **kwargs):
        Machine(model=self, states=self.STATES,
                transitions=self.TRANSITIONS, initial='initial',
                ignore_invalid_triggers=True, queued=True,
                after_state_change=self.notify_state_change)

        self.action = action
        self.key = key
        self.mapping = key.parent
        self.arguments = kwargs
        self.sleep_event = None
        self.waiting_music = None

    def is_loaded_or_failed(self):
        return self.is_loaded(allow_substates=True) or self.is_failed()

    def callback_music_state(self, new_state):
        # If a music gets unloaded while the action is loaded_running and
        # depending on the music, it won't be able to do the finish_action.
        # Can that happen?
        # a: play 'mp3';
        # z: wait 'mp3';
        # e: pause 'mp3';
        # r: stop 'mp3'; unload_music 'mp3'
        if new_state == 'failed':
            self.fail()
        elif self.is_loaded(allow_substates=True) and\
                new_state in ['initial', 'loading']:
            self.reload(reloading=True)
        elif self.is_loading() and new_state.startswith('loaded_'):
            self.success()

    # Machine states / events
    def on_enter_loading(self, reloading=False):
        if reloading:
            return
        if hasattr(actions, self.action):
            if 'music' in self.arguments and\
                    self.action not in ['unload_music', 'load_music']:
                self.arguments['music'].subscribe_state_change(
                        self.callback_music_state)
            else:
                self.success()
        else:
            error_print("Unknown action {}".format(self.action))
            self.fail()

    def on_enter_loaded_running(self, key_start_time):
        debug_print(self.description())
        if hasattr(actions, self.action):
            getattr(actions, self.action).run(self,
                    key_start_time=key_start_time, **self.arguments)

    def on_enter_destroyed(self):
        if 'music' in self.arguments:
            self.arguments['music'].unsubscribe_state_change(
                    self.callback_music_state)

    def notify_state_change(self, *args, **kwargs):
        self.key.callback_action_state_changed()

    # This one cannot be in the Machine state since it would be queued to run
    # *after* the wait is ended...
    def interrupt(self):
        if getattr(actions, self.action, None) and\
                hasattr(getattr(actions, self.action), 'interrupt'):
            return getattr(getattr(actions, self.action), 'interrupt')(
                    self, **self.arguments)

    def pause(self):
        if getattr(actions, self.action, None) and\
                hasattr(getattr(actions, self.action), 'pause'):
            return getattr(getattr(actions, self.action), 'pause')(
                    self, **self.arguments)

    def unpause(self):
        if getattr(actions, self.action, None) and\
                hasattr(getattr(actions, self.action), 'unpause'):
            return getattr(getattr(actions, self.action), 'unpause')(
                    self, **self.arguments)

    def reset(self):
        if getattr(actions, self.action, None) and\
                hasattr(getattr(actions, self.action), 'reset'):
            return getattr(getattr(actions, self.action), 'reset')(
                    self, **self.arguments)

    # Helpers
    def music_list(self, music):
        if music is not None:
            return [music]
        else:
            return self.mapping.open_files.values()

    def description(self):
        if hasattr(actions, self.action):
            return getattr(actions, self.action)\
                    .description(self, **self.arguments)
        else:
            return _("unknown action {}").format(self.action)
