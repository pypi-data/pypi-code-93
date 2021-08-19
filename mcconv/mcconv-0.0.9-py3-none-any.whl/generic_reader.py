"""

Universal parser for text files from generators. It aims for cases:
1. Files have are space/tab separated data values
2. Each event start with one line of data
3. Then there are several lines with data for each particle in event
4. (!) number of tokens in event and particle line should be different

2-3. Means that if we see an event record after particle records
     it means, that the new event has started

 This class works for files like from pythia6, beagle, etc...

 D A T A   E X A M P L E:
 Lets look at beagle event record:
      BEAGLE EVENT FILE
      ============================================
      I, ievent, ...
      ============================================
      I  ISTHKK(I)  ...
      ============================================
      0          1    1   11    2    1    ... <50+ tokens>
      ============================================
       1     21         11        0       -0.000000       -0.000000       -5.000000  ... <15 tokens>
       2     21       2212        0        0.000000        0.000000       50.107677  ...
      ...
      20      1       2212        0        0.018354        0.019732       45.588296  ...
      =============== Event finished ===============
      0          2    1   11    2    1 ... <next event >
      ============================================
      1     21         11        0        0.000000        0.000000       -5.000000 ...
 What we see here is:
     1. First 5 lines are to be skipped
     2. Lines with '====================' are to be skipped
     3. Lines like "0 1 1 11 2 1 ..." are the beginning of event data with whole vent info
     4. All the next lines like "1 21 22122 ..." are particle data lines (called record in this class)
     5. All lines in 3 and 4 need to be tokenized
     6. In other file formats comments like '#...' should be ignored

 As a result of parsing we will have and event in terms of :
  TextFileEvent:
      started_at_line;    // Line number at which the event has started
      event_tokens;       // All tokens like ["0", "1", "1", "11", "2", "1", ...] from 'event' related line/s
      record_tokens       // All tokens like ["1", "21", "22122", ...] from each particle or 'record' lines


"""
import io
import enum
import shlex
from typing import AnyStr, Callable
import re


class UnparsedTextEvent:
    """Unparsed """
    def __init__(self):
        self.start_line_index = 0
        self.io_event_index = 0             # event number as it was read from file
        self.event_tokens = []
        self.unparsed_particles = []

FIELDS_PATTERN = re.compile(r"(?:\"(.*?)\"|(\S+))")

def regex_split(data):
    return [x[0] or x[1] for x in FIELDS_PATTERN.findall(data)]

class GenericTextReader:
    """Generic class to read EIC related text MC file formats"""

    buffer_size = 65536

    def __init__(self, is_line_relevant: Callable = None, is_event: Callable = None, is_particle: Callable = None, convert_rules={}, skip_lines: int = 0):
        self.file_path = ""
        self.file: [io.TextIOBase, None] = None
        self.line_index = 0
        self.skip_lines = skip_lines
        self.is_line_relevant = is_line_relevant
        self.is_event_line = is_event
        self.is_particle_line = is_particle
        self.last_record_was_particle = False
        self.particle_tokens_len = 14
        self.hepmc_conv_rules = convert_rules
        self.event_index = 0

        if not is_line_relevant:
            self.is_line_relevant = self.default_is_line_relevant

        if not is_event:
            self.is_event_line = self.default_is_event

        if not is_particle:
            self.is_particle_line = self.default_is_particle

    def open(self, file_path):
        self.file_path = file_path
        self.file = open(self.file_path)

    def close(self):
        if self.file:
            self.file.close()

    def default_is_line_relevant(self, line):
        is_comment = any(word in line for word in ['BEAGLE', 'I', '=', 'PYTHIA'])
        return not is_comment

    def default_is_event(self, tokens):
        return len(tokens) != self.particle_tokens_len  # Beagle event header has like 50 tokens, particle like 16

    def default_is_particle(self, tokens):
        return len(tokens) == self.particle_tokens_len

    def events(self, evt_skip: int = 0, evt_take: int = 0):
        """Generator, reads event by event"""

        event: UnparsedTextEvent = UnparsedTextEvent()

        # Number of events processed
        self.event_index = 0

        while True:
            lines = self.file.readlines(self.buffer_size)
            if not lines:
                break
            for line in lines:
                assert isinstance(line, str)
                line = line.strip()

                # Checks if the line is not empty, is comment, or in skip range
                if self._should_skip_line(line):
                    self.line_index += 1
                    continue

                # tokenize line
                #tokens = regex_split(line)
                tokens = line.replace('\t', ' ').split()

                # Is it a beginning of a new event?
                if self.is_event_line(tokens):

                    # It is not the first event, right?
                    if self.last_record_was_particle:

                        try:
                            # Should we skip the event?
                            if evt_skip <= self.event_index:

                                # Select the event
                                yield event

                                # Should we break?
                                if evt_take and evt_take + evt_skip == self.event_index + 1:
                                    return
                        finally:
                            # Whatever we decide
                            # Create a new event class
                            event = UnparsedTextEvent()
                            self.event_index += 1

                    # Add tokens
                    event.start_line_index = self.line_index
                    event.io_event_index = self.event_index
                    event.event_tokens = tokens
                    self.last_record_was_particle = False

                # It is a particle record
                if self.is_particle_line(tokens):
                    self.last_record_was_particle = True
                    event.unparsed_particles.append(tokens)

                # increment line count in the end
                self.line_index += 1

        # End... Do we have some event prepared?
        if event.event_tokens or event.unparsed_particles:
            yield event

        return


    def to_pandas(self, event_fields, particle_fields, chunk_size=0):
        """
        Converts events to pandas data frame.

        If
        """


    def unparsed_events(self):
        """
         Same as events, but events are being overwritten by child classes

        :return: Generator. List(UnparsedTextEvent)
        """

    @property
    def reader_name(self):
        """
        The name of the reader class
        :return: A string with the reader name
        """
        return "generic_reader"

    def _should_skip_line(self, line):
        """Checks if the line is not empty, is comment, or in skip range"""
        if not line:
            return True

        if self.line_index < self.skip_lines:
            return True

        return not self.is_line_relevant(line)
