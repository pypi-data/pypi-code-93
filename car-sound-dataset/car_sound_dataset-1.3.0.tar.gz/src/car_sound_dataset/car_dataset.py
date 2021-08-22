import os
import sys

from google_drive_downloader import GoogleDriveDownloader as gdd
import json
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
import numpy as np
import sounddevice as sd
import soundfile as sf
import random



class CarSoundDataset():
    """
        A class used to represent the car sound dataset.

        ...

        Attributes
        ----------
        path : str
            A path, where you want to download and use the dataset.
            The default path is the current working directory.

        Methods
        -------
        download_and_get_dataset()
            Downloads the dataset and the json file, which identifies the events.

        plot_event(car_dataset_dict, event_id)
            You can plot an event with this method.

        play_event(car_dataset_dict, event_id, nomralize=True)
            You can play the recordings of an event with this method.

        filter_by_pattern(car_dataset_dict, pattern)
            This method helps you to select events by a pattern.
            The pattern should contain 'X', '0' or '1'.
            'X' - You don't care, if the device recorded the event or not.
            '0' - You skip the recordings of this device.
            '1' - This device recorded the event.
            You have to give the pattern as a list. Each list element represents each device.
            An example pattern: ['0', '1', 'X', '0', 'X', '1']
            This means we skip the recordings of DEVICE1 and DEVICE4. We select the events,
            where DEVICE2 and DEVICE6 recorded the event. Each event will contain 2-4 recordings.
            It depends on DEVICE3 and DEVICE5. If one of DEVICE3 and DEVICE5 recorded the event,
            the event will contain 3 recordings and if both is recorded the event, it will contain
            4 recordings.

        filter_by_exact_device_count(car_dataset_dict, device_count)
            This method selects the events, which is recorded by the given count of devices.

        filter_by_min_device_count(car_dataset_dict, device_count)
            This method selects the events, which is recorded by at least the given count of devices.

        load_dict_as_pool(car_dataset_dict)
            This method loads the recordings into a 3D numpy array. In this case each element
            contains only one recording. The recordings of an event are split to single recordings.

        load_dict(car_dataset_dict, is_random = False, device_indexes = [])
            This method loads the recordings into a 3D numpy array. In this case each element
            contains events. One event usually contains more than one recordings.

    """

    def __init__(self, path=os.getcwd()):
        """
            Parameters
            ----------
            path : str
                A path, where you want to download and use the dataset.
                The default path is the current working directory.

        """

        self.path = path

    def download_and_get_dataset(self):

        """
            Downloads the dataset and the json file, which identifies the events.

            Returns
            ----------
            dict
                A dictionary, which represents the events of the dataset.
                The key of the dictionary is the event number, and the value is
                a list of recordings, which means an event.

        """

        path = self.path
        car_sounds_zipped_path = path + '\\CAR_SOUNDS.zip'
        car_sounds_unzipped_path = path + '\\CAR_SOUNDS'
        car_events_json_path = path + '\\car_sound_events.json'

        if not os.path.exists(car_sounds_unzipped_path):
            gdd.download_file_from_google_drive(file_id='1GjEs-S12RH2X70I3pEBMFY2RQ1c_ol1a',
                                                dest_path=car_sounds_zipped_path,
                                                unzip=True)
            os.remove(car_sounds_zipped_path)

        if not os.path.exists(car_events_json_path):
            gdd.download_file_from_google_drive(file_id='1HJNGzD8g6rLrONBK9WB9sEExlqHHKkTv',
                                                dest_path=car_events_json_path,
                                                unzip=False)

        with open(car_events_json_path) as json_file:
            data = json.load(json_file)
        data = {int(k): v for k, v in data.items()}

        return data

    def list_events_of_dict(self, car_dataset_dict):
        """
             This method prints to console the event IDs of a car_dataset_dict.

             Parameters
             ----------
             car_dataset_dict : dict
                 The whole or a filtered dictionary, which contains events.

        """

        print("The event IDs in the dict: ")
        keys = car_dataset_dict.keys()
        for key in keys:
            print(key, '; ', end='')

        print()
        print()

    def plot_event(self, car_dataset_dict, event_id):
        """
             You can plot an event with this method. The red plot means that
             those DEVICES did not record the event.

             Parameters
             ----------
             car_dataset_dict : dict
                 The whole or a filtered dictionary, which contains events.

             event_id: int
                The event number.
                If you use an event number which is not in your dict,
                you will get an error.

        """

        try:
            path = self.path
            event = car_dataset_dict[event_id]
            fig, axs = plt.subplots(3, 2)

            fig.suptitle('Recordings of event ' + str(event_id))
            for i in range(0, 3, 1):
                for j in range(0, 2, 1):

                    if event[2 * i + j] == None:
                        sound_data = np.zeros(11712, dtype=np.int16)
                        axs[i, j].plot(sound_data, 'r')

                    else:
                        freq, sound_data = read(path + '/' + 'CAR_SOUNDS' + '/' + event[2 * i + j])
                        axs[i, j].plot(sound_data)

                    axs[i, j].set_title('DEVICE ' + str((2 * i + j) + 1))

            plt.tight_layout()

            plt.show()

        except:
            print("ERROR: You gave an incorrect event ID!")
            sys.exit(-1)


    def play_event(self, car_dataset_dict, event_id, nomralize=True):
        """
             You can play the recordings of an event with this method.

             Parameters
             ----------
             car_dataset_dict : dict
                 The whole or a filtered dictionary, which contains events.

             event_id: int
                The event number.
                If you use an event number which is not in your dict,
                you will get an error.

             normalize: bool, optional
                If this parameter is True, the recordings will be normalized before playing.
                Else you will play the raw recordings
                Default: True

        """

        try:

            path = self.path
            event = car_dataset_dict[event_id]
            sounds = [x for x in event if x is not None]
            print('Playing recordings of event ' + str(event_id))
            for sound in sounds:
                parts = sound.split('_')
                print('Recording of DEVICE ' + parts[0][1])
                data, fs = sf.read(path + '/' + 'CAR_SOUNDS' + '/' + sound, dtype='int16')
                if nomralize:
                    temp = np.abs(data)
                    max = np.max(temp)
                    scale = 32768 // max
                else:
                    scale = 1
                sd.play(data * scale, fs)
                sd.wait()

        except:
            print("ERROR: You gave an incorrect event ID!")
            sys.exit(-1)

    # example pattern: ['0', '1', 'X', '0', 'X', '1']
    def filter_by_pattern(self, car_dataset_dict, pattern):
        """
            This method helps you to select events by a pattern.
            The pattern should contain 'X', '0' or '1'.
            'X' - You don't care, if the device recorded the event or not.
            '0' - You skip the recordings of this device.
            '1' - This device recorded the event.
            You have to give the pattern as a list. Each list element represents each device.
            An example pattern: ['0', '1', 'X', '0', 'X', '1']
            This means we skip the recordings of DEVICE1 and DEVICE4. We select the events,
            where DEVICE2 and DEVICE6 recorded the event. Each event will contain 2-4 recordings.
            It depends on DEVICE3 and DEVICE5. If one of DEVICE3 and DEVICE5 recorded the event,
            the event will contain 3 recordings and if both is recorded the event, it will contain
            4 recordings.

             Parameters
             ----------
             car_dataset_dict : dict
                 The whole or a filtered dictionary, which contains events.

             pattern: list
                A list, which represents the pattern.

            Returns
            ----------
            dict
                A dictionary, which represents the filtered dataset.

        """
        filtered_events = {}
        for event_key in car_dataset_dict:
            temp_filtered_event = []
            event_pattern = []
            event = car_dataset_dict[event_key]
            for recording in event:
                if recording is not None:
                    event_pattern.append('1')
                else:
                    event_pattern.append('0')

            votes = []
            for i in range(0, len(pattern), 1):
                if pattern[i] == 'X':
                    votes.append(True)
                elif pattern[i] == '0':
                    votes.append(True)
                elif pattern[i] == event_pattern[i]:
                    votes.append(True)
                else:
                    votes.append(False)

            if sum(votes) == 6:

                for i in range(0, len(pattern), 1):
                    if pattern[i] == '0':
                        temp_filtered_event.append(None)
                    else:
                        temp_filtered_event.append(event[i])

                if len([x for x in temp_filtered_event if x is not None]) != 0:
                    filtered_events[event_key] = temp_filtered_event

        return filtered_events

    def filter_by_exact_device_count(self, car_dataset_dict, device_count):
        """
             This method selects the events, which is recorded by the given count of devices.

             Parameters
             ----------
             car_dataset_dict : dict
                 The whole or a filtered dictionary, which contains events.

             device_count: int
                This number means that exactly how many device recorded the event.

             Returns
             ----------
             dict
                A dictionary, which represents the filtered dataset.

        """
        filtered_events = {}
        for event_key in car_dataset_dict:
            event = car_dataset_dict[event_key]
            if len([x for x in event if x is not None]) == device_count:
                filtered_events[event_key] = event

        return filtered_events

    def filter_by_min_device_count(self, car_dataset_dict, device_count):
        """
             This method selects the events, which is recorded by at least the given count of devices.

             Parameters
             ----------
             car_dataset_dict : dict
                 The whole or a filtered dictionary, which contains events.

             device_count: int
                This number means that at least how many device recorded the event.

             Returns
             ----------
             dict
                A dictionary, which represents the filtered dataset.

        """
        filtered_events = {}
        for event_key in car_dataset_dict:
            event = car_dataset_dict[event_key]
            if len([x for x in event if x is not None]) >= device_count:
                filtered_events[event_key] = event

        return filtered_events

    def load_dict_as_pool(self, car_dataset_dict):
        """
              This method loads the recordings into a 3D numpy array. In this case each element
              contains only one recording. The recordings of an event are split to single recordings.

              Parameters
              ----------
              car_dataset_dict : dict
                  The whole or a filtered dictionary, which contains events.

              Returns
              ----------
              numpy array
                 A 3D numpy array, which contains the data of the recordings.

         """
        path = self.path
        number_of_recordings = 0
        for event_key in car_dataset_dict:
            event = car_dataset_dict[event_key]
            for recording in event:
                if recording is not None:
                    number_of_recordings += 1

        pool = np.zeros((number_of_recordings, 1, 11712), dtype=np.int16)

        numpy_index = 0
        for event_key in car_dataset_dict:
            event = car_dataset_dict[event_key]
            for recording in event:
                if recording is not None:
                    freq, sound_data = read(path + '/' + 'CAR_SOUNDS' + '/' + recording)
                    pool[numpy_index][0] = sound_data
                    numpy_index += 1

        return pool

    def load_dict(self, car_dataset_dict, is_random=False, device_indexes=[]):
        """
              This method loads the recordings into a 3D numpy array. In this case each element
              contains events. One event usually contains more than one recordings. Without the optional
              parameters the method will load the first N available recordings, where N is the size
              of the event, which contains the minimum recordings. If is_random parameter is True and device_indexes
              is empty, the method will load random N recordings of an event. If we give a list with device indexes
              (1,2,3,4,5,6), the method will load the recordings, which belongs to the given devices.
              Example device indexes: [1,2,3]
              This means recordings of DEVICE1, DEVICE2 and DEVICE3 will be loaded, they are available.

              Parameters
              ----------
              car_dataset_dict : dict
                  The whole or a filtered dictionary, which contains events.

              is_random: bool, optional
                 If True, randomize the recordings of each event.
                 Default: False

              device_indexes: list, optional
                List of device indexes, which recordings will be loaded.
                Default: Empty

              Returns
              ----------
              numpy array
                 A 3D numpy array, which contains the data of the recordings.

         """
        path = self.path
        number_of_events = 0

        for event_key in car_dataset_dict:
            number_of_events += 1

        if (not is_random) and (len(device_indexes) == 0):

            numbers_list = []
            for event_key in car_dataset_dict:
                event = car_dataset_dict[event_key]
                number_of_recordings = 0
                for recording in event:
                    if recording is not None:
                        number_of_recordings += 1
                numbers_list.append(number_of_recordings)

            max_n = np.min(numbers_list)

            data = np.zeros((number_of_events, max_n, 11712), dtype=np.int16)

            numpy_index_dimension_1 = 0
            for event_key in car_dataset_dict:

                event = car_dataset_dict[event_key]
                numpy_index_dimension_2 = 0

                for recording in event:

                    if recording is not None:

                        freq, sound_data = read(path + '/' + 'CAR_SOUNDS' + '/' + recording)
                        data[numpy_index_dimension_1][numpy_index_dimension_2] = sound_data
                        numpy_index_dimension_2 += 1

                        if numpy_index_dimension_2 == max_n:
                            break

                numpy_index_dimension_1 += 1

        elif is_random and (len(device_indexes) == 0):

            numbers_list = []
            for event_key in car_dataset_dict:
                event = car_dataset_dict[event_key]
                number_of_recordings = 0
                for recording in event:
                    if recording is not None:
                        number_of_recordings += 1
                numbers_list.append(number_of_recordings)

            max_n = np.min(numbers_list)

            data = np.zeros((number_of_events, max_n, 11712), dtype=np.int16)

            numpy_index_dimension_1 = 0
            for event_key in car_dataset_dict:

                event = car_dataset_dict[event_key]
                random.shuffle(event)

                numpy_index_dimension_2 = 0

                for recording in event:

                    if recording is not None:

                        freq, sound_data = read(path + '/' + 'CAR_SOUNDS' + '/' + recording)
                        data[numpy_index_dimension_1][numpy_index_dimension_2] = sound_data
                        numpy_index_dimension_2 += 1

                        if numpy_index_dimension_2 == max_n:
                            break

                numpy_index_dimension_1 += 1

        else:

            max_n = len(device_indexes)

            for event_key in car_dataset_dict:

                event = car_dataset_dict[event_key]

                enable_copy = True

                for idx in device_indexes:
                    idx -= 1
                    if event[idx] is None:
                        enable_copy = False

                if not enable_copy:

                    number_of_events -= 1

            data = np.zeros((number_of_events, max_n, 11712), dtype=np.int16)

            numpy_index_dimension_1 = 0
            for event_key in car_dataset_dict:

                event = car_dataset_dict[event_key]

                numpy_index_dimension_2 = 0

                enable_copy = True

                for idx in device_indexes:
                    idx -= 1
                    if event[idx] is None:
                        enable_copy = False

                if enable_copy:
                    for idx in device_indexes:
                        idx -= 1
                        if event[idx] is not None:

                            freq, sound_data = read(path + '/' + 'CAR_SOUNDS' + '/' + event[idx])
                            data[numpy_index_dimension_1][numpy_index_dimension_2] = sound_data
                            numpy_index_dimension_2 += 1

                            if numpy_index_dimension_2 == max_n:
                                break

                    numpy_index_dimension_1 += 1

        if len(data) == 0:
            print("ERROR: Your parameters are incorrect! The result dataset is empty!")
            sys.exit(-1)

        return data
