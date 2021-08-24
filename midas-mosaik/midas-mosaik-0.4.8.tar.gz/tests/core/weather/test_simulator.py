"""Test module for the weather simulator."""
import unittest
from datetime import datetime
from os.path import abspath, join

import pandas as pd
from midas.core.weather.model.provider import WeatherData
from midas.core.weather.simulator import WeatherSimulator
from midas.tools import config

CFG = config.check_config(None)


class TestSimulator(unittest.TestCase):
    """Test class for the weather simulator."""

    def setUp(self):
        datapath = CFG["PATHS"]["data_path"]

        # self.sim = WeatherSimulator()
        self.params = {
            "sid": "TestSimulator-0",
            "step_size": 900,
            "data_path": datapath,
            "start_date": "2018-05-19 14:00:00+0100",
        }

    def test_init(self):
        """Test the init function of the simulator."""

        sim = WeatherSimulator()
        sim.init(**self.params)
        meta = sim.meta

        self.assertIsInstance(meta, dict)
        self.assertIsInstance(sim.wdata, WeatherData)
        self.assertIsInstance(sim.now_dt, datetime)

    def test_create_weather(self):
        """Test to create a weather model."""
        sim = WeatherSimulator()
        sim.init(**self.params)

        entities = sim.create(num=1, model="Weather", interpolate=False)
        self.assertEqual(len(entities), 1)
        for entity in entities:
            self.assertIsInstance(entity, dict)

    def test_create_weather_forecast(self):
        """Test to create a weather forecast model."""
        sim = WeatherSimulator()
        sim.init(**self.params)

        entities = sim.create(
            num=1,
            model="WeatherForecast",
            forecast_horizon_hours=12,
            forecast_error=0,
            seed=0,
            interpolate=False,
        )
        self.assertEqual(len(entities), 1)
        for entity in entities:
            self.assertIsInstance(entity, dict)

    def test_step(self):
        """Test a simulation step with both a weather model and a
        weather forecast model.

        """
        sim = WeatherSimulator()
        sim.init(**self.params)

        sim.create(1, "WeatherCurrent", interpolate=False)
        sim.create(
            1,
            "WeatherForecast",
            forecast_horizon_hours=12,
            forecast_error=0,
            interpolate=False,
            seed=0,
        )

        sim.step(0, {})

        t_air = sim.models["WeatherCurrent-0"].t_air_deg_celsius
        self.assertIsInstance(t_air, float)

        fc_t_air = sim.models["WeatherForecast-1"].forecast_t_air_deg_celsius
        self.assertIsInstance(fc_t_air, pd.DataFrame)

        self.assertEqual(t_air, fc_t_air.iloc[0]["t_air_deg_celsius"])

    def test_get_data(self):
        """Test the get data function of the simulator."""
        sim = WeatherSimulator()
        sim.init(**self.params)

        sim.create(1, "WeatherCurrent", interpolate=False)
        sim.create(
            1,
            "WeatherForecast",
            forecast_horizon_hours=12,
            forecast_error=0,
            interpolate=False,
            seed=0,
        )
        sim.step(0, {})

        outputs = {
            "WeatherCurrent-0": [
                "t_air_deg_celsius",
                "day_avg_t_air_deg_celsius",
            ],
            "WeatherForecast-1": [
                "forecast_bh_w_per_m2",
                "forecast_dh_w_per_m2",
            ],
        }

        data = sim.get_data(outputs)

        self.assertIsInstance(data, dict)
        self.assertEqual(len(data), 2)
        for key, value in data.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, dict)

            for attr, val in value.items():
                self.assertIsInstance(attr, str)
                if "forecast" in attr:
                    self.assertIsInstance(val, pd.DataFrame)
                    self.assertEqual(val.size, 48)
                    self.assertIn(val.columns[0], attr)
                else:
                    self.assertIsInstance(val, float)


if __name__ == "__main__":
    unittest.main()
