import os
from subprocess import Popen, PIPE

import pandas as pd

from magnumapi.tool_adapters.ToolAdapter import ToolAdapter

print('Loaded Tool Adapter version 0.0.1 for ANSYS2020R2')


class AnsysToolAdapter(ToolAdapter):

    def __init__(self,
                 ansys_path: str,
                 rel_dir: str,
                 inp_path: str,
                 out_path: str,
                 output_file: str
                 ) -> None:
        self.ansys_path = ansys_path
        self.rel_dir = rel_dir
        self.inp_path = inp_path
        self.out_path = out_path
        self.output_file = output_file
        self.output_lines = []

    def run(self) -> None:
        if os.path.isfile(self.output_file):
            os.remove(self.output_file)

        p = Popen([self.ansys_path, '-b', '-p', '-aa_r', '-smp', '-np', '2', '-lch', '-dir', self.rel_dir, '-i',
                   self.inp_path, '-o', self.out_path],
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)
        byte_output, err = p.communicate(b"input data that is passed to subprocess' stdin")
        rc = p.returncode

        byte_output_decode = byte_output.decode()
        self.output_lines = byte_output_decode.split('\n')

    def read_figures_of_merit_table(self) -> pd.DataFrame:
        with open(self.output_file, 'r') as output:
            output_file_content = output.read().split('\n')

        keys = output_file_content[0].split(' ')
        keys = [key for key in keys if key != '']

        values = output_file_content[1].split(' ')
        values = [float(value) for value in values if value != '']

        key_value = {key: value for key, value in zip(keys, values)}
        return pd.DataFrame(key_value, index=[0])

    @staticmethod
    def convert_figures_of_merit_to_dict(fom_df: pd.DataFrame) -> dict:
        return fom_df.to_dict('records')[0]

    @staticmethod
    def prepare_force_file(force_input_path, force_output_path):
        with open(force_input_path, 'r') as file_read:
            force_txt = file_read.readlines()

        ansys_force = []
        for force_txt_el in force_txt:
            row_float = [float(el) for el in force_txt_el.replace('\n', '').split(' ') if el != '']
            ansys_force.append('nodeNum = NODE(%f, %f, 0.0)' % tuple(row_float[:2]))
            ansys_force.append('F,nodeNum,FX, %f' % row_float[2])
            ansys_force.append('F,nodeNum,FY, %f' % row_float[3])

        with open(force_output_path, 'w') as file_write:
            for ansys_force_el in ansys_force:
                file_write.write(ansys_force_el + '\n')
