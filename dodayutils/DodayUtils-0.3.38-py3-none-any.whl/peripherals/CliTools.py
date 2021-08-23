import subprocess
from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *

@dutils
def cli_normal_call(param=[], **kwargs):
	"""
	This is the function to do the normal
	cli call
	"""
	return subprocess.check_output(param) 

@dutils
def cli_async_call(param=[], **kwargs):
	"""
	This is the function to call cli
	asynchronously. Return process id, 
	need to call pid.wait() to avoid
	zombie processes
	"""
	return subprocess.Popen(param) 

@dutils
def cli_call_scripts(file_path, param=[], **kwargs):
	"""
	This is the function to help call the
	script via cli. 
	"""
	if param != []:
		output = subprocess.check_output(['bash', file_path]+param)
	else:
		output = subprocess.check_output(['bash', file_path]) # with args:  subprocess.call(['./test.sh', 'param1', 'param2'])
	return output

@dutils
def cli_pi_play_sound(sound_file, sound_source, mode="async", **kwargs):
	"""
	This is the function to play sound via command line. 
	- Input:
		* sound_file: e.g. '/home/pi/ding.mp3'
		* sound_source: local or hdmi
		* mode: normal or async
	- Return: process id
	"""
	# Get default lib from api lib files
	sound_file_load = os.path.dirname(os.path.abspath(__file__))+sound_file.replace('@', '/') \
		if '@' in sound_file else sound_file

	if mode == "async":
		return cli_async_call(['omxplayer', '--no-keys', '-o', sound_source, sound_file_load, '&'])
	elif mode == "normal":
		return cli_normal_call(['omxplayer', '--no-keys', '-o', sound_source, sound_file_load, '&'])
