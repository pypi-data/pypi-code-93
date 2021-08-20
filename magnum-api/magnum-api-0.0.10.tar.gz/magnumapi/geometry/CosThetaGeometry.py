from typing import List
import datetime

import plotly.graph_objects as go
import plotly.express as px

from magnumapi.geometry.CosThetaBlock import RelativeCosThetaBlock, HomogenizedCosThetaBlock
from magnumapi.geometry.Geometry import Geometry
from magnumapi.geometry.Arc import Arc
from magnumapi.geometry.Line import Line
from magnumapi.geometry.ansys.HomogenizedBlockDefinition import HomogenizedBlockDefinition

print('Analysis executed on %s' % str(datetime.datetime.now()).split('.')[0])
print('Loaded MagNum API version 0.0.1')


class RelativeCosThetaGeometry(Geometry):
    def __init__(self, blocks: List[RelativeCosThetaBlock]):
        super().__init__(blocks)

    def build_blocks(self):
        radius_prev = None
        for index, block in enumerate(self.blocks):
            if radius_prev != block.block_def.radius:
                alpha_ref, phi_ref = 0, 0
            else:
                area_prev = self.blocks[index - 1].areas[-1]
                phi_ref = Line.calculate_positioning_angle(area_prev.get_line(2), block.block_def.radius)
                alpha_ref = Line.calculate_relative_alpha_angle(area_prev.get_line(2))

            block.build_block(phi_ref=phi_ref, alpha_ref=alpha_ref)
            radius_prev = block.block_def.radius


class HomogenizedCosThetaGeometry(Geometry):

    def __init__(self, blocks: List[HomogenizedCosThetaBlock]) -> None:
        super().__init__(blocks)

    def to_roxie_df(self):
        raise NotImplementedError('This method is not implemented for this class')

    @classmethod
    def with_cos_theta_geometry(cls, geometry):
        inner_radii = cls.get_inner_radii(geometry)
        outer_radii = cls.get_outer_radii(geometry)

        blocks = []
        index_layer = 0
        radius_prev = geometry.blocks[0].block_def.radius
        for index_block, block in enumerate(geometry.blocks):
            if radius_prev != block.block_def.radius:
                index_layer += 1

            inner_radius = inner_radii[index_layer]
            outer_radius = outer_radii[index_layer]

            # write block corner angles
            # 4 ----- 3
            # |       |
            # |       |
            # 1-------2
            phi_0 = block.areas[0].get_line(0).p1.get_phi()
            phi_1 = block.areas[0].get_line(0).p2.get_phi()
            phi_2 = block.areas[-1].get_line(2).p1.get_phi()
            phi_3 = block.areas[-1].get_line(2).p2.get_phi()

            homo_block_def = HomogenizedBlockDefinition(no=index_block + 1,
                                                        type=1,
                                                        nco=block.block_def.nco,
                                                        radius_inner=inner_radius,
                                                        radius_outer=outer_radius,
                                                        phi_0=phi_0,
                                                        phi_1=phi_1,
                                                        phi_2=phi_2,
                                                        phi_3=phi_3,
                                                        current=block.block_def.current,
                                                        condname=block.block_def.condname,
                                                        n1=block.block_def.n1,
                                                        n2=block.block_def.n2,
                                                        imag=block.block_def.imag,
                                                        turn=block.block_def.turn)

            blocks.append(HomogenizedCosThetaBlock(block_def=homo_block_def,
                                                   cable_def=block.cable_def,
                                                   strand_def=block.strand_def,
                                                   conductor_def=block.conductor_def,
                                                   insul_def=block.insul_def))

            radius_prev = block.block_def.radius

        return HomogenizedCosThetaGeometry(blocks=blocks)

    @staticmethod
    def get_inner_radii(geometry) -> List[float]:
        inner_radii = []
        radius_prev = geometry.blocks[0].block_def.radius
        radius_min = float('inf')
        for block in geometry.blocks:
            # for blocks in the same layer
            if radius_prev == block.block_def.radius:
                # find minimum from inner node radii of each turn
                for area in block.areas:
                    turn_radius_min = min(area.get_line(3).p1.get_r(), area.get_line(3).p2.get_r())
                    radius_min = min(radius_min, turn_radius_min)
            else:
                inner_radii.append(radius_min)
                radius_min = float('inf')

            radius_prev = block.block_def.radius
        inner_radii.append(radius_min)

        return inner_radii

    @staticmethod
    def get_outer_radii(geometry) -> List[float]:
        outer_radii = []
        radius_prev = geometry.blocks[0].block_def.radius
        radius_max = -float('inf')
        for block in geometry.blocks:
            # for blocks in the same layer
            if radius_prev == block.block_def.radius:
                # find minimum from inner node radii of each turn
                for area in block.areas:
                    turn_radius_max = max(area.get_line(1).p1.get_r(), area.get_line(1).p2.get_r())
                    radius_max = max(radius_max, turn_radius_max)
            else:
                outer_radii.append(radius_max)
                radius_max = -float('inf')

            radius_prev = block.block_def.radius
        outer_radii.append(radius_max)

        return outer_radii

    def build_blocks(self):
        for block in self.blocks:
            block.build_block()

    def plotly_blocks(self, figsize=(65, 65), xlim=(0, 80), ylim=(0, 80)):

        lines = []
        arcs = []

        index = 1
        for block in self.blocks:
            line_bottom = block.area.get_line(0)
            arc_outer = block.area.get_line(1)
            line_top = block.area.get_line(2)
            arc_inner = block.area.get_line(3)

            arcs.append(dict(type="path",
                             path=Arc.describe_ellipse_arc(a=arc_inner.get_radius(),
                                                           b=arc_inner.get_radius(),
                                                           start_angle=arc_inner.get_start_angle_in_rad(),
                                                           end_angle=arc_inner.get_end_angle_in_rad()),
                             line_color="black"))

            arcs.append(dict(type="path",
                             path=Arc.describe_ellipse_arc(a=arc_outer.get_radius(),
                                                           b=arc_outer.get_radius(),
                                                           start_angle=arc_outer.get_start_angle_in_rad(),
                                                           end_angle=arc_outer.get_end_angle_in_rad()),
                             line_color="black"))

            lines.append(go.Scatter(x=[line_bottom.p1.x, line_bottom.p2.x],
                                    y=[line_bottom.p1.y, line_bottom.p2.y],
                                    fill="toself", fillcolor='white', marker=dict(size=1),
                                    name='block' + str(index), line=go.scatter.Line(color='black')))

            lines.append(go.Scatter(x=[line_top.p1.x, line_top.p2.x],
                                    y=[line_top.p1.y, line_top.p2.y],
                                    fill="toself", fillcolor='white', marker=dict(size=1),
                                    name='block' + str(index), line=go.scatter.Line(color='black')))

            index += 1

        fig = go.Figure(lines)
        fig.update_layout(
            autosize=False,
            width=750,
            height=750,
            xaxis_range=xlim,
            yaxis_range=ylim,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            shapes=arcs
        )
        fig.add_trace(px.scatter(x=[0], y=[0]).data[0])
        fig.update_xaxes(title=dict(text='x, [mm]'))
        fig.update_yaxes(title=dict(text='y, [mm]'))
        fig.show()

    def get_number_of_layers(self: "HomogenizedCosThetaGeometry") -> int:
        n_layers = 0
        radius_prev = None
        for block in self.blocks:
            if radius_prev != block.homo_block_def.radius_inner:
                n_layers += 1

            radius_prev = block.homo_block_def.radius_inner

        return n_layers

    def get_number_of_blocks_per_layer(self: "HomogenizedCosThetaGeometry") -> List[int]:
        blocks_per_layer = [0]
        radius_prev = self.blocks[0].homo_block_def.radius_inner
        for block in self.blocks:
            if radius_prev != block.homo_block_def.radius_inner:
                blocks_per_layer.append(1)
            else:
                blocks_per_layer[-1] += 1

            radius_prev = block.homo_block_def.radius_inner

        return blocks_per_layer
