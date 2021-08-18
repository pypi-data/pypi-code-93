import os, re

from .config import (
	audio_dir, video_dir,
	audio_key, video_key,
	video_cache_dir,
	video_result_dir,
	partial_postfix,
	finished_files_list,
)
from .helpers import get_system_output, is_video_finished

def check_audio_format(filepath):
	"""
	Get audio format from ffprobe output
	"""

	# https://stackoverflow.com/a/21789183
	# https://stackoverflow.com/a/28769074
	video_stats = get_system_output(('ffprobe', os.path.abspath(filepath)))
	return re.search(r'Audio: (\w+)', video_stats).group(1)

def extract_audio(videos, cache_key, abs_out_dir):
	extracted_audios = []
	for v in videos:
		video_cache_file = os.path.join(abs_out_dir, video_cache_dir, v[cache_key])
		audio_format = check_audio_format(video_cache_file)

		audio_file = f"{v['title']}.{audio_format}"

		extracted_audios.append({
			'title': v['title'], # as id
			audio_key: audio_file,
		})

		audio_path = os.path.join(abs_out_dir, audio_dir, audio_file)

		if os.path.exists(audio_path):
			continue

		# https://stackoverflow.com/a/63237888
		# 0:a:0 is get from '0' input 'audio' with number '0', '-c copy' is do not convert audio stream
		result = os.system(f"""
			ffmpeg \
			-i '{video_cache_file}' \
			-map 0:a:0 \
			-c copy '{audio_path}'
		""")

		not_finished_file = audio_path + partial_postfix
		if result == 0:
			# convert successfully
			pass
		elif result == 256:
			# file exist
			print('file', not_finished_file, 'exists')
		else:
			os.system(f"mv '{audio_path}' '{not_finished_file}'")
			print('result code:', result)

	return extracted_audios

def append_audios(filenames, abs_out_dir, preserve_video):
	for file in filenames:
		audio_path = os.path.join(abs_out_dir, audio_dir, file[audio_key])
		video_path = os.path.join(abs_out_dir, video_dir, file[video_key])

		out_file = os.path.join(abs_out_dir, video_result_dir, file[video_key])

		if os.path.exists(out_file) or is_video_finished(abs_out_dir, file[video_key]):
			continue

		# https://stackoverflow.com/a/11783474
		# looks like audio fits to video duration (if check duration with ffprobe for aac,
		# for example, it return 'Estimating duration from bitrate, this may be inaccurate')
		# maybe because video is written before audio
		result = os.system(f"""
			ffmpeg \
			-i '{video_path}' \
			-i '{audio_path}' \
			-map 0 \
			-map 1:a \
			-c:v copy \
			'{out_file}'
		""")

		if result == 0:
			# append successfully
			pass
		elif result == 256:
			# file exist
			print('file', out_file, 'exists')
		elif result == 65280:
			# SIGINT
			quit('\nExiting')
		else:
			# ffmpeg can't continue converting, only from beginning
			os.system(f"rm '{out_file}'")
			quit(f'result code: {result}')

	if not preserve_video:
		move_videos(filenames, abs_out_dir)

def move_videos(filenames, abs_out_dir):
	for file in filenames:
		if is_video_finished(abs_out_dir, file[video_key]):
			continue

		video_folder = os.path.join(abs_out_dir, video_dir)
		video_path = os.path.join(video_folder, file[video_key])
		out_file = os.path.join(abs_out_dir, video_result_dir, file[video_key])

		finished_file = os.path.join(video_folder, finished_files_list)
		os.system(f"mv '{out_file}' '{video_path}'")
		os.system(f"echo '{file[video_key]}' >> '{finished_file}'")
