from . import geo
from .geo import GPSPin, cleanse, split_trips


def test_parse_poly():
    thing = 'who\ncares\n\t1.2\t3.4\n\t5.6\t7.8\nEND\nEND'

    r = geo.parse_poly(thing)
    print(f'r is {r}')
    assert len(r) == 1
    assert r[0][0] == [1.2, 3.4]


def test_parse_poly_file():
    with open('bangalore.poly') as f:
        p = geo.parse_poly(f.read())
        assert len(p) > 0


def test_cleanse():
    trajectory = open('trajectory.txt').read()
    raw = [GPSPin(lat=float(x), lng=float(y), ts=int(z))
           for x, y, z in [item.split(',') for item in trajectory.split(';')]]
    pins = []
    last = None
    for pin in raw:
        if last:
            if pin.ts == last.ts:
                continue
        last = pin
        pins.append(pin)

    r = cleanse(pins)
    assert len(r) != len(pins)


def test_split_1():
    trajectory = '1,1,0;1,2,1;1,2,2;1,2,3;1,2,4;1,2,5;1,2,6;1,2,7;1,2,8;1,3,9;1,4,10'
    pins = [GPSPin(lat=float(x), lng=float(y), ts=int(z)) for x, y, z in [
        item.split(',') for item in trajectory.split(';')]]
    trips, pauses = split_trips(pins, 100, 5)
    print(trips)
    print(pauses)
    assert len(trips) == 2
    assert len(pauses) == 1
    assert len(pauses[0]) == 8


def test_split_2():
    trajectory = '1,1,0;1,2,1;1,2,2;1,2,3;1,2,4;1,2,5;1,2,6;1,2,7;1,2,8;1,3,9;1,4,10'
    pins = [GPSPin(lat=float(x), lng=float(y), ts=int(z)) for x, y, z in [
        item.split(',') for item in trajectory.split(';')]]
    trips, pauses = split_trips(pins, 1000000000, 5)
    print(trips)
    print(pauses)
    assert len(trips) == 0
    assert len(pauses) == 1
    assert len(pauses[0]) == 11


def test_split_3():
    trajectory = '1,1,0;1,2,1;1,2,2;1,2,3;1,2,4;1,2,5;1,2,6;1,2,7;1,2,8;1,3,9;1,4,10'
    pins = [GPSPin(lat=float(x), lng=float(y), ts=int(z)) for x, y, z in [
        item.split(',') for item in trajectory.split(';')]]
    trips, pauses = split_trips(pins, 100, 12)
    print(trips)
    print(pauses)
    assert len(trips) == 1
    assert len(pauses) == 0
