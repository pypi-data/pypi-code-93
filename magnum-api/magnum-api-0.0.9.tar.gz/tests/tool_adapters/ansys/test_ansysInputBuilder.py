import unittest
from unittest.mock import patch

import numpy as np

from magnumapi.geometry.CosThetaGeometry import HomogenizedCosThetaGeometry
from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.geometry.roxie.CableDatabase import CableDatabase
from magnumapi.tool_adapters.ansys.AnsysInputBuilder import AnsysInputBuilder
from tests.resource_files import create_resources_file_path


class TestAnsysInputBuilder(unittest.TestCase):
    @patch("matplotlib.pyplot.show")
    def test_input_file_generation(self, mock_show=None):

        json_path = create_resources_file_path('resources/geometry/roxie/16T/16T_rel.json')
        cadata_path = create_resources_file_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        geometry = GeometryFactory.init_with_json(json_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        homo_geometry = HomogenizedCosThetaGeometry.with_cos_theta_geometry(geometry)

        # Find number of layers
        n_layers = homo_geometry.get_number_of_layers()

        self.assertEqual(4, n_layers)
        # For each layer
        # # Number of blocks per layer
        blocks_per_layer = homo_geometry.get_number_of_blocks_per_layer()
        self.assertListEqual([4, 3, 3, 2], blocks_per_layer)

        # # write inner radius - taken as the minimum radius out of all all radii of a layer
        inner_radii = HomogenizedCosThetaGeometry.get_inner_radii(geometry)

        inner_radii_ref = [25.000000000000004, 39.0, 53.0, 67.45000006216533]
        np.testing.assert_allclose(inner_radii_ref, inner_radii)

        # # write inner radius - taken as the minimum radius out of all radii of a layer
        outer_radii = HomogenizedCosThetaGeometry.get_outer_radii(geometry)

        outer_radii_ref = [38.514032903286974, 52.513971821900164, 66.87212964199654, 81.3221676585706]
        np.testing.assert_allclose(outer_radii_ref, outer_radii)

        output_text = AnsysInputBuilder.prepare_ansys_model_input(homo_geometry)
        output_text_ref_path = create_resources_file_path('resources/tool_adapters/ansys/Model.inp')
        with open(output_text_ref_path, 'r') as file:
            output_text_ref = file.readlines()

        self.assertListEqual(output_text_ref, output_text)

        if mock_show is not None:
            mock_show.assert_called()


if __name__ == '__main__':
    unittest.main()
