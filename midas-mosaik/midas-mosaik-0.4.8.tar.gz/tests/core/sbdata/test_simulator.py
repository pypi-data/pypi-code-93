"""
This module contains the test cases for the simbench data simulator.

"""
import unittest

from midas.core.sbdata import SimbenchDataSimulator
from midas.util.base_data_model import DataModel
from midas.tools import config


CFG = config.check_config(None)


class TestSimulator(unittest.TestCase):
    """Test case for the simbench data simulator."""

    def setUp(self):

        self.sim_params = {
            "sid": "TestSimulator-0",
            "step_size": 900,
            "start_date": "2017-01-01 00:00:00+0100",
            "data_path": CFG["PATHS"]["data_path"],
        }

    def test_init(self):
        sim = SimbenchDataSimulator()
        meta = sim.init(**self.sim_params)

        self.assertIsInstance(meta, dict)

    def test_create(self):

        # Test init
        sim = SimbenchDataSimulator()
        meta = sim.init(**self.sim_params)

        self.assertIsInstance(meta, dict)

        # Test create
        entities = sim.create(3, "Load")
        self.assertEqual(len(entities), 3)
        for entity in entities:
            self.assertIsInstance(entity, dict)
            self.assertIn(entity["eid"], sim.models)
            self.assertIsInstance(sim.models[entity["eid"]], DataModel)

        entity1 = entities[0]

        entities = sim.create(2, "Sgen")
        self.assertEqual(len(entities), 2)
        for entity in entities:
            self.assertIsInstance(entity, dict)
            self.assertIn(entity["eid"], sim.models)
            self.assertIsInstance(sim.models[entity["eid"]], DataModel)

        entities = sim.create(1, "Load", idx=1)
        self.assertEqual(len(entities), 1)
        entity2 = entities[0]

        # Compare with first created load

        # Test step
        sim.step(0, dict())

        print()


if __name__ == "__main__":
    unittest.main()
