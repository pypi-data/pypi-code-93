from trucotrack.trackers.mediapipe import hand_tracker

class TrucoTrackCli:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Uses MediaPipe to generate CSV files from videos or camera live streams with the records of the tracked movements.')
        self.parse_arguments()

    def main(self):
        tracker = hand_tracker.HandTracker(self.args)
        tracker.run()

    def parse_arguments(self):
        self.parser.add_argument('--video', help='[filename] Existing video to be tracked. If empty, --camera will be used')
        self.parser.add_argument('--camera', help='[int] Number that identifies the camera to use')
        self.parser.add_argument('--output', help='[filename] Text file that will store the records')
        self.parser.add_argument('--interval', help='[int] Number of records to store in memory before writing them')
        self.parser.add_argument('--first', help='[int] First frame to capture')
        self.parser.add_argument('--last', help='[int] Last frame to capture')
        self.parser.add_argument('--dynamic', help='[yes|no] Run a continuous detection of hands')
        self.parser.add_argument('--hands', help='[int] Number of hands to track')
        self.parser.add_argument('--flip', help='[yes|no] Flip the image horizontally')
        self.parser.add_argument('--draw', help='[yes|no] Draw the tracking points')
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
        self.assert_is_not_empty('output')
        self.assert_file_is_writable('output')
        self.assert_is_integer('interval')
        self.assert_is_integer('first')
        self.assert_is_integer('last')
        self.assert_is_integer('hands')
        self.assert_is_optional_yes_or_no('dynamic')
        self.assert_is_optional_yes_or_no('flip')
        self.assert_is_optional_yes_or_no('draw')

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
        self.ensure_is_int('hands')

    def set_defaults(self):
        if self.args.video == None and self.args.camera == None:
            self.args.camera = 0

        if self.args.first == None:
            self.args.first = 1

        if self.args.hands == None:
            self.args.hands = 2

        if self.args.dynamic == None:
            self.args.dynamic = 'yes'

        if self.args.flip == None:
            self.args.flip = 'yes' if self.args.video == None else 'no'

        if self.args.draw == None:
            self.args.draw = 'yes'

        if self.args.interval == None:
            self.args.interval = 25
