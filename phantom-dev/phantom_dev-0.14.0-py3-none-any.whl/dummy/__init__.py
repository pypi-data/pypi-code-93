import sys
from functools import wraps

from . import phantom as dummy_phantom


class MockedPhantomModule:
	MODULE_NAME = 'phantom'

	def __init__(self, force=False):
		self.force = force
		self.old_module = None

	def __enter__(self):
		self.old_module = sys.modules.get(self.MODULE_NAME)
		if self.old_module is None or self.force:
			sys.modules[self.MODULE_NAME] = dummy_phantom

		return sys.modules[self.MODULE_NAME]

	def __exit__(self, *args, **kwargs):
		current_module = sys.modules.get(self.MODULE_NAME)
		if current_module is not dummy_phantom:
			return

		if self.old_module is None:
			sys.modules.pop(self.MODULE_NAME)
		else:
			sys.modules[self.MODULE_NAME] = self.old_module


class PatchedPath:
	def __init__(self, path):
		self.path = str(path)
		self.added = False

	def __enter__(self):
		if self.path in sys.path:
			return

		sys.path.insert(0, self.path)
		self.added = True

	def __exit__(self, *args, **kwargs):
		if self.added:
			sys.path.remove(self.path)


def mock_phantom(callable):
	@wraps(callable)
	def wrapper(*args, **kwargs):
		with MockedPhantomModule():
			return callable(*args, **kwargs)

	return wrapper
