"""
:mod:`pybol.Manifest` --- Ship states
====================================

The :mod:`pybol.Manifest` allows streamlined movement of large sets of file structures (states).

.. autoclass:: Manifest
.. autoclass:: State

"""


import sys
import yaml
import os
import shutil
import logging 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PyBOL")
logger.info("Starting PyBOL logging")

class Manifest(object):
    """Tool for managing a multistate workflow. Requires a properly formatted
    manifest file; see example.
    """

    def __init__(self, filename=None):
        self._states = {}
        self._path = ''
        if filename:
            try:
                logger.info('Loading manifest file \'{}\''.format(filename))
                with open(filename, 'r') as f:
                    raw = yaml.safe_load(f)
                    self.path = raw.pop('path')
                logger.info('Loaded manifest file')
            except IOError as e:
                logger.error('Could not open file \'{}\''.format(filename))
                raise
            except KeyError as e:
                logger.error('No path provided. Check manifest file')
                raise
            logger.info('Building states')
            self._build_states(raw)
            logger.info('States built')
        else:
            logger.info('Creating empty manifest')
    
    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if not os.path.exists(path):
            logger.warning('Path \'{}\' does not exist'.format(path))
        self._path = path

    @property
    def states(self):
        return self._states

    @states.setter
    def states(self, states):
        if isinstance(states, dict):
            if len(states):
                for s in states:
                    if not isinstance(states[s], State):
                        logger.error('State dict can only contain state objects')
                        raise TypeError('State dict can only contain state objects')
                self._states = states
            else:
                self._states = {}
        else:
            logger.error('state attribute must be specified in a dict')
            raise TypeError('States must be held in a dict')

    def add_state(self, name, files=[], force=False, options=[]):

        if not name in self._states or force:
            self._states[name] = State(name, files=files, options=options)
        else:
            logger.error('State {} already exists'.format(name))

    def remove_state(self, name):
        try:
            logger.info('Removing state:', name)
            self._states.pop(name)
        except KeyError:
            logger.error('No state', name)

    def assemble(self, state, dest):
        """Builds the specified state.

        Keyword arguments:
        state -- a state from the manifest file.
        dest -- destination path.
        """
        logger.info('Assembling state \'{0}\' in \'{1}\''.format(state,dest))
        self.states[state].assemble(self.path, dest)
        logger.info('Assembled state \'{}\''.format(state))

    def _build_states(self, data):
        """Iterates through all states in the manifest file and populates the 
        states dictionary.

        Keyword arguments:
        data -- dictionary containing all of the state information.
        """
        for key in data:
            try:
                options = data[key]['options']
            except KeyError:
                options = []

            try:
                self.add_state(key, files=data[key]['files'], options=options)
            except TypeError:
                logger.error('Missing file list in state {}'.format(key))
                raise

    def __len__(self):
        return len(self.states)
                
                                                
class State(object):

    _files = []
    _name = ''

    def __init__(self, name, files=[], full_transfer=False, options=[]):
        self.name = name
        self._files = files
        self._full_transfer = full_transfer
        self._options = options

        self._option_dict = {full_transfer: False}

        if len(self._options) > 0:
            try:
                for o in self._options:
                    current_option = o
                    self._option_dict[o] = True
            except KeyError:
                logger.error('Unknown option: {}'.format(current_option))
                raise

            logger.info('Options are applied at assembly')
        

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, str):
            logger.info('Setting state name to {}'.format(name))
            self._name = name
        else:
            logger.error('Could not set state name. Must be a string')
            raise ValueError

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, files):
        self._files = files

    def clear_files(self):
        """Clears the files held in the state

        """
        del self.files[:]

    def assemble(self, src_path, dest):
        """Builds a state according to the information provided in the
        manifest file.

        Keyword arguments:
        src_path -- path containing all of the states.
        dest -- destination path. 

        """
        
        dirname = os.path.join(src_path, self.name)

        if len(self._options) > 0:
            if self._option_dict['full_transfer']:
                logger.info('Applying full transfer option to state {}'.format(self.name))
                self.files = os.listdir(dirname)
                self.files = [[x,x] for x in self.files] 
    
        for f in self.files:
            src_path_f = os.path.join(dirname, f[0])
            dest_f = os.path.join(dest, f[1])
            logger.info("Copying from {0} --> {1}".format(src_path_f,dest_f))
            if not os.path.exists(os.path.dirname(dest_f)):
                logger.info("Creating directory tree")
                os.makedirs(os.path.dirname(dest_f))
            
            if os.path.isdir(src_path_f):
                if os.path.exists(dest_f):
                    shutil.rmtree(dest_f)
                shutil.copytree(src_path_f,dest_f)
            else:
                shutil.copyfile(src_path_f, dest_f)

        logger.info("{0} build complete...".format(self.name))

    def __str__(self):
        return "{0} -- {1}".format(self.name, self.files)

    def __len__(self):
        return len(self.files)
