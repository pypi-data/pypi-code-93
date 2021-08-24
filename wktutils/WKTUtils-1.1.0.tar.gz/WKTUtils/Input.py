import dateparser
import re
from geomet import wkt, InvalidGeoJSONException


# Parse and validate a date: "1991-10-01T00:00:00Z"
def parse_date_util(v):
    d = dateparser.parse(v)
    if d is None:
        raise ValueError('Invalid date: {0}'.format(v))
    return dateparser.parse(v).strftime('%Y-%m-%dT%H:%M:%SZ')

# Parse a WKT and convert it to a coordinate string
# NOTE: If given an empty ("POINT EMPTY") shape, will return "point:". Should it throw instead?
def parse_wkt_util(v):
    try:
        wkt_json = wkt.loads(str(v).upper())
    except (ValueError, AttributeError, InvalidGeoJSONException) as e:
        raise ValueError('Cannot load WKT: {0}. Error: {1}'.format(v, str(e)))
    # take note of the WKT type
    if wkt_json['type'].upper() not in ["POINT","LINESTRING", "POLYGON"]:
        raise ValueError('Unsupported WKT: {0}.'.format(v))
    
    if wkt_json['type'].upper() == "POLYGON":
        coords = wkt_json['coordinates']
        # If not an empty poly, take out the hole:
        # (Also de-nest it in the process)
        if len(wkt_json['coordinates']) != 0:
            coords = coords[0]
    elif wkt_json['type'].upper() == "LINESTRING":
        coords = wkt_json['coordinates']
    else: # type == POINT
        coords = [wkt_json['coordinates']]
    # Turn [[x,y],[x,y]] into [x,y,x,y]:
    coords = [x for x in sum(coords, [])]
    # Turn any "6e8" to a literal number. (As a sting):
    coords = ['{:.16f}'.format(float(cord)) for cord in coords]
    return '{0}:{1}'.format(wkt_json['type'].lower(), ','.join(coords))
