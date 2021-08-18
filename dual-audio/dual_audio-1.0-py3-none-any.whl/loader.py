import os

from .config import partial_postfix, video_key
from .helpers import is_video_finished

def load_files_from_list(data, filename_key, abs_out_dir, media_dir, extension_key):
	loaded_files = []
	for d in data:
		filename = f"{d['title']}.{d[extension_key]}"
		loaded_files.append({**d, filename_key: filename})

		# check existing if it's not a cache video
		if filename_key == video_key and is_video_finished(abs_out_dir, filename):
			continue

		file_path = os.path.join(abs_out_dir, media_dir, filename)

		if os.path.exists(file_path):
			# just for message
			os.system(f"wget --output-document '{file_path}' --no-clobber '{d['link']}'")
			continue

		not_finished_file = file_path + partial_postfix
		result = os.system(f"wget --output-document '{not_finished_file}' --continue '{d['link']}'")

		if result == 0:
			# download successfully
			os.system(f"mv '{not_finished_file}' '{file_path}'")
		elif result == 2:
			# SIGINT (ctrl+C)
			quit('\nExiting')
		else:
			print('result code:', result)

	return loaded_files
