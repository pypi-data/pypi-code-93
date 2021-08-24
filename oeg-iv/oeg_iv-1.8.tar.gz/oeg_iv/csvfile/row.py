# -*- coding: utf-8 -*-
"""InspectionViewer export csv file data row."""
from ..py23 import win1251, is_contains, replace1251
from .. import (
  Error, ObjectClass, TypeMarker, TypeHorWeld, COMMON, LINEOBJ, SEAM, DEFEKTS,
)

REVERSE_MARKER = {
  TypeMarker.CASE_START: TypeMarker.CASE_END,
  TypeMarker.CASE_END: TypeMarker.CASE_START,
  TypeMarker.TURN_START: TypeMarker.TURN_END,
  TypeMarker.TURN_END: TypeMarker.TURN_START,
}
REVERSE_COMMENTS = {
  'лево': 'право',
  'право': 'лево',
  'начало': 'конец',
  'конец': 'начало',
}


def iv_bool(val):
    """Bool value for IV csv."""
    return win1251('ИСТИНА' if val else 'ЛОЖЬ')


def to_int(text):
    """Convert text to int."""
    return int(round(float(text.strip().replace(',', '.')), 0))


def reverse_orient(orient_str):
    """Reverse orientation of string in format "hours,minutes"."""
    if not orient_str:
        return orient_str

    hours_str = orient_str
    minutes_str = '0'
    if ',' in orient_str:
        hours_str, minutes_str = orient_str.split(',')

    if hours_str == '12':
        hours_str = '0'

    if len(minutes_str) == 1:
        minutes_str += '0'

    minutes = 60 - int(minutes_str)
    hours = 12 - int(hours_str)
    if minutes == 60:
        minutes = 0
    else:
        hours -= 1

    if minutes < 10:
        minutes = '0{}'.format(minutes)

    return "{},{}".format(hours, minutes)


