from itertools import accumulate

import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from magnumapi.geometry.Geometry import Geometry
from magnumapi.geometry.GeometryFactory import GeometryFactory


class OptimizationCockpitWidget:

    def __init__(self, gen_opt, logger_df, config, optim_input_df, block_inputs, cadata):
        self.gen_opt = gen_opt
        self.min_logger_df = gen_opt.get_min_fitness_per_generation(logger_df)
        self.config = config
        self.optim_input_df = optim_input_df
        self.block_inputs = block_inputs
        self.cadata = cadata

        fig = make_subplots(
            rows=3, cols=2,
            shared_xaxes=False,
            vertical_spacing=0.03,
            column_widths=[0.35, 0.65],
            row_heights=[0.15, 0.2, 0.65],
            specs=[[{"type": "xy"}, {"type": "table"}], [{"type": "xy", "rowspan": 2}, {"type": "scatter"}],
                   [None, {"type": "scatter"}]]
        )

        self.widget = go.FigureWidget(fig)

    def show(self):
        return self.widget

    def build(self):
        self.update_title(len(self.min_logger_df), self.min_logger_df.loc[self.min_logger_df.index[-1], 'fitness'])

        # Display fitness function graph with callback
        self.display_fitness_function_graph(row=2, col=2)

        index_best = self.min_logger_df.index[-1]

        # Display selected generation objective table
        obj_best_df = self.create_objective_table(index_best)
        self.display_objective_table(obj_best_df)

        # Display fitness function comparison graph
        self.display_fitness_function_comparison_graph(obj_best_df, obj_best_df, row=1, col=1)

        # Display design variables graph
        self.display_design_variables_graph(index_best, index_best, row=2, col=1)

        # Display geometry graph
        self.display_geometry_graph(index_best, row=3, col=2)

        # Create callback function
        def callback(self):
            def update_point(trace, points, selector):
                index = points.point_inds[0]

                # Update selected generation objective table
                widget_data = self.widget.data[1]
                obj_df = self.create_objective_table(index)
                OptimizationCockpitWidget.update_objective_table(widget_data, obj_df)

                # Clear remaining graphs befor display
                self.widget.data = [self.widget.data[0], self.widget.data[1]]

                # Display fitness function comparison graph
                self.display_fitness_function_comparison_graph(obj_df, obj_best_df, row=1, col=1)

                # Display design variables graph
                self.display_design_variables_graph(index, index_best, row=2, col=1)

                # Display geometry graph
                self.display_geometry_graph(index, row=3, col=2)

                self.update_title(index, self.min_logger_df.loc[index, 'fitness'])

            return update_point

        scatter = self.widget.data[0]
        self.widget.layout.hovermode = 'closest'
        scatter.on_click(callback(self))

    def update_title(self, index_gen, fitness_function):
        self.widget.update_layout(
            height=1000,
            showlegend=False,
            title_x=0.5,
            title_text="Optimization Cockpit - index: %d - fitness function: %f" % (index_gen, fitness_function),
        )

    def display_fitness_function_graph(self, row=2, col=2):
        self.widget.add_trace(
            go.Scatter(
                x=self.min_logger_df.index.values,
                y=self.min_logger_df['fitness'].values,
                mode="lines+markers",
                name="fitness"
            ),
            row=row, col=col
        )

    def display_objective_table(self, obj_df):
        obj_trans_df = OptimizationCockpitWidget.transpose_objective_table(obj_df)

        self.widget.add_trace(
            go.Table(
                header=dict(
                    values=obj_trans_df.columns,
                    font=dict(size=10),
                    align="left"
                ),
                cells=dict(
                    values=[obj_trans_df[k].tolist() for k in obj_trans_df.columns],
                    align="left")
            ),
            row=1, col=2)

    @staticmethod
    def get_weight(config_objectives, objective):
        for config_objective in config_objectives:
            if config_objective.objective == objective:
                return config_objective.weight

    @staticmethod
    def get_constraint(config_objectives, objective):
        for config_objective in config_objectives:
            if config_objective.objective == objective:
                return config_objective.constraint

    def create_objective_table(self, index):
        objectives = [obj.objective for obj in self.config.objectives]
        obj_df = pd.DataFrame(self.min_logger_df.loc[index, objectives])
        obj_df = obj_df.rename(columns={obj_df.columns[0]: 'objective'})

        obj_df['weights'] = obj_df.apply(lambda col:
                                         OptimizationCockpitWidget.get_weight(self.config.objectives, col.name),
                                         axis=1)
        obj_df['constraints'] = obj_df.apply(lambda col:
                                             OptimizationCockpitWidget.get_constraint(self.config.objectives, col.name),
                                             axis=1)
        obj_df['objective_weighted'] = obj_df['weights'] * (obj_df['objective'] - obj_df['constraints'])

        return obj_df

    @staticmethod
    def transpose_objective_table(obj_df):
        obj_trans_df = obj_df.T
        obj_trans_df = obj_trans_df.reset_index()
        obj_trans_df = obj_trans_df.rename(columns={"index": ""})
        return obj_trans_df

    @staticmethod
    def update_objective_table(widget_data, obj_df):
        obj_trans_df = OptimizationCockpitWidget.transpose_objective_table(obj_df)

        widget_data.cells = dict(
            values=[obj_trans_df[k].tolist() for k in obj_trans_df.columns],
            align="left")

    def display_fitness_function_comparison_graph(self, obj_df, obj_best_df, row=1, col=1):

        objective_variables = obj_df.index.values
        fitness_actual = obj_df['objective_weighted'].values
        fitness_best = obj_best_df['objective_weighted'].values

        cum_fitness_actual = list(accumulate(fitness_actual))
        cum_fitness_best = list(accumulate(fitness_best))

        hover_text_actual = ['%s: %f' % obj_fitness for obj_fitness in zip(objective_variables, fitness_actual)]
        hover_text_best = ['%s: %f' % obj_fitness for obj_fitness in zip(objective_variables, fitness_best)]

        n = len(objective_variables)
        for i in range(n):
            trace = go.Bar(
                x=[cum_fitness_best[n - i - 1], cum_fitness_actual[n - i - 1]],
                y=['Best', 'Actual'],
                hovertext=[hover_text_best[n - i - 1], hover_text_actual[n - i - 1]],
                orientation='h',
                hoverinfo='text',
                offsetgroup=1
            )
            self.widget.append_trace(trace, row, col)

    def display_design_variables_graph(self, index_act, index_best, row=2, col=1):
        dv_columns = [col for col in self.min_logger_df.columns if ':' in col]
        act_gen = self.prepare_row_for_bar_plot(self.min_logger_df.loc[index_act, dv_columns])
        best_gen = self.prepare_row_for_bar_plot(self.min_logger_df.loc[index_best, dv_columns])

        trace_best = go.Bar(
            x=best_gen['frac'].values,
            hovertext=OptimizationCockpitWidget.get_hover_texts(best_gen),
            y=best_gen['variable'].values,
            name='Best',
            orientation='h')

        trace_act = go.Bar(
            x=act_gen['frac'].values,
            hovertext=OptimizationCockpitWidget.get_hover_texts(act_gen),
            y=act_gen['variable'].values,
            name='Actual',
            orientation='h')

        self.widget.add_traces([trace_best, trace_act], rows=row, cols=col)

    def prepare_row_for_bar_plot(self, df):
        min_logger_trans_df = pd.DataFrame(df)
        min_logger_trans_df = min_logger_trans_df.rename(columns={min_logger_trans_df.columns[0]: 'value'})

        def get_dv_parameter(optim_input_df, variable, parameter):
            block, variable = variable.split(':')
            block = int(block)
            return optim_input_df[(optim_input_df['variable'] == variable) &
                                  (optim_input_df['bcs'] == block)][parameter].values[0]

        min_logger_trans_df['variable_type'] = min_logger_trans_df.apply(
            lambda col: get_dv_parameter(self.optim_input_df, col.name, 'variable_type'), axis=1)
        min_logger_trans_df['xl'] = min_logger_trans_df.apply(
            lambda col: get_dv_parameter(self.optim_input_df, col.name, 'xl'), axis=1)
        min_logger_trans_df['xu'] = min_logger_trans_df.apply(
            lambda col: get_dv_parameter(self.optim_input_df, col.name, 'xu'), axis=1)
        min_logger_trans_df['frac'] = (min_logger_trans_df['value'] - min_logger_trans_df['xl']) / (
                min_logger_trans_df['xu'] - min_logger_trans_df['xl'])
        min_logger_trans_df['variable'] = min_logger_trans_df.index
        return min_logger_trans_df

    @staticmethod
    def get_hover_texts(df):
        hovertexts = []
        for _, row in df.iterrows():
            if row['variable_type'] == 'float':
                hovertext = 'value: %.3f, range: [%.3f, %.3f]' % tuple(row[['value', 'xl', 'xu']].values)
            else:
                hovertext = 'value: %d, range: [%d, %d]' % tuple(row[['value', 'xl', 'xu']].values)

            hovertexts.append(hovertext)

        return hovertexts

    def display_geometry_graph(self, index, row=3, col=2):
        fit_row = self.min_logger_df[self.min_logger_df.index == index]
        fit_dct = fit_row.to_dict('records')[0]
        fit_input = self.gen_opt.update_parameters(self.block_inputs, fit_dct)

        geometry = GeometryFactory.init_with_dict(fit_input, self.cadata)
        geometry.build_blocks()

        go_scatter = Geometry.create_plotly_scatters(geometry.blocks)

        max_number_of_blocks = int(self.optim_input_df[self.optim_input_df['variable'] == 'nco']['xu'].sum())
        for i in range(max_number_of_blocks - len(go_scatter)):
            go_scatter.append(go.Scatter(x=[], y=[]))

        self.widget.add_traces(go_scatter, rows=row, cols=col)
