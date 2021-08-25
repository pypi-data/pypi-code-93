import argparse
import cv2
from os import path
from trucotrack import frame_dispatcher
from trucotrack.trackers import mediapipe_face, mediapipe_hand

class Cli:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Uses MediaPipe to generate CSV files from videos or camera live streams with the records of the tracked movements.')
        self.parser.add_argument('--video', help='[filename] Existing video to be tracked. If empty, --camera will be used')
        self.parser.add_argument('--camera', help='[int] Number that identifies the camera to use')
        self.parser.add_argument('--interval', help='[int] Number of records to store in memory before writing them')
        self.parser.add_argument('--first', help='[int] First frame to capture')
        self.parser.add_argument('--last', help='[int] Last frame to capture')
        self.parser.add_argument('--flip', help='[yes|no] Flip the image horizontally')
        self.parser.add_argument('--mp_hands_max', help='[int] Maximum number of hands to track with MediaPipe')
        self.parser.add_argument('--mp_hands_static', help='[yes|no] Tell MediaPipe to run a continuous detection of hands')
        self.parser.add_argument('--mp_hands_draw', help='[yes|no] Draw MediaPipe\'s records of tracked hands')
        self.parser.add_argument('--mp_hands_csv', help='[filename] Export a CSV file with MediaPipe\'s records of tracked hands')
        self.parser.add_argument('--mp_faces_max', help='[int] Maximum number of faces to track with MediaPipe')
        self.parser.add_argument('--mp_faces_static', help='[yes|no] Tell MediaPipe to run a continuous detection of faces')
        self.parser.add_argument('--mp_faces_draw', help='[yes|no] Draw MediaPipe\'s records of tracked faces')
        self.parser.add_argument('--mp_faces_csv', help='[filename] Export a CSV file with MediaPipe\'s records of tracked faces')
        self.parse_arguments()

    def main(self):
        dispatcher = frame_dispatcher.FrameDispatcher(self.args)

        first_iteration = True
        for dispatched_frame in dispatcher.get_frame():
            if self.using_mp_hands():
                if first_iteration:
                    mp_hand_tracker = mediapipe_hand.MediapipeHand(self.args)
                mp_hand_tracks = mp_hand_tracker.process(dispatched_frame)

            if self.using_mp_faces():
                if first_iteration:
                    mp_face_tracker = mediapipe_face.MediapipeFace(self.args)
                mp_face_tracks = mp_face_tracker.process(dispatched_frame)

            cv2.imshow('Motion Tracker', dispatched_frame['frame'])
            first_iteration = False

        if self.using_mp_hands():
            mp_hand_tracker.close_writer()

        if self.using_mp_faces():
            mp_face_tracker.close_writer()

    def using_mp_hands(self):
        return self.args.mp_hands_draw == 'yes' or \
            self.args.mp_hands_csv != None

    def using_mp_faces(self):
        return self.args.mp_faces_draw == 'yes' or \
            self.args.mp_faces_csv != None

    def parse_arguments(self):
        self.args = self.parser.parse_args()
        self.validate()
        self.ensure_types()
        self.set_defaults()

    def string_represents_integer(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def stop_because(self, reason):
        print("\n" + reason + "\n")
        print('Try calling the program with -h for help')
        exit()

    def assert_is_not_empty(self, argument_name):
        value = getattr(self.args, argument_name)

        if value == None:
            self.stop_because('A value is missing for --' + argument_name)

    def assert_is_integer(self, argument_name):
        value = getattr(self.args, argument_name)

        if value != None and not self.string_represents_integer(value):
            self.stop_because(
                'Invalid value received for --' + argument_name + '. ' +
                'Try with a valid integer number.')

    def assert_only_one_is_not_empty(self, argument_name_1, argument_name_2):
        empty_1 = getattr(self.args, argument_name_1) == None
        empty_2 = getattr(self.args, argument_name_2) == None

        if not empty_1 and not empty_2:
            self.stop_because(
                'Invalid value received for --' +
                argument_name_1 + ' and --' + argument_name_2 + '. ' +
                'Only one of them can be provided at a time.')
        elif empty_1 and empty_2:
            self.stop_because(
                'Invalid value received for --' +
                argument_name_1 + ' and --' + argument_name_2 + '. ' +
                'One of them must be defined.')

    def assert_file_is_writable(self, argument_name):
        file_name = getattr(self.args, argument_name)

        try:
            with open(file_name, 'w') as f:
                pass
        except IOError as x:
            self.stop_because(
                'Invalid value received for --' + argument_name + '. ' +
                'Check that the file path is writable.')

    def assert_is_optional_yes_or_no(self, argument_name):
        value = getattr(self.args, argument_name)

        if value != None and value not in ['yes', 'no']:
            self.stop_because(
                'Invalid value received for --' + argument_name + '. ' +
                'Try with either yes, or no.')

    def assert_file_exists(self, argument_name):
        value = getattr(self.args, argument_name)

        if value != None and not path.isfile(value):
            self.stop_because('Invalid value received for --' + argument_name)

    def validate(self):
        self.assert_only_one_is_not_empty('video', 'camera')
        self.assert_file_exists('video')
        self.assert_is_integer('camera')
        self.assert_is_integer('interval')
        self.assert_is_integer('first')
        self.assert_is_integer('last')
        self.assert_is_optional_yes_or_no('flip')

        self.assert_is_integer('mp_hands_max')
        self.assert_is_optional_yes_or_no('mp_hands_static')
        self.assert_is_optional_yes_or_no('mp_hands_draw')
        if self.args.mp_hands_csv != None:
            self.assert_file_is_writable('mp_hands_csv')

        self.assert_is_integer('mp_faces_max')
        self.assert_is_optional_yes_or_no('mp_faces_static')
        self.assert_is_optional_yes_or_no('mp_faces_draw')
        if self.args.mp_faces_csv != None:
            self.assert_file_is_writable('mp_faces_csv')

    def ensure_is_int(self, field):
        if field in self.args:
            value = getattr(self.args, field)
            if value != None:
                setattr(self.args, field, int(value))

    def ensure_types(self):
        self.ensure_is_int('camera')
        self.ensure_is_int('interval')
        self.ensure_is_int('first')
        self.ensure_is_int('last')
        self.ensure_is_int('mp_hands_max')
        self.ensure_is_int('mp_faces_max')

    def set_defaults(self):
        if self.args.video == None and self.args.camera == None:
            self.args.camera = 0

        if self.args.first == None:
            self.args.first = 1

        if self.args.flip == None:
            self.args.flip = 'yes' if self.args.video == None else 'no'

        if self.args.interval == None:
            self.args.interval = 25

        if self.using_mp_hands():
            if self.args.mp_hands_max == None:
                self.args.mp_hands_max = 2

            if self.args.mp_hands_static == None:
                self.args.mp_hands_static = 'no'

            if self.args.mp_hands_draw == None:
                self.args.mp_hands_draw = 'yes'

        if self.using_mp_faces():
            if self.args.mp_faces_max == None:
                self.args.mp_faces_max = 1

            if self.args.mp_faces_static == None:
                self.args.mp_faces_static = 'no'

            if self.args.mp_faces_draw == None:
                self.args.mp_faces_draw = 'yes'

def main():
    tracker = Cli()
    tracker.main()

if __name__ == '__main__':
    main()
