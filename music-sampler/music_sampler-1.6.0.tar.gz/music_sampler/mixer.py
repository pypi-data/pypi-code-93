import sounddevice as sd
import audioop
import time

from .helpers import Config, error_print

sample_width = Config.sample_width

def sample_width_to_dtype():
    if sample_width == 1 or sample_width == 2 or sample_width == 4:
        return 'int' + str(8*sample_width)
    else:
        error_print("Unknown sample width, setting default value 2.")
        Config.sample_width = 2
        return 'int16'

def _latency(latency):
    if latency == "high" or latency == "low":
        return latency
    else:
        return float(latency)

class Mixer:
    def __init__(self):
        self.stream = sd.RawOutputStream(
                samplerate=Config.frame_rate,
                channels=Config.channels,
                dtype=sample_width_to_dtype(),
                latency=_latency(Config.latency),
                blocksize=Config.blocksize,
                callback=self.play_callback)
        self.open_files = []

    def add_file(self, music_file):
        if music_file not in self.open_files:
            self.open_files.append(music_file)
        self.start()

    def remove_file(self, music_file):
        if music_file in self.open_files:
            self.open_files.remove(music_file)
        if len(self.open_files) == 0:
            self.stop()

    def stop(self):
        self.stream.stop()

    def start(self):
        self.stream.start()

    def play_callback(self, out_data, frame_count, time_info, status_flags):
        out_data_length = len(out_data)
        empty_data = b"\0" * out_data_length
        data = b"\0" * out_data_length

        for open_file in self.open_files:
            file_data = open_file.play_callback(out_data_length, frame_count)

            if data == empty_data:
                data = file_data
            elif file_data != empty_data:
                data = audioop.add(data, file_data, sample_width)

        out_data[:] = data

