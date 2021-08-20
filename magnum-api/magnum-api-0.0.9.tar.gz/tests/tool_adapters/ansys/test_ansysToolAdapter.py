import unittest

from magnumapi.tool_adapters.ansys.AnsysToolAdapter import AnsysToolAdapter
from magnumapi.tool_adapters.roxie.RoxieToolAdapter import RoxieToolAdapter
from tests.resource_files import create_resources_file_path


class TestAnsysToolAdapter(unittest.TestCase):

    def test_roxie_force_to_ansys(self):
        # arrange
        roxie_force_input_path = create_resources_file_path('resources/tool_adapters/ansys/roxie.force2d')
        roxie_force_output_path = create_resources_file_path('resources/tool_adapters/ansys/roxie_edit.force2d')
        ansys_force_output_path = create_resources_file_path('resources/tool_adapters/ansys/forces_edit.vallone')
        field = 15
        target_field = 16

        # act
        # # update ROXIE force file
        RoxieToolAdapter.update_force2d_with_field_scaling(roxie_force_input_path,
                                                           roxie_force_output_path,
                                                           field,
                                                           target_field)

        # # prepare ANSYS force file
        AnsysToolAdapter.prepare_force_file(roxie_force_output_path, ansys_force_output_path)

        # assert
        with open(ansys_force_output_path, 'r') as file:
            ansys_force = file.readlines()

        output_text_ref_path = create_resources_file_path('resources/tool_adapters/ansys/forces_edit_ref.vallone')

        with open(output_text_ref_path, 'r') as file:
            ansys_force_ref = file.readlines()

        for ansys_force_ref_el, ansys_force_el in zip(ansys_force_ref, ansys_force):
            self.assertEqual(ansys_force_ref_el, ansys_force_el)


if __name__ == '__main__':
    unittest.main()
