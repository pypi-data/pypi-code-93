from unittest import TestCase
from unittest.mock import patch

from magnumapi.tool_adapters.roxie.RoxieToolAdapter import RoxieToolAdapter
from tests.resource_files import create_resources_file_path


class TestRoxieToolAdapter(TestCase):
    @patch("plotly.graph_objects.Figure.show")
    def test_parse_roxie_xml_11T(self, mock_show=None):
        # arrange
        roxie_data_xml_path = create_resources_file_path('resources/geometry/roxie/11T/reference/roxieData11T.xml')
        strand_data = RoxieToolAdapter.parse_roxie_xml(roxie_data_xml_path)

        # act
        RoxieToolAdapter.plotly_results(strand_data)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    def test_parse_roxie_xml_16T_formatted(self):
        # arrange
        roxie_data_xml_path = create_resources_file_path('resources/geometry/roxie/16T/reference/roxieData16T.xml')

        # assert
        with self.assertRaises(IndexError):
            RoxieToolAdapter.parse_roxie_xml(roxie_data_xml_path)

    @patch("plotly.graph_objects.Figure.show")
    def test_parse_roxie_xml_16T_raw(self, mock_show=None):
        # arrange
        roxie_data_xml_path = create_resources_file_path('resources/geometry/roxie/16T/roxieData.xml')
        roxie_data_formatted_xml_path = create_resources_file_path('resources/geometry/roxie/16T/roxieData_formatted.xml')

        # act
        RoxieToolAdapter.correct_xml_file(roxie_data_formatted_xml_path, roxie_data_xml_path)

        strand_data = RoxieToolAdapter.parse_roxie_xml(roxie_data_formatted_xml_path)
        RoxieToolAdapter.plotly_results(strand_data, xlim=(0, 85), ylim=(0, 85))

        # assert
        if mock_show is not None:
            mock_show.assert_called()


