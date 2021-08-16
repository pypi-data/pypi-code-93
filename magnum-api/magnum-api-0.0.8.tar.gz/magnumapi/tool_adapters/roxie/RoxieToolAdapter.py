import os
import platform
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET

import pandas as pd
import numpy as np
import plotly.express as px

from magnumapi.tool_adapters.ToolAdapter import ToolAdapter
import magnumapi.tool_adapters.roxie.RoxieAPI as RoxieAPI

print('Loaded Tool Adapter version 0.0.1 for ROXIE VERS.10, UPDATE 3.1, 2015')


class RoxieToolAdapter(ToolAdapter):
    # ROXIE API shall be static - as in cosim

    def __init__(self, data_file_path: str, output_file_path: str) -> None:
        self.data_file_path = data_file_path
        self.output_file_path = output_file_path
        self.output_lines = []

    def run(self) -> None:
        # if input.output file exists, delete it before running the model
        if os.path.isfile(self.output_file_path):
            os.remove(self.output_file_path)

        # Different execution modes depending on the operating system
        if platform.system() == 'Windows':
            command = ['docker', 'exec', '-d', 'roxie_terminal', 'runroxie', self.data_file_path]
        else:
            command = ['runroxie', self.data_file_path]

        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        byte_output, err = p.communicate(b"input data that is passed to subprocess' stdin")
        rc = p.returncode

        byte_output_decode = byte_output.decode()
        self.output_lines = byte_output_decode.split('\n')

        # ToDo in case the output file was not generated, display output

    def display_output(self) -> None:
        for output_line in self.output_lines:
            print(output_line)

    @staticmethod
    def convert_figures_of_merit_to_dict(fom_df: pd.DataFrame) -> dict:
        b3 = fom_df[(fom_df.index == 'B') & (fom_df['S1'] == 3)]['OBJECTIVE.1'].values[0]
        b5 = fom_df[(fom_df.index == 'B') & (fom_df['S1'] == 5)]['OBJECTIVE.1'].values[0]
        margmi = fom_df[fom_df.index == 'MARGMI']['OBJECTIVE.1'].values[0]
        bigb = fom_df[fom_df.index == 'BIGB']['OBJECTIVE.1'].values[0]

        return {'b3': b3, 'b5': b5, 'margmi': margmi, 'bigb': bigb}

    def read_figures_of_merit_table(self) -> pd.DataFrame:
        N_OBJECTIVES_KEYWORD = 'NUMBER OF OBJECTIVES AND CONSTRAINTS'
        output_file = open(self.output_file_path, 'r')
        output_lines = output_file.read().split('\n')
        output_file.close()
        idx_start_obj_table, n_objectives = RoxieAPI.find_index_start_and_length_objective_table(output_lines,
                                                                                                 N_OBJECTIVES_KEYWORD)
        objective_table_df = RoxieAPI.extract_objective_table(output_lines, idx_start_obj_table, n_objectives)
        return objective_table_df

    @staticmethod
    def parse_roxie_xml(file_path: str) -> pd.DataFrame:
        mytree = ET.parse(file_path)
        mytree.getroot().get('x')

        x_values = []
        y_values = []

        for type_tag in mytree.getroot().findall('loop/step/loop/step/loop/coilGeom/strands/p'):
            x_value = float(type_tag.get('x'))
            y_value = float(type_tag.get('y'))
            x_values.append(x_value)
            y_values.append(y_value)

        x_strands = []
        y_strands = []
        for i in range(0, len(x_values), 4):
            x_strands.append(np.mean(x_values[i:i + 4]))
            y_strands.append(np.mean(y_values[i:i + 4]))

        if not mytree.getroot().findall('loop/step/loop/step/loop/step/coilData'):
            raise IndexError('The XML file does not contain coilData with results. '
                             'Please enable plotting in the ROXIE file')

        data_str = mytree.getroot().findall('loop/step/loop/step/loop/step/coilData')[0].text\
            .replace(';', '').split('\n')
        data = []
        for data_el in data_str:
            if ',' in data_el:
                data.append(float(data_el.split(',')[1]))

        return pd.DataFrame({'x, [mm]': x_strands, 'y, [mm]': y_strands, '|B| (T)': data})

    @staticmethod
    def plotly_results(strand_data: pd.DataFrame, xlim=(0, 80), ylim=(0, 80)) -> None:
        roxie = ['rgb(17,0,181)', 'rgb(11,42,238)', 'rgb(0,104,236)', 'rgb(0,154,235)', 'rgb(0,208,226)',
                 'rgb(0,246,244)', 'rgb(0,255,0)', 'rgb(116,255,0)', 'rgb(191,255,0)', 'rgb(252,255,0)',
                 'rgb(255,199,0)', 'rgb(255,146,0)', 'rgb(255,86,0)', 'rgb(255,0,0)', 'rgb(246,0,0)',
                 'rgb(232, 0, 0)', 'rgb(197, 0, 50)', 'rgb(168, 0, 159)']

        fig = px.scatter(strand_data, x="x, [mm]", y="y, [mm]", color="|B| (T)", hover_data=['|B| (T)'],
                         color_continuous_scale=roxie)
        fig.update_layout(autosize=False,
                          width=750,
                          height=600,
                          xaxis_range=xlim,
                          yaxis_range=ylim,
                          plot_bgcolor='rgba(0,0,0,0)',
                          images=[dict(
                              source="https://i.ibb.co/kcc2mbw/ROXIE.png",
                              xref="paper", yref="paper",
                              x=1.16, y=-0.1,
                              sizex=0.2, sizey=0.2,
                              xanchor="right", yanchor="bottom"
                          )])
        fig.show()

    @staticmethod
    def update_force2d_with_field_scaling(roxie_force_input_path, roxie_force_output_path, field, target_field):
        with open(roxie_force_input_path, 'r') as file_read:
            roxie_force_txt = file_read.readlines()

        # # convert text input to a list of floats
        scaling = (field / target_field) ** 2
        roxie_force = []
        for roxie_force_txt_el in roxie_force_txt:
            row_float = [float(el) for el in roxie_force_txt_el.replace('\n', '').split(' ') if el != '']
            row_float[2] *= scaling
            row_float[3] *= scaling
            roxie_force.append(row_float)

        with open(roxie_force_output_path, 'w') as file_write:
            for roxie_force_el in roxie_force:
                row_str = [str(roxie_force_el_el) for roxie_force_el_el in roxie_force_el]
                file_write.write(' '.join(row_str) + '\n')

    @staticmethod
    def correct_xml_file(input_xml_path, output_xml_path) -> None:
        with open(input_xml_path, 'r') as file:
            xml_lines = file.read()
        # get rid of an extra line and a starting empty space
        if xml_lines[:2] == '\n ':
            xml_lines = xml_lines[2:]

        with open(output_xml_path, 'w') as file:
            file.write(xml_lines)
