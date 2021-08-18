import os, subprocess

from .config import audio_key, video_key, video_dir, finished_files_list

def get_system_output(args):
	return subprocess.Popen(
		args,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,  # get all output
		universal_newlines=True,  # return string not bytes
	).communicate()[0]

def check_system_utilities():
	from .config import needed_utilities as utilities

	missing = []
	for u in utilities:
		if os.system(f'which {u} > /dev/null'):
			missing.append(u)

	if len(missing) == 0:
		return

	print('Please, install this packages/utilities to the system:')
	for m in missing:
		print(m)

	quit()

def setup_checks(out_directory):
	check_system_utilities()

	out_dir = os.path.abspath(out_directory)

	from .config import needed_dirs as dirs
	for d in dirs:
		os.makedirs(os.path.join(out_dir, d), exist_ok=True)

def find_object_by_keys_value(l, key, value):
	res = [o for o in l if o[key] == value]
	return res[0] if res else None

def get_filenames(audio_index, video_index):
	"""
	Get filenames from indexes

	audio_index: see converter.py::extract_audio
	video_index: see playlist.py::parse_playlist and loader.py
	"""
	if len(audio_index) != len(video_index):
		quit(f'Count of audios ({len(audio_index)}) and videos ({len(video_index)}) does not match')

	result = []

	for a in audio_index:
		v = find_object_by_keys_value(video_index, 'title', a['title'])
		if not v:
			quit(f"Not found \"{a['title']}\" in {video_index}")

		result.append({
			'title': a['title'],
			audio_key: a[audio_key],
			video_key: v[video_key],
		})

	return result

def is_video_finished(abs_out_dir, name):
	finished_file = os.path.join(abs_out_dir, video_dir, finished_files_list)
	result = os.system(f"grep '{name}' '{finished_file}' > /dev/null")
	return True if result == 0 else False