class Row:  # pylint: disable=too-many-instance-attributes
    """Row of export csv file."""

    def __init__(self):
        """Create empty csv row object."""
        self.dist_od = None
        self.type_object = None
        self.object_code = 0
        self.object_name = ''
        self.object_code_t = ''
        self.marker = iv_bool(False)
        self.length = ''
        self.width = ''
        self.depth_min = ''
        self.depth_max = ''
        self.orient_td = ''
        self.orient_bd = ''
        self.mpoint_orient = ''
        self.mpoint_dist = ''
        self.type_def = ''
        self.dist_ml = ''
        self.dist_mr = ''
        self.dist_stl = ''
        self.dist_str = ''
        self.link_stl = ''
        self.link_str = ''
        self.link_ml = ''
        self.link_mr = ''
        self.comments = ''
        self.latitude = ''
        self.longtitude = ''
        self.altitude = ''

    def __str__(self):
        """String representation for row object."""
        return ';'.join([str(i) for i in self.values()])

    def set_geo(self, latitude, longtitude, altitude):
        """Set geo coords for object."""
        if latitude and longtitude and altitude:
            self.latitude = latitude
            self.longtitude = longtitude
            self.altitude = altitude

        return self

    @classmethod
    def with_dist(cls, distanse, latitude='', longtitude='', altitude=''):
        """Construct row as common object with dist and geo."""
        obj = cls()
        obj.dist_od = int(distanse)

        return obj.set_geo(latitude, longtitude, altitude)

    @classmethod
    def as_common(cls, distanse, typ, latitude='', longtitude='', altitude=''):
        """Construct row as common object."""
        obj = cls.with_dist(distanse, latitude, longtitude, altitude)
        obj.type_object = typ
        obj.object_code_t = COMMON[obj.type_object]
        return obj

    @classmethod
    def as_weld(cls, distanse, custom_number='', latitude='', longtitude='', altitude=''):
        """Construct row as weld object."""
        obj = cls.as_common(distanse, ObjectClass.WELD, latitude, longtitude, altitude)
        if custom_number:
            obj.object_name = custom_number.encode('windows-1251')

        return obj

    @classmethod
    def as_thick(cls, distanse, thick, latitude='', longtitude='', altitude=''):
        """Construct row as thickness change object."""
        obj = cls.as_common(distanse, ObjectClass.THICK, latitude, longtitude, altitude)
        obj.depth_max = thick
        return obj

    @classmethod
    def as_category(cls, distanse, category, latitude='', longtitude='', altitude=''):
        """Construct row as pipeline category object."""
        obj = cls.as_common(distanse, ObjectClass.PIPELINE_CATEGORY, latitude, longtitude, altitude)
        obj.depth_max = category
        return obj

    @classmethod
    def as_seam(cls, distanse, typ, orient1, orient2):
        """Construct row as seam object with given typ."""
        if typ not in SEAM:
            raise Error("Wrong seam type: {}".format(typ))

        obj = cls.with_dist(distanse, '', '', '')
        obj.type_object = ObjectClass.HOR_WELD
        obj.object_code = typ
        obj.object_code_t = SEAM[obj.object_code]

        if obj.object_code in [TypeHorWeld.HORIZONTAL, TypeHorWeld.SPIRAL, TypeHorWeld.SECOND]:
            obj.orient_td = str(orient1)

        if obj.object_code in [TypeHorWeld.SECOND]:
            obj.orient_bd = str(orient2)

        return obj

    @classmethod
    def as_lineobj(cls, distanse, typ, name, is_marker, comment, latitude='', longtitude='', altitude=''):
        """Construct row as line object."""
        obj = cls.with_dist(distanse, latitude, longtitude, altitude)
        obj.type_object = ObjectClass.MARKER
        obj.object_code = typ
        obj.object_code_t = LINEOBJ[typ]
        obj.object_name = name
        obj.marker = iv_bool(is_marker)
        obj.comments = comment

        return obj

    @classmethod
    def as_defekt(  # pylint: disable=too-many-locals
      cls, distanse, typ, side, length, width, depth, orient1, orient2, mp_orient, mp_dist, comment,
      latitude='', longtitude='', altitude=''
    ):
        """Construct row as defekt object."""
        if typ not in DEFEKTS:
            raise Error("Wrong defekt type: {}".format(typ))

        depth_int = to_int(depth)

        obj = cls.with_dist(distanse, latitude, longtitude, altitude)
        obj.type_object = ObjectClass.DEFEKT
        obj.object_code = typ
        obj.object_code_t = DEFEKTS[typ]

        if orient1:
            obj.orient_td = str(orient1)
        if orient2:
            obj.orient_bd = str(orient2)

        obj.length = length
        obj.width = width
        obj.depth_min = depth_int
        obj.depth_max = depth_int
        obj.type_def = side

        if mp_orient:
            obj.mpoint_orient = str(mp_orient)
        if mp_dist:
            obj.mpoint_dist = mp_dist

        obj.comments = comment

        return obj

    @classmethod
    def from_csv_row(cls, row):
        """Construct from csv row."""
        obj = cls()

        obj.dist_od = row[0]
        obj.type_object = row[1]
        obj.object_code = row[2]
        obj.object_name = row[3]
        obj.object_code_t = row[4]
        obj.marker = row[5]
        obj.length = row[6]
        obj.width = row[7]
        obj.depth_min = row[8]
        obj.depth_max = row[9]
        obj.orient_td = row[10]
        obj.orient_bd = row[11]
        obj.mpoint_orient = row[12]
        obj.mpoint_dist = row[13]
        obj.type_def = row[14]
        obj.dist_ml = row[15]
        obj.dist_mr = row[16]
        obj.dist_stl = row[17]
        obj.dist_str = row[18]
        obj.link_stl = row[19]
        obj.link_str = row[20]
        obj.link_ml = row[21]
        obj.link_mr = row[22]
        obj.comments = row[23]
        obj.latitude = row[24]
        obj.longtitude = row[25]
        obj.altitude = row[26]

        return obj

    def values(self):
        """Column values for row."""
        return [
          self.dist_od,
          self.type_object,
          self.object_code,
          self.object_name,
          self.object_code_t,
          self.marker,
          self.length,
          self.width,
          self.depth_min,
          self.depth_max,
          self.orient_td,
          self.orient_bd,
          self.mpoint_orient,
          self.mpoint_dist,
          self.type_def,
          self.dist_ml,
          self.dist_mr,
          self.dist_stl,
          self.dist_str,
          self.link_stl,
          self.link_str,
          self.link_ml,
          self.link_mr,
          self.comments,
          self.latitude,
          self.longtitude,
          self.altitude,
        ]

    def copy(self):
        """Create copy of row."""
        obj = Row()

        obj.dist_od, \
            obj.type_object, \
            obj.object_code, \
            obj.object_name, \
            obj.object_code_t, \
            obj.marker, \
            obj.length, \
            obj.width, \
            obj.depth_min, \
            obj.depth_max, \
            obj.orient_td, \
            obj.orient_bd, \
            obj.mpoint_orient, \
            obj.mpoint_dist, \
            obj.type_def, \
            obj.dist_ml, \
            obj.dist_mr, \
            obj.dist_stl, \
            obj.dist_str, \
            obj.link_stl, \
            obj.link_str, \
            obj.link_ml, \
            obj.link_mr, \
            obj.comments, \
            obj.latitude, \
            obj.longtitude, \
            obj.altitude = self.values()

        return obj

    @property
    def is_category(self):
        """Row is pipeline category object."""
        return int(self.type_object) == ObjectClass.PIPELINE_CATEGORY

    @property
    def is_thick(self):
        """Row is wall thick change object."""
        return int(self.type_object) == ObjectClass.THICK

    @property
    def is_weld(self):
        """Row is weld object."""
        return int(self.type_object) == ObjectClass.WELD

    @property
    def is_defect(self):
        """Row is defect object."""
        return int(self.type_object) == ObjectClass.DEFEKT

    @property
    def is_lineobj(self):
        """Row is line object."""
        return int(self.type_object) == ObjectClass.MARKER

    @property
    def is_seam(self):
        """Row is seam object."""
        return int(self.type_object) == ObjectClass.HOR_WELD

    def reverse(self, total_length):
        """Reverse dist, orientation and start point if objects with length."""
        my_length = 0
        if self.length:
            my_length = int(self.length)

        self.dist_od = str(total_length - int(self.dist_od) - my_length)

        if self.mpoint_dist:
            self.mpoint_dist = str(total_length - int(self.mpoint_dist))

        tmp = self.dist_ml
        self.dist_ml = self.dist_mr
        self.dist_mr = tmp

        tmp = self.dist_stl
        self.dist_str = self.dist_stl
        self.dist_stl = tmp

        tmp = self.link_stl
        self.link_stl = self.link_str
        self.link_str = tmp

        tmp = self.link_ml
        self.link_ml = self.link_mr
        self.link_mr = tmp

        # orientatations
        self.orient_td = reverse_orient(self.orient_td)
        self.orient_bd = reverse_orient(self.orient_bd)

        if int(self.type_object) != ObjectClass.HOR_WELD:
            tmp = self.orient_bd
            self.orient_bd = self.orient_td
            self.orient_td = tmp

        self.mpoint_orient = reverse_orient(self.mpoint_orient)

        # object type
        if int(self.type_object) == ObjectClass.MARKER:
            object_code = int(self.object_code)
            self.object_code = str(REVERSE_MARKER.get(object_code, object_code))

        # comments
        for key, val in REVERSE_COMMENTS.items():
            if is_contains(self.comments, key):
                replace1251(self.comments, key, val)
                break
