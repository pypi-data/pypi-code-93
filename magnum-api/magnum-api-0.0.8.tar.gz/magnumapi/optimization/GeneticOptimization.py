from abc import ABC, abstractmethod
import json
import os
from shutil import copyfile
from copy import deepcopy
from typing import List

import pandas as pd
import papermill as pm
from papermill.exceptions import PapermillExecutionError
import scrapbook as sb

from numpy.random import randint
from numpy.random import rand
import numpy as np

from magnumapi.optimization.ObjectiveConfig import ObjectiveConfig
from magnumapi.optimization.OptimizationConfig import OptimizationConfig
from magnumapi.optimization.OptimizationNotebookConfig import OptimizationNotebookConfig
from magnumapi.tool_adapters.DirectoryManager import DirectoryManager

class GeneticOptimization(ABC):

    def __init__(self, config: OptimizationConfig, optim_input_df):
        self.n_gen = config.n_gen
        self.n_pop = config.n_pop
        self.r_cross = config.r_cross
        self.r_mut = config.r_mut
        self.logger = []
        self.config = config
        self.optim_input_df = optim_input_df

    def get_logger_df(self):
        return pd.concat(self.logger).reset_index(drop=True)

    def get_mean_fitness_per_generation(self, logger_df: pd.DataFrame) -> pd.DataFrame:
        mean_logger_dfs = []
        for index in range(0, len(logger_df), self.n_pop):
            sub_logger_df = logger_df[(logger_df.index >= index) & (logger_df.index < index + self.n_pop)]
            sub_logger_df = sub_logger_df[sub_logger_df['fitness'] < 1e7]
            mean_logger_dfs.append(sub_logger_df['fitness'].mean())
        return pd.DataFrame(mean_logger_dfs, columns=['fitness'])

    def get_min_fitness_per_generation(self, logger_df: pd.DataFrame) -> pd.DataFrame:
        min_logger_dfs = []
        for index in range(0, len(logger_df), self.n_pop):
            sub_logger_df = logger_df[(logger_df.index >= index) & (logger_df.index < index + self.n_pop)]
            idx_min = sub_logger_df['fitness'].idxmin()
            min_logger_dfs.append(logger_df[logger_df.index == idx_min])
        return pd.concat(min_logger_dfs).reset_index()

    def initialize_folder_structure(self):
        DirectoryManager.create_directory_if_nonexistent(self.config.output_folder)
        subdirectory_name = DirectoryManager.find_output_subdirectory_name(self.config.output_folder)
        output_subdirectory_dir = os.path.join(self.config.output_folder, subdirectory_name)

        DirectoryManager.create_directory_if_nonexistent(output_subdirectory_dir)
        DirectoryManager.copy_model_input(self.config.input_folder, 'input', output_subdirectory_dir)
        DirectoryManager.copy_notebook_folders(self.config.input_folder, self.config.notebooks, output_subdirectory_dir)
        DirectoryManager.create_directory_if_nonexistent(os.path.join(output_subdirectory_dir, 'optimization'))
        DirectoryManager.copy_model_input(self.config.input_folder, 'optimization', output_subdirectory_dir)

        logger_path = os.path.join(output_subdirectory_dir, self.config.logger_rel_path)
        print('The logger is saved in: %s' % logger_path)

        for config_notebook in self.config.notebooks:
            input_ipynb_file_path = os.path.join(output_subdirectory_dir,
                                                 config_notebook.notebook_folder,
                                                 config_notebook.notebook_name)
            output_ipynb_file_path = os.path.join(output_subdirectory_dir,
                                                  config_notebook.notebook_folder,
                                                  config_notebook.notebook_name.lower().replace('.ipynb', '.py'))
            GeneticOptimization.convert_notebook_to_function(input_ipynb_file_path,
                                                             config_notebook.notebook_name.lower().split('.')[0],
                                                             output_ipynb_file_path)

        return output_subdirectory_dir

    # tournament selection
    @staticmethod
    def selection(pop, scores, k=3):
        # first random selection
        selection_ix = randint(len(pop))
        for ix in randint(0, len(pop), k - 1):
            # check if better (e.g. perform a tournament)
            if scores[ix] < scores[selection_ix]:
                selection_ix = ix
        return pop[selection_ix]

    # crossover two parents to create two children
    def crossover(self, p1, p2):
        # children are copies of parents by default
        c1, c2 = p1.copy(), p2.copy()
        # check for recombination
        if rand() < self.r_cross:
            # select crossover point that is not on the end of the string
            pt = randint(1, len(p1) - 2)
            # perform crossover
            c1 = p1[:pt] + p2[pt:]
            c2 = p2[:pt] + p1[pt:]
        return [c1, c2]

    # mutation operator
    def mutation(self, bitstring):
        for i in range(len(bitstring)):
            # check for a mutation
            if rand() < self.r_mut:
                # flip the bit
                bitstring[i] = 1 - bitstring[i]

    def calculate_figures_of_merit_for_notebooks(self, output_subdirectory_dir):
        fom_dct = {}

        for notebook_config in self.config.notebooks:

            notebook_folder = notebook_config.notebook_folder
            notebook_name = notebook_config.notebook_name
            notebook_dir = os.path.join(output_subdirectory_dir, notebook_folder)
            # copy artefacts
            for dest, source in notebook_config.input_artefacts.items():
                copyfile(os.path.join(output_subdirectory_dir, source),
                         os.path.join(notebook_dir, dest))

            # set parameters
            parameters_dct = {'full_output': False}
            for dest, source in notebook_config.input_parameters.items():
                parameters_dct[dest] = fom_dct[source]

            # execute notebook
            notebook_path = os.path.join(notebook_dir, notebook_name)
            notebook_name_split = notebook_name.split('.')
            out_notebook_name = '%s_out.%s' % tuple(notebook_name_split)

            out_notebook_path = os.path.join(output_subdirectory_dir, notebook_folder, out_notebook_name)

            try:
                pm.execute_notebook(notebook_path, out_notebook_path, cwd=notebook_dir, parameters=parameters_dct)
            except PapermillExecutionError as e:
                # on error pass the message
                return e.exec_count, e.source, e.traceback[-1]
            except Exception as exception:
                raise Exception(exception)

            # fetch figure of merit
            fom_model = sb.read_notebook(out_notebook_path).scraps['model_results'].data
            fom_dct = {**fom_dct, **fom_model}

        return fom_dct

    @staticmethod
    def initialize_config(json_path) -> OptimizationConfig:

        with open(json_path) as f:
            data = json.load(f)

        input_folder = data['input_folder']
        output_foler = data['output_folder']
        logger_rel_path = data['logger_rel_path']
        n_pop = data['n_pop']
        n_gen = data['n_gen']
        r_cross = data['r_cross']
        r_mut = data['r_mut']
        objectives = [ObjectiveConfig(**ff) for ff in data['objectives']]
        notebooks = [OptimizationNotebookConfig(**nb) for nb in data['notebooks']]

        return OptimizationConfig(input_folder=input_folder,
                                  output_folder=output_foler,
                                  logger_rel_path=logger_rel_path,
                                  n_pop=n_pop,
                                  n_gen=n_gen,
                                  r_cross=r_cross,
                                  r_mut=r_mut,
                                  objectives=objectives,
                                  notebooks=notebooks)

    def optimize(self,
                 block_inputs,
                 model_input_path,
                 output_subdirectory_dir,
                 is_script_executed=True,
                 n_elite=2):

        # initial population of random bitstring
        pop = [RoxieGeneticOptimization.generate_random_chromosome(self.optim_input_df) for _ in range(self.n_pop)]
        # keep track of best solution
        best, best_eval = 0, float('inf')

        # enumerate generations
        for gen in range(self.n_gen):
            print('Generation:', gen)
            # decode population
            scores = []

            for index, chromosome in enumerate(pop):
                print('\tIndividual:', index)
                decoded_chromosome = self.decode_chromosome(chromosome)
                updated_block_inputs = self.update_parameters(block_inputs, decoded_chromosome)

                # write updated input
                with open(model_input_path, 'w') as file:
                    json.dump(updated_block_inputs, file, sort_keys=True, indent=4)

                # evaluate figures of merit
                if is_script_executed:
                    fom_dct = self.calculate_figures_of_merit_for_scripts(output_subdirectory_dir)
                else:
                    fom_dct = self.calculate_figures_of_merit_for_notebooks(output_subdirectory_dir)
                    if isinstance(fom_dct, tuple):
                        print(fom_dct[0])
                        print(fom_dct[1])
                        print(fom_dct[2])

                if isinstance(fom_dct, dict):
                    score = self.calculate_fitness(fom_dct)
                else:
                    score = 10e6
                    fom_dct = {'b3': float('nan'), 'b5': float('nan'), 'margmi': float('nan'), 'bigb': float('nan'),
                               'seqv': float('nan')}

                scores.append(score)

                self.logger.append(pd.DataFrame({**decoded_chromosome, **fom_dct, **{'fitness': score}}, index=[0]))

            # evaluate all candidates in the population
            print(sorted(scores))

            # check for new best solution
            for i in range(self.n_pop):
                if scores[i] < best_eval:
                    best, best_eval = pop[i], scores[i]

            print(">%d, new best f(%s) = %f" % (gen, best, best_eval))

            # elitism - keep best two forward
            # # sort according to the best result
            pop_sorted = [pop_el for _, pop_el in sorted(zip(scores, pop))]
            scores_sorted = [score_el for score_el, _ in sorted(zip(scores, pop))]

            # take two from pop and scores
            elite = pop_sorted[:n_elite]

            # select parents
            selected = [self.selection(pop_sorted, scores_sorted) for _ in range(self.n_pop - n_elite)]

            # create the next generation
            children = list()
            for i in range(0, self.n_pop - n_elite, 2):
                # get selected parents in pairs
                p1, p2 = selected[i], selected[i + 1]
                # crossover and mutation
                for c in self.crossover(p1, p2):
                    # mutation
                    self.mutation(c)
                    # store for next generation
                    children.append(c)

            # replace population
            pop = elite + children

            output_table_path = os.path.join(output_subdirectory_dir, self.config.logger_rel_path)
            self.get_logger_df().to_csv(output_table_path)

    def calculate_figures_of_merit_for_scripts(self, output_subdirectory_dir):
        fom_dct = {}

        for notebook_config in self.config.notebooks:
            notebook_folder = notebook_config.notebook_folder
            notebook_name = notebook_config.notebook_name
            notebook_dir = os.path.join(output_subdirectory_dir, notebook_folder)

            # copy artefacts
            for dest, source in notebook_config.input_artefacts.items():
                copyfile(os.path.join(output_subdirectory_dir, source),
                         os.path.join(notebook_dir, dest))

            # set parameters
            parameters_dct = {'full_output': False}
            for dest, source in notebook_config.input_parameters.items():
                parameters_dct[dest] = fom_dct[source]

            # execute script
            notebook_name = notebook_name.split('.')[0].lower()
            cwd = os.getcwd()
            os.chdir(notebook_dir)
            run = getattr(__import__(notebook_name), 'run_' + notebook_name)
            print('Running %s script' % notebook_name)
            try:
                fom_model = run(**parameters_dct)
            except Exception as exception:
                print(exception)
                return str(exception)
            os.chdir(cwd)

            fom_dct = {**fom_dct, **fom_model}

        return fom_dct

    @staticmethod
    def convert_notebook_to_function(input_ipynb_file_path, notebook_name, output_ipynb_file_path):
        with open(input_ipynb_file_path, 'r') as file:
            notebook = json.load(file)

        parameters = []
        code_lines = []
        output_line = ''
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                if 'tags' in cell['metadata']:
                    if 'parameters' in cell['metadata']['tags']:
                        for line in cell['source']:
                            parameters.append(line)
                else:
                    for line in cell['source']:
                        if 'sb.glue' in line:
                            output_line = line
                        else:
                            code_lines.append(line.replace('\n', ''))

        output_var = output_line.split(',')[1]
        if '=' in output_var:
            output_var = output_var.split('=')[-1]

        import_lines = []
        function_lines = []

        for code_line in code_lines:
            if code_line.strip().startswith('from') or code_line.strip().startswith('import'):
                import_lines.append(code_line)
            else:
                function_lines.append(code_line)

        output_lines = list(import_lines)

        output_lines.append('\n')

        parameters = [parameter.replace('\n', '') for parameter in parameters]
        output_lines.append('def run_%s(%s):' % (notebook_name, ', '.join(parameters)))

        for function_line in function_lines:
            output_lines.append('\t' + function_line)

        output_lines.append('\t' + 'return ' + output_var)

        with open(output_ipynb_file_path, 'w') as file:
            for output_line in output_lines:
                file.write(output_line + '\n')

    @abstractmethod
    def decode_chromosome(self, chromosome):
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def update_parameters(self, blocks_def, block_variable_value) -> List[dict]:
        raise NotImplementedError('This method is not implemented for this class')

    def calculate_fitness(self, fom_dct):
        fitness = 0
        for objective_config in self.config.objectives:
            fitness += objective_config.weight * (fom_dct[objective_config.objective] - objective_config.constraint)

        return fitness


