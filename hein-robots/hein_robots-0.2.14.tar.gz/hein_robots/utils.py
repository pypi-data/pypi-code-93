from unittest import TestCase
from hein_robots.robotics import Location


class HeinRobotsTestCase(TestCase):
    def assertLocationEqual(self, location_a: Location, location_b: Location, places=1):
        self.assertAlmostEqual(location_a.x, location_b.x, places=places)
        self.assertAlmostEqual(location_a.y, location_b.y, places=places)
        self.assertAlmostEqual(location_a.z, location_b.z, places=places)
        self.assertAlmostEqual(location_a.rx, location_b.rx, places=places)
        self.assertAlmostEqual(location_a.ry, location_b.ry, places=places)
        self.assertAlmostEqual(location_a.rz, location_b.rz, places=places)

    def assertListAlmostEqual(self, list_a, list_b, delta=0.01):
        self.assertEqual(len(list_a), len(list_b))

        for i in range(len(list_a)):
            self.assertAlmostEqual(list_a[i], list_b[i], delta=delta)