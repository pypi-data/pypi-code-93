''' This package contains patching decorators for testing '''
from unittest.mock import patch
import importlib


def patch_modulify(module):
    ''' Patches the modulify from the module in the original class. '''
    def decorator(original_class):
        ''' Patched the modulify from the module in the original class. '''
        orig_setup = original_class.setUp

        # https://stackoverflow.com/a/37890916
        def new_setup(self, *args, **kwargs):
            ''' SetUp function for the tests '''
            # Do cleanup first so it is ready if an exception is raised
            def kill_patches():  # Create a cleanup callback that undoes our patches
                patch.stopall()  # Stops all patches started with start()
                importlib.reload(module)  # Reload our module which restores the original decorator
            # We want to make sure this is run so we do this in addCleanup instead of tearDown
            self.addCleanup(kill_patches)
            # Now patch the decorator where the decorator is being imported from
            # The lambda makes our decorator into a pass-thru. Also, don't forget to call start()
            patch('soil.modulify', lambda *x, **y: lambda f: f).start()
            # HINT: if you're patching a decor with params use something like:
            # lambda *x, **y: lambda f: f
            importlib.reload(module)  # Reloads the uut.py module which applies our patched decorator
            orig_setup(self, *args, **kwargs)
        original_class.setUp = new_setup
        return original_class
    return decorator