class RoxieGeneticOptimization(GeneticOptimization):

    def __init__(self, config, optim_input_df):
        super().__init__(config, optim_input_df)

    @staticmethod
    def generate_random_chromosome(optim_input_df):
        chromosome = []
        for index, row in optim_input_df.iterrows():
            n_bits = row['bits']
            gene = randint(0, 2, n_bits)
            chromosome.extend(gene)

        return chromosome

    # decode chromosome
    def decode_chromosome(self, chromosome):
        block_variable_value = {}
        for index, row in self.optim_input_df.iterrows():
            # extract gene
            sum_bits = self.optim_input_df[self.optim_input_df.index < index]['bits'].sum()
            bits = row['bits']
            gene = chromosome[sum_bits: sum_bits + bits]

            # convert bitstring to a string of chars
            chars = ''.join([str(s) for s in gene])

            # convert string to integer
            integer = int(chars, 2)

            # convert to value
            variable_type = row['variable_type']
            xl = row['xl']
            xu = row['xu']
            if variable_type == 'int':
                if xl + integer > xu:
                    value = int(xu)
                else:
                    value = int(xl + integer)
            else:
                value = xl + integer * (xu - xl) / 2 ** bits

            variable = row['variable']
            block = row['bcs']
            block_variable_value["%d:%s" % (block, variable)] = value

        return block_variable_value

    def update_parameters(self, blocks_def, block_variable_value):
        blocks_def_update = deepcopy(blocks_def)
        for block_variable, value in block_variable_value.items():
            if ':' in block_variable:
                block, variable = block_variable.split(':')
                block = int(block)

                blocks_def_update[block - 1][variable] = value

        blocks_def_update = [block for block in blocks_def_update if block['nco'] > 0]

        return blocks_def_update
