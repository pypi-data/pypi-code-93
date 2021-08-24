"""Interfaces for InspectionViewer export csv file."""
import csv
from ..py23 import gen_next, open_text_file
from .. import Error


def transform_length(dist_od, length_od, table, table_index):
    """
    transform_length modify length at given dist according table.

    Get vector (distance, length), table of dist modifications,
    position in this table and return transformed length.
    """
    try:
        length = int(length_od)
        pos = int(dist_od)
    except ValueError:
        return length_od

    if not length:
        return length_od

    _, dist_start = transform_dist(pos, table, table_index)
    _, dist_end = transform_dist(pos + length, table, table_index)

    return dist_end - dist_start


def transform_dist(dist_od, table, table_index):
    """
    transform_dist get distance, table of dist modifications and current position in this table.

    Return new position in table of dist modifications and transformed distance for dist_od.
    """
    try:
        pos = int(dist_od)
    except ValueError:
        return table_index, dist_od

    max_index = len(table) - 2
    left_side = table[table_index]
    right_side = table[table_index + 1]

    while pos > right_side[0]:
        if table_index == max_index:
            break
        table_index += 1
        left_side = table[table_index]
        right_side = table[table_index + 1]

    if pos < left_side[0]:
        pos = left_side[1] - (left_side[0] - pos)

    elif pos == left_side[0]:
        pos = left_side[1]

    elif pos < right_side[0]:
        old_length = right_side[0] - left_side[0]
        new_length = right_side[1] - left_side[1]
        pos = float(pos - left_side[0])
        pos = int(round((pos * new_length) / old_length + left_side[1], 0))

    elif pos == right_side[0]:
        pos = right_side[1]

    else:  # pos > right_side[0]
        pos = right_side[1] + (pos - right_side[0])

    return table_index, pos


class Stream:
    """Holds current state of data stream."""

    def __init__(self):
        """Inital data stream state."""
        self.thick = None
        self.category = None


class FloatDelimiter:
    """Possible float delimiter for output csv."""

    Point = '.'
    Comma = ','


def format_floats(val_list, float_delimiter):
    """Convert floats from val_list to string with given float delimiter."""
    if float_delimiter == FloatDelimiter.Point:
        return val_list

    return [
      str(i).replace('.', float_delimiter) if isinstance(i, float) else i
      for i in val_list
    ]


