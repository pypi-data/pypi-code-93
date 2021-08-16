from abc import ABC

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from magnumapi.geometry.Line import Line


class Geometry(ABC):
    def __init__(self, blocks):
        self.blocks = blocks

    def build_blocks(self):
        for block in self.blocks:
            block.build_block()

    def to_roxie_df(self):
        return pd.concat([block.to_roxie_df() for block in self.blocks], axis=0).reset_index(drop=True)

    def to_df(self):
        return pd.concat([block.to_df() for block in self.blocks], axis=0).reset_index(drop=True)

    def plot_blocks(self, figsize=(10, 10), is_grid=True, xlim=(0, 80), ylim=(0, 80)):
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.grid(is_grid)

        for block in self.blocks:
            block.plot_block(ax)

        plt.show()

    def plotly_blocks(self, figsize=(65, 65), xlim=(0, 80), ylim=(0, 80)):
        go_scatter = Geometry.create_plotly_scatters(self.blocks)

        fig = go.Figure(go_scatter)
        fig.update_layout(
            autosize=False,
            width=750,
            height=750,
            yaxis_range=ylim,
            xaxis_range=xlim,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig.add_trace(px.scatter(x=[0], y=[0]).data[0])
        fig.update_xaxes(title=dict(text='x, [mm]'))
        fig.update_yaxes(title=dict(text='y, [mm]'))
        fig.show()

    @staticmethod
    def create_plotly_scatters(blocks):
        go_scatter = []
        index = 1
        for block in blocks:
            for area in block.areas:
                x = []
                y = []
                for i in range(4):
                    x.append(area.get_line(i).p1.x)
                    y.append(area.get_line(i).p1.y)

                x.append(area.get_line(0).p1.x)
                y.append(area.get_line(0).p1.y)

                go_scatter.append(go.Scatter(x=x, y=y, fill="toself", fillcolor='white', marker=dict(size=1),
                                             name='turn' + str(index), line=go.scatter.Line(color='blue')))
                index += 1
        return go_scatter

    def plot_bare_blocks(self, figsize=(15, 15), grid=True, xlim=(0, 80), ylim=(0, 80)):
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_aspect('equal', 'box')
        ax.grid(grid)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        for block in self.blocks:
            block.plot_bare_block(ax)

        plt.show()

    def get_bare_blocks(self):
        # ToDo - the block object should contain ins_areas and bare_areas
        bare_blocks = []
        for block in self.blocks:
            bare_blocks.append(block.get_bare_areas())
        return bare_blocks

    def print_blocks(self):
        for block in self.blocks:
            block.print_block()

    def is_outside_of_first_quadrant(self):
        for block in self.blocks:
            if block.is_outside_of_first_quadrant():
                return True

        return False

    def are_turns_overlapping(self):
        radius_prev = None
        for index, block in enumerate(self.blocks):
            if radius_prev == block.block_def.radius:
                area_curr = block.areas[0]
                area_prev = self.blocks[index - 1].areas[-1]
                line_prev = area_prev.get_line(2)
                line_prev_rev = Line.of_end_points(line_prev.p2, line_prev.p1)
                orient_p1 = Line.calculate_point_orientation_wrt_line(line_prev_rev, area_curr.get_line(0).p1)
                orient_p2 = Line.calculate_point_orientation_wrt_line(line_prev_rev, area_curr.get_line(0).p2)

                if orient_p1 == -1 or orient_p2 == -1:
                    return True

            radius_prev = block.block_def.radius

        return False

    def is_wedge_tip_too_sharp(self, min_value_in_mm):
        radius_prev = None
        for index, block in enumerate(self.blocks):
            if radius_prev == block.block_def.radius:
                area_curr = block.areas[0]
                area_prev = self.blocks[index - 1].areas[-1]

                line_first_area = area_curr.get_line(0)
                line_last_area = area_prev.get_line(2)

                l_arc = Line.calc_arc_length_between_two_lines(block.block_def.radius, line_last_area, line_first_area)
                if l_arc < min_value_in_mm:
                    return True

            radius_prev = block.block_def.radius

        return False

    @staticmethod
    def display_definition_table(df):
        from ipyaggrid import Grid

        column_defs = [{'headername': c, 'field': c} for c in df.columns]

        grid_options = {
            'columnDefs': column_defs,
            'enableSorting': True,
            'enableFilter': True,
            'enableColResize': True,
            'enableRangeSelection': True,
            'rowSelection': 'multiple',
        }

        return Grid(grid_data=df,
                    grid_options=grid_options,
                    quick_filter=True,
                    show_toggle_edit=True,
                    sync_on_edit=True,
                    export_csv=True,
                    export_excel=True,
                    theme='ag-theme-balham',
                    show_toggle_delete=True,
                    columns_fit='auto',
                    index=False)
