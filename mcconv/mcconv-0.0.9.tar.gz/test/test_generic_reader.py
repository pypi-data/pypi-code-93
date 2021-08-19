from mcconv import GenericTextReader, UnparsedTextEvent

import os
import unittest
from mcconv import detect_mc_type, McFileTypes



class TestGenericTextReader(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def _mc_file_path(self, path):
        """Gets data file path"""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, 'data', path)


    def test_read_file(self):
        """Test detecting BeaGLE file type"""

        def is_line_relevant(line):
            is_comment = any(word in line for word in ['BEAGLE', 'I', '='])
            return not is_comment

        def is_event(tokens):
            return len(tokens) > 20 # Beagle event header has like 50 tokens, particle like 16

        def is_particle(tokens):
            return len(tokens) < 20

        reader = GenericTextReader(is_line_relevant, is_event, is_particle)
        reader.open(self._mc_file_path('beagle_3events.txt'))

        events = [event for event in reader.events()]
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0].start_line_index, 6)        # The first event is on line index 6
        self.assertEqual(len(events[0].unparsed_particles), 11)   # There are 11 particles
        self.assertEqual(events[0].unparsed_particles[0][2], "11")  # There are 11 particles
        self.assertEqual(events[0].event_tokens[6], "-5")  # There are 11 particles
        reader.close()

    def test_default_event_identification(self):
        """Test detecting BeaGLE file type"""

        reader = GenericTextReader()
        reader.particle_tokens_len = 18
        reader.open(self._mc_file_path('beagle_3events.txt'))

        events = [event for event in reader.events()]
        self.assertEqual(3, len(events))
        self.assertEqual(events[0].start_line_index, 6)        # The first event is on line index 6
        self.assertEqual(len(events[0].unparsed_particles), 11)   # There are 11 particles
        self.assertEqual(events[0].unparsed_particles[0][2], "11")  # There are 11 particles
        self.assertEqual(events[0].event_tokens[6], "-5")  # There are 11 particles
        reader.close()

    def test_event_ranges(self):
        """Test number of events to skip and to take"""
        reader = GenericTextReader()
        reader.open(self._mc_file_path('pythia6-radcor-10evt.txt'))

        events = [event for event in reader.events(evt_skip=3, evt_take=2)]
        self.assertEqual(2, len(events))
        self.assertEqual(events[0].start_line_index, 167)  # The 4th event is on line index 168
        self.assertEqual(events[0].unparsed_particles[1][2], '2212')  # The second particle is proton
