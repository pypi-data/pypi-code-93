import math
import json
import logging
from pydantic import BaseModel


class GPSPin(BaseModel):
    lat: float
    lng: float
    ts: int

    def to_latlng(self):
        return LatLng(lat=self.lat, lng=self.lng)


"""
cleanse input pins by removing pin b if straightline distance of a-b / duration is more than speed threshold
"""


def cleanse(pins, threshold=8):
    if len(pins) < 3:
        return pins
    speed = 0
    start = pins[0]
    result = [start]
    for pin in pins[1:]:
        end = pin
        if end.ts < start.ts:
            raise ValueError('pins are not in chronological order')
        if end.ts == start.ts:
            continue
        speed = distance(LatLng(lat=start.lat, lng=start.lng), LatLng(
            lat=end.lat, lng=end.lng)) / (end.ts - start.ts)
        if speed <= threshold:
            result.append(end)
            start = end

    return result


def split_trips(pins, sld_tolerance, min_pause_duration):
    result = []
    pauses = []
    if len(pins) < 3:
        return [pins]
    start = None
    last = pins[0]
    trip = [last]
    detecting = []
    mode = 0  # 0: travelling 1: detecting pause 2: pausing
    for pin in pins[1:]:
        if mode == 0:
            if distance(pin.to_latlng(), last.to_latlng()) <= sld_tolerance:
                start = last
                mode = 1
                detecting = [last, pin]
            else:
                trip.append(pin)
        elif mode == 1:
            if distance(pin.to_latlng(), start.to_latlng()) <= sld_tolerance:
                detecting.append(pin)
                if pin.ts - start.ts >= min_pause_duration:
                    mode = 2
                    if len(trip) > 1:
                        result.append(trip)
                    trip = []
            else:  # moving again
                trip.extend(detecting)
                trip.append(pin)
                detecting = []
                mode = 0
        elif mode == 2:
            if distance(pin.to_latlng(), start.to_latlng()) <= sld_tolerance:
                detecting.append(pin)
            else:  # moving again
                pauses.append(detecting)
                detecting = []
                trip = [last, pin]
                mode = 0
        last = pin
        # print(mode,len(trip),len(detecting))
    if mode == 1:  # if we end up detecting, that means no pause at all
        trip.extend(detecting)
    if len(trip) > 0:
        result.append(trip)
    if len(detecting) > 0:
        pauses.append(detecting)
    return result, pauses


class LatLng(BaseModel):
    lat: float
    lng: float


def distance(loc1: LatLng, loc2: LatLng):
    # approximate radius of earth in meter
    R = 6373000

    lat1 = math.radians(loc1.lat)
    lng1 = math.radians(loc1.lng)
    lat2 = math.radians(loc2.lat)
    lng2 = math.radians(loc2.lng)

    dlng = lng2 - lng1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def geojson_to_poly(gjson: str, name: str = None):
    loaded = json.loads(gjson)
    if not name:
        if 'name' in loaded:
            name = loaded['name']
        else:
            name = 'default'
    output = [name]
    features = loaded['features']
    for f in features:
        geometry = f['geometry']
        if geometry['type'] != 'Polygon':
            raise ValueError('only converting from geojson polygon is supported')
        if len(geometry['coordinates']) > 1:
            logging.warn(
                'multiple coordinates of polygon detected, only using first one as exterior definition')
        output.append('area1')
        for coord in geometry['coordinates'][0]:
            output.append(f'\t{coord[0]}\t{coord[1]}')
        output.append('END')
    output.append('END')
    return '\n'.join(output)


def poly_to_geojson(poly: str):
    gjson = {
        'type': 'FeatureCollection',
        'name': 'default',
        'features': [
            {
                'type': 'Feature',
                'properties': {},
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        []
                    ]
                }
            }
        ]
    }
    poly = poly.replace('\t', ' ')
    lines = poly.split('\n')
    gjson['name'] = lines[0].strip()
    for line in lines[2:]:
        if line.strip() == 'END':
            break
        coords = [x for x in line.strip().split(' ') if len(x) > 0]
        gjson['features'][0]['geometry']['coordinates'][0].append(
            [float(coords[0]), float(coords[1])])
    return gjson


def parse_poly(pstr: str):
    result = []
    lines = pstr.split('\n')
    mode = 0
    coords = []
    for line in lines:
        line = line.rstrip()
        line = line.replace('\t', ' ')
        swt = line.startswith(' ')
        if mode == 0 and swt:
            mode = 1  # begin area
        if mode == 1 and swt:
            items = [float(x) for x in line.split(' ') if len(x) > 0]
            if len(items) == 2:
                coords.append([items[0], items[1]])
            else:
                raise ValueError(f'invalid line: {line}')
        if mode == 1 and line == 'END':
            mode = 0
            result.append(coords)
            coords = []
    return result
