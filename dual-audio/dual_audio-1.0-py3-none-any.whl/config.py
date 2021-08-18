audio_dir = 'audio'
video_cache_dir = 'video-cache'
video_dir = 'video'
video_result_dir = 'video-result'

needed_utilities = [
	'ffmpeg',
	'grep',
	'wget',
]

needed_dirs = [
	audio_dir,
	video_cache_dir,
	video_dir,
	video_result_dir,
]

partial_postfix = '-partial'

finished_files_list = 'finished.txt'

# keys
video_cache_key = 'video_cache_file'
audio_key = 'audio_file'
video_key = 'video_file'
video_extension_key = 'video_extension'
audio_extension_key = 'audio_extension'

template_keys = {
	'title': '<title>',
	'link': '<link>',
}