class File:
    """Export/import csv file."""

    ENCODING = 'windows-1251'
    DELIMETER = ';'
    COLUMN_HEADS = [
      'DistOd',
      'TypeObject',
      'Object_Code',
      'ObjectName',
      'Object_Code_T',
      'Marker',
      'Length',
      'Width',
      'Depth_min',
      'Depth_max',
      'OrientTD',
      'OrientBD',
      'MPoint_Orient',
      'MPoint_Dist',
      'Type_Def',
      'DistML',
      'DistMR',
      'DistStL',
      'DistStR',
      'LinkStL',
      'LinkStR',
      'LinkML',
      'LinkMR',
      'Comments',
      'Latitude',
      'Longtitude',
      'Altitude',
    ]

    def __init__(self, float_delimiter=FloatDelimiter.Point):
        """Create empti csv file object."""
        self.data = []
        self.thicks = []
        self.categories = []
        self.float_delimiter = float_delimiter
        self.stream = Stream()

    @classmethod
    def open_file(cls, file_path, mode):
        """Python 2/3 open file."""
        return open_text_file(file_path, mode, cls.ENCODING)

    @classmethod
    def from_file(cls, file_path, float_delimiter=FloatDelimiter.Point):
        """Construct from export csv file."""
        from .row import Row

        obj = cls(float_delimiter=float_delimiter)
        reader = csv.reader(cls.open_file(file_path, 'r'), delimiter=cls.DELIMETER)
        next(reader)  # skip column titles row
        for row in reader:

            if not row:
                continue

            item = Row.from_csv_row(row)
            obj.data.append(item)
            if item.is_category:
                obj.categories.append(item)
            elif item.is_thick:
                obj.thicks.append(item)

        return obj

    @property
    def total_length(self):
        """Reckord total length."""
        return int(self.data[-1].dist_od)

    def to_file(self, file_path):
        """Save csv to file."""
        output = self.open_file(file_path, 'w')
        writer = csv.writer(output, delimiter=self.DELIMETER)

        writer.writerow(self.COLUMN_HEADS)
        for row in sorted(self.data, key=lambda val: int(val.dist_od)):
            if int(row.type_object) >= 0:
                writer.writerow(format_floats(row.values(), self.float_delimiter))

        output.close()

    def append(self, csv_file):
        """Append data from csv file."""
        length = self.total_length
        for item in csv_file.data:
            item.dist_od = str(int(item.dist_od) + length)
            self.data.append(item)

    def join(self, files):
        """Join several csv files."""
        from .row import Row

        for item in files:
            try:
                tube_length = int(item)
            except ValueError:
                self.append(self.from_file(item))
                continue

            point = Row()
            point.dist_od = str(self.total_length + tube_length)
            point.type_object = -1  # set as ObjectClass.JOIN
            self.data.append(point)

    def reverse(self):
        """Reverse vector of objects."""
        total_length = self.total_length
        for i in self.data:
            i.reverse(total_length)

        self.data.reverse()

        # find index for first weld
        index = None
        for i, item in enumerate(self.data):
            if item.is_weld:
                index = i
                break

        if index is None:
            return

        first_weld = self.data[index]
        base_dist = int(first_weld.dist_od)
        next_dist = int(self.data[index + 1].dist_od)

        # check for duplicate dist
        while (next_dist - base_dist) <= 1:
            index += 1
            base_dist = next_dist
            next_dist = int(self.data[index + 1].dist_od)

        if self.thicks:
            base_dist += 1
            index += 1
            first_thick = self.thicks[-1].copy()
            first_thick.dist_od = str(base_dist)
            self.data.insert(index, first_thick)
            self.data.remove(self.thicks[-1])

        if self.categories:
            base_dist += 1
            index += 1
            first_category = self.categories[-1].copy()
            first_category.dist_od = str(base_dist)
            self.data.insert(index, first_category)
            self.data.remove(self.categories[-1])

    @classmethod
    def load_dist_modify(cls, file_name):
        """Load distance modificatons from file_name."""
        reader = csv.reader(cls.open_file(file_name, 'r'), delimiter=cls.DELIMETER)
        next(reader)  # skip column titles row
        table = []
        for row in reader:
            table.append([int(row[0]), int(row[1])])

        table.sort(key=lambda val: val[0])
        return table

    def dist_modify(self, table):
        """Apply distance modificatons from file_name."""
        table_index = 0
        for row in sorted(self.data, key=lambda val: int(val.dist_od)):

            if int(row.dist_od) < table[table_index][0]:
                raise Error("dist {} < node {}".format(row.dist_od, table[table_index][0]))

            if row.is_defect:
                _, row.mpoint_dist = transform_dist(row.mpoint_dist, table, table_index)
                row.length = transform_length(row.dist_od, row.length, table, table_index)

            table_index, row.dist_od = transform_dist(row.dist_od, table, table_index)

    def _create_tubes_iterator(self, warns):
        """Create iterator for tubes in csv data."""
        from .tubes import Tube

        tube = None
        auto_num = 1
        for row in sorted(self.data, key=lambda val: int(val.dist_od)):
            if row.is_weld:
                if tube:
                    tube.finalize(row.dist_od, warns)
                    auto_num += 1
                yield tube
                tube = Tube(row, self.stream, str(auto_num))
            else:
                if tube:
                    tube.add_object(row)
                else:
                    warns.append("Object before first weld: {}".format(row))

    def get_tubes(self, warns):
        """Return ready iterator for tubes in csv data."""
        tubes = self._create_tubes_iterator(warns)
        gen_next(tubes)
        return tubes
