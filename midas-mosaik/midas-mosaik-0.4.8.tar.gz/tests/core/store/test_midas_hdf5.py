import unittest

from midas.core.store import MidasHdf5


class TestMidasHdf5(unittest.TestCase):
    def setUp(self):
        self.inputs1 = {
            "Database": {
                "p_mw": {
                    "DummySim-0.DummyHousehold-0": 0.02,
                    "DummySim-0.DummyHousehold-1": 0.02,
                    "DummySim-1.DummyPV-0": 0.03,
                },
                "q_mvar": {
                    "DummySim-0.DummyHousehold-0": 0.01,
                    "DummySim-0.DummyHousehold-1": 0.015,
                    "DummySim-1.DummyPV-0": 0.01,
                },
                "t_air": {
                    "DummyWeather-0.WeatherCurrent-0": 15.0,
                },
            }
        }
        self.inputs2 = {
            "Database": {
                "p_mw": {
                    "DummySim-0.DummyHousehold-0": 0.02,
                    "DummySim-0.DummyHousehold-1": 0.02,
                    "DummySim-1.DummyPV-0": 0.03,
                    "DummySim-2.DummyCHP-0": 0.5,
                },
                "q_mvar": {
                    "DummySim-0.DummyHousehold-0": 0.01,
                    "DummySim-0.DummyHousehold-1": 0.015,
                    "DummySim-1.DummyPV-0": 0.01,
                },
                "t_air": {
                    "DummyWeather-0.WeatherCurrent-0": 15.0,
                },
                "wind": {
                    "DummyWeather-1.WeatherForecast-0": 20,
                },
            }
        }

    def test_setup(self):
        dbsim = MidasHdf5()

        dbsim.init("MidasHdf5", step_size=900)

        # Only one instance allowed
        with self.assertRaises(AssertionError):
            dbsim.create(2, "Database", filename="there.hdf5")

        entity = dbsim.create(1, "Database", filename="here.hdf5")

        self.assertIsNotNone(dbsim.database)
        self.assertEqual("here.hdf5", dbsim.filename)
        self.assertEqual(900, dbsim.step_size)

        # Only one instance allowed
        with self.assertRaises(AssertionError):
            dbsim.create(1, "Database", filename="there.hdf5")

    def test_step(self):
        dbsim = MidasHdf5()
        dbsim.init("MidasHdf5", step_size=900)
        dbsim.create(1, "Database", filename="here.hdf5")
        dbsim.step(0, self.inputs1)

        dbsim.step(900, self.inputs2)

        print(dbsim.database["DummySim-0"])


if __name__ == "__main__":
    unittest.main()
