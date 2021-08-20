import json
import ast
from unittest import TestCase

from magnumapi.optimization.GeneticOptimization import GeneticOptimization
from tests.resource_files import create_resources_file_path


class TestGeneticOptimization(TestCase):
    def test_initialize_config(self):
        # arrange
        json_file_path = create_resources_file_path('resources/optimization/config.json')

        # act
        optimization_cfg = GeneticOptimization.initialize_config(json_file_path)

        # assert
        self.assertEqual('/home/mmaciejewski/gitlab/magnum-nb/', optimization_cfg.input_folder)
        self.assertEqual('/home/mmaciejewski/gitlab/magnum-nb/output/', optimization_cfg.output_folder)
        self.assertEqual('optimization/GeneticOptimization.csv', optimization_cfg.logger_rel_path)

        self.assertEqual(100, optimization_cfg.n_gen)
        self.assertEqual(20, optimization_cfg.n_pop)
        self.assertAlmostEqual(0.9, optimization_cfg.r_cross, places=1)
        self.assertAlmostEqual(0.01, optimization_cfg.r_mut, places=2)

        self.assertEqual('b3', optimization_cfg.objectives[0].objective)
        self.assertAlmostEqual(0.1, optimization_cfg.objectives[0].weight, places=1)
        self.assertAlmostEqual(0.0, optimization_cfg.objectives[0].constraint, places=1)

        self.assertEqual('b5', optimization_cfg.objectives[1].objective)
        self.assertAlmostEqual(0.1, optimization_cfg.objectives[1].weight, places=1)
        self.assertAlmostEqual(0.0, optimization_cfg.objectives[1].constraint, places=1)

        self.assertEqual('margmi', optimization_cfg.objectives[2].objective)
        self.assertAlmostEqual(1, optimization_cfg.objectives[2].weight, places=0)
        self.assertAlmostEqual(0.85, optimization_cfg.objectives[2].constraint, places=2)

        self.assertEqual('seqv', optimization_cfg.objectives[3].objective)
        self.assertAlmostEqual(0.001, optimization_cfg.objectives[3].weight, places=3)
        self.assertAlmostEqual(0.0, optimization_cfg.objectives[3].constraint, places=1)

        self.assertEqual('geometry', optimization_cfg.notebooks[0].notebook_folder)
        self.assertEqual('Geometry.ipynb', optimization_cfg.notebooks[0].notebook_name)
        self.assertEqual({}, optimization_cfg.notebooks[0].input_parameters)
        self.assertEqual([], optimization_cfg.notebooks[0].output_parameters)
        self.assertEqual({}, optimization_cfg.notebooks[0].input_artefacts)
        self.assertEqual([], optimization_cfg.notebooks[0].output_artefacts)

        self.assertEqual('magnetic', optimization_cfg.notebooks[1].notebook_folder)
        self.assertEqual('ROXIE.ipynb', optimization_cfg.notebooks[1].notebook_name)
        self.assertEqual({}, optimization_cfg.notebooks[1].input_parameters)
        self.assertEqual(['b3', 'b5', 'bigb', 'margmi'], optimization_cfg.notebooks[1].output_parameters)
        self.assertEqual({}, optimization_cfg.notebooks[1].input_artefacts)
        self.assertEqual(['magnetic/input/roxie_scaled.force2d'],
                         optimization_cfg.notebooks[1].output_artefacts)

        self.assertEqual('mechanical', optimization_cfg.notebooks[2].notebook_folder)
        self.assertEqual('ANSYS.ipynb', optimization_cfg.notebooks[2].notebook_name)
        self.assertEqual({}, optimization_cfg.notebooks[2].input_parameters)
        self.assertEqual(['seqv', 'sxmn', 'syin', 'symn', 'syou'], optimization_cfg.notebooks[2].output_parameters)
        self.assertEqual({'input/roxie_scaled.force2d': 'magnetic/input/roxie_scaled.force2d'},
                         optimization_cfg.notebooks[2].input_artefacts)
        self.assertEqual([], optimization_cfg.notebooks[2].output_artefacts)

        self.assertEqual('thermal', optimization_cfg.notebooks[3].notebook_folder)
        self.assertEqual('MIITs.ipynb', optimization_cfg.notebooks[3].notebook_name)
        self.assertEqual({'peak_field': 'bigb'}, optimization_cfg.notebooks[3].input_parameters)
        self.assertEqual(['T_hotspot'], optimization_cfg.notebooks[3].output_parameters)
        self.assertEqual({}, optimization_cfg.notebooks[3].input_artefacts)
        self.assertEqual([], optimization_cfg.notebooks[3].output_artefacts)

    def test_str_config(self):
        # arrange
        json_file_path = create_resources_file_path('resources/optimization/config.json')

        # act
        optimization_cfg = GeneticOptimization.initialize_config(json_file_path)

        # assert
        str_repr_ref_path = create_resources_file_path('resources/optimization/config_str_representation_ref.txt')

        with open(str_repr_ref_path, 'r') as file:
            str_repr_ref = file.read()

        self.assertEqual(str_repr_ref, str(optimization_cfg))