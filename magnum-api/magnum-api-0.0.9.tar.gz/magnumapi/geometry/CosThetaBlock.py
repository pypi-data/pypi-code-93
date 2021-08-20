import math
from abc import abstractmethod

import pandas as pd
import matplotlib.pyplot as plt

from magnumapi.geometry.Arc import Arc
from magnumapi.geometry.Area import Area
from magnumapi.geometry.Block import Block
from magnumapi.geometry.Line import Line
from magnumapi.geometry.Point import Point
from magnumapi.geometry.ansys.HomogenizedBlockDefinition import HomogenizedBlockDefinition
from magnumapi.geometry.roxie.AbsoluteCosThetaBlockDefinition import AbsoluteCosThetaBlockDefinition
from magnumapi.geometry.roxie.ConductorDefinition import ConductorDefinition
from magnumapi.geometry.roxie.CosThetaBlockDefinition import CosThetaBlockDefinition
from magnumapi.geometry.roxie.RelativeCosThetaBlockDefinition import RelativeCosThetaBlockDefinition
from magnumapi.geometry.roxie.CableDefinition import CableDefinition
from magnumapi.geometry.roxie.InsulationDefinition import InsulationDefinition
from magnumapi.geometry.roxie.StrandDefinition import StrandDefinition


class CosThetaBlock(Block):

    def __init__(self,
                 block_def: CosThetaBlockDefinition,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition):
        super().__init__(cable_def=cable_def,
                         insul_def=insul_def,
                         strand_def=strand_def,
                         conductor_def=conductor_def)
        self.block_def = block_def

    @abstractmethod
    def get_alpha(self):
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def get_phi(self):
        raise NotImplementedError('This method is not implemented for this class')

    def build_block(self, phi_ref=0.0, alpha_ref=0.0):
        phi = phi_ref + self.get_phi()
        alpha = alpha_ref + self.get_alpha()
        p_ref = Point.of_polar(self.block_def.radius, phi)

        for nco_i in range(self.block_def.nco):
            area = self.get_insulated_isosceles_trapezium(p_ref=p_ref, alpha_ref=alpha)
            area_shift = area.copy()
            if self.is_area_intersecting_or_within_radius(area_shift):
                alpha_top_line = Line.calculate_relative_alpha_angle(area_shift.get_line(0))
                area_shift = area.translate(Point.of_polar(2 * self.cable_def.thickness_i, alpha_top_line))

            shift = Area.find_trapezoid_shift_to_intercept_with_radius(self.block_def.radius, area_shift)
            alpha_low = Line.calculate_relative_alpha_angle(area_shift.get_line(0))
            area = area_shift.copy().translate(Point.of_polar(-shift, alpha_low))

            self.areas.append(area)

            p_ref = area.get_line(2).p2.copy()
            alpha = Line.calculate_relative_alpha_angle(self.areas[-1].get_line(2))

    def get_bare_areas(self):
        bare_areas = []
        for area in self.areas:
            bare_area = self.get_bare_area(area)
            bare_areas.append(bare_area)

        return bare_areas

    def get_bare_area(self, area):
        line_ref = area.get_line(0).copy()
        p_ref = line_ref.p1.copy()
        alpha_ref = Line.calculate_relative_alpha_angle(line_ref)
        return self.get_bare_isosceles_trapezium(p_ref=p_ref, alpha_ref=alpha_ref)

    def get_insulated_isosceles_trapezium(self, p_ref=Point.of_cartesian(0.0, 0.0), alpha_ref=0.0):
        """
        A turn is represented as an isosceles trapezoid of a given height, inner and outer width. When inner and outer
        widths are equal, then the turn is a rectangle. The difference between the inner and outer widths gives the
        keystone angle of a cable. The inner width is in contact with the mandrel radius.

        :return:
        """
        keystone_half_rad = math.atan(
            (self.cable_def.thickness_o - self.cable_def.thickness_i) / (2 * self.cable_def.width))
        keystone_half_deg = math.degrees(keystone_half_rad)

        area_bare = self.get_bare_isosceles_trapezium(p_ref=p_ref, alpha_ref=alpha_ref)

        # calculate insulation coordinates
        ins_r_projected = self.insul_def.thickness / math.cos(keystone_half_rad)
        ins_a_projected = self.insul_def.width / math.cos(keystone_half_rad)

        p1_ins_r = Point.of_polar(ins_r_projected, 180 + alpha_ref)
        p1_ins_a = Point.of_polar(ins_a_projected, -90 + keystone_half_deg + alpha_ref)
        p1_ins = area_bare.get_line(0).p1 + (p1_ins_r + p1_ins_a)

        p2_ins_r = Point.of_polar(ins_r_projected, alpha_ref)
        p2_ins_a = Point.of_polar(ins_a_projected, -90 + keystone_half_deg + alpha_ref)
        p2_ins = area_bare.get_line(1).p1 + (p2_ins_r + p2_ins_a)

        p3_ins_r = Point.of_polar(ins_r_projected, 2 * keystone_half_deg + alpha_ref)
        p3_ins_a = Point.of_polar(ins_a_projected, 90 + keystone_half_deg + alpha_ref)
        p3_ins = area_bare.get_line(2).p1 + (p3_ins_r + p3_ins_a)

        p4_ins_r = Point.of_polar(ins_r_projected, 180 + 2 * keystone_half_deg + alpha_ref)
        p4_ins_a = Point.of_polar(ins_a_projected, 90 + keystone_half_deg + alpha_ref)
        p4_ins = area_bare.get_line(3).p1 + (p4_ins_r + p4_ins_a)

        l1_ins = Line.of_end_points(p1_ins, p2_ins)
        l2_ins = Line.of_end_points(p2_ins, p3_ins)
        l3_ins = Line.of_end_points(p3_ins, p4_ins)
        l4_ins = Line.of_end_points(p4_ins, p1_ins)

        area_ins = Area.of_lines((l1_ins, l2_ins, l3_ins, l4_ins))

        return area_ins

    def get_bare_isosceles_trapezium(self, p_ref=Point.of_cartesian(0.0, 0.0), alpha_ref=0.0):
        keystone_half_rad = math.atan(
            (self.cable_def.thickness_o - self.cable_def.thickness_i) / (2 * self.cable_def.width))
        keystone_half_deg = math.degrees(keystone_half_rad)
        side = self.cable_def.width / math.cos(keystone_half_rad)

        p1 = p_ref
        p2 = p1 + Point.of_polar(side, alpha_ref)
        p3 = p2.copy() + Point.of_polar(self.cable_def.thickness_o, alpha_ref + 90 + keystone_half_deg)
        p4 = p1 + Point.of_polar(self.cable_def.thickness_i, alpha_ref + 90 + keystone_half_deg)

        l1 = Line.of_end_points(p1, p2)
        l2 = Line.of_end_points(p2, p3)
        l3 = Line.of_end_points(p3, p4)
        l4 = Line.of_end_points(p4, p1)

        area = Area.of_lines((l1, l2, l3, l4))

        ins_r_projected = self.insul_def.thickness / math.cos(keystone_half_rad)
        ins_a_projected = self.insul_def.width / math.cos(keystone_half_rad)

        p1_ins_r = Point.of_polar(ins_r_projected, 180 + alpha_ref)
        p1_ins_a = Point.of_polar(ins_a_projected, -90 + keystone_half_deg + alpha_ref)

        area_translated = area.translate(-(p1_ins_r + p1_ins_a))

        return area_translated

    def is_area_intersecting_or_within_radius(self, area):
        is_intercepting = Line.find_interception_parameter(self.block_def.radius, area.get_line(3)) is not None
        is_within_radius = Line.is_line_intercepting_radius(radius=self.block_def.radius, line=area.get_line(3))
        return is_intercepting or is_within_radius

    def plot_block(self, ax):
        circle = plt.Circle((0, 0), self.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        for area in self.areas:
            area.plot(ax)

    def plot_bare_block(self, ax):
        circle = plt.Circle((0, 0), self.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        for area in self.areas:
            self.get_bare_area(area).plot(ax)

    def print_block(self):
        for area in self.areas:
            print(area)

    def is_outside_of_first_quadrant(self):
        is_inside_first_quadrant = False
        for area in self.areas:
            is_inside_first_quadrant |= Area.is_outside_of_first_quadrant(area)

        return is_inside_first_quadrant


class AbsoluteCosThetaBlock(CosThetaBlock):

    def __init__(self,
                 block_def: AbsoluteCosThetaBlockDefinition,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition):
        super().__init__(block_def, cable_def, insul_def, strand_def, conductor_def)
        self.alpha = block_def.alpha
        self.phi = block_def.phi

    def get_alpha(self):
        return self.alpha

    def get_phi(self):
        return self.phi

    def to_roxie_df(self):
        dct = self.block_def.__dict__
        dct_no_areas = {key: value for key, value in dct.items()}
        df = pd.DataFrame(dct_no_areas, index=[0])
        return df[['no', 'type', 'nco', 'radius', 'phi', 'alpha', 'current', 'condname', 'n1', 'n2', 'imag', 'turn']]


class RelativeCosThetaBlock(CosThetaBlock):

    def __init__(self,
                 block_def: RelativeCosThetaBlockDefinition,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition):
        super().__init__(block_def, cable_def, insul_def, strand_def, conductor_def)
        self.alpha_r = block_def.alpha_r
        self.phi_r = block_def.phi_r

    def get_alpha(self):
        return self.alpha_r

    def get_phi(self):
        return self.phi_r

    def to_roxie_df(self):
        dct = self.block_def.__dict__
        dct_no_areas = {key: value for key, value in dct.items()}
        df = pd.DataFrame(dct_no_areas, index=[0])
        # ToDo: What if areas is empty?
        line_ref = self.areas[0].get_line(0)
        df['alpha'] = Line.calculate_relative_alpha_angle(line_ref)
        df['phi'] = Line.calculate_positioning_angle(line_ref, self.block_def.radius)
        return df[['no', 'type', 'nco', 'radius', 'phi', 'alpha', 'current', 'condname', 'n1', 'n2', 'imag', 'turn']]


class HomogenizedCosThetaBlock(Block):

    def __init__(self,
                 block_def: HomogenizedBlockDefinition,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition):
        super().__init__(cable_def, insul_def, strand_def, conductor_def)
        self.homo_block_def = block_def
        self.area = None

    def to_roxie_df(self):
        raise NotImplementedError('This method is not implemented for this class')

    def plot_block(self, ax):
        self.area.plot(ax)

    def build_block(self):
        p0 = Point.of_polar(self.homo_block_def.radius_inner, self.homo_block_def.phi_0)
        p1 = Point.of_polar(self.homo_block_def.radius_outer, self.homo_block_def.phi_1)
        p2 = Point.of_polar(self.homo_block_def.radius_outer, self.homo_block_def.phi_2)
        p3 = Point.of_polar(self.homo_block_def.radius_inner, self.homo_block_def.phi_3)
        self.area = Area.of_lines((Line.of_end_points(p0, p1),
                                   Arc.of_end_points_center(p1, p2),
                                   Line.of_end_points(p2, p3),
                                   Arc.of_end_points_center(p3, p0)))
