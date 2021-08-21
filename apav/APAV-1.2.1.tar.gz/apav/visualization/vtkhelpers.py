"""
This file is part of APAV.

APAV is a python package for performing analysis and visualization on
atom probe tomography data sets.

Copyright (C) 2018 Jesse Smith

APAV is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

APAV is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with APAV.  If not, see <http://www.gnu.org/licenses/>.
"""

from collections import namedtuple
from itertools import product
import sys

from apav.vtkall import *
import numpy as n
from numpy import linalg

from apav.utils import helpers


def ApavMapper():
    # return vtkPolyDataMapper()
    return vtkOpenGLPolyDataMapper()


def ApavActor():
    # return vtkActor()
    return vtkOpenGLActor()


def ApavGlyphMapper():
    # return vtkGlyph3D()
    # return vtkGlyph3DMapper()
    return vtkOpenGLGlyph3DMapper()


def cylinder(pt1 ,pt2, radius, resolution=30):
    line = vtkLineSource()
    line.SetPoint1(pt1)
    line.SetPoint2(pt2)

    cyl = vtkTubeFilter()
    cyl.SetRadius(radius)
    cyl.SetNumberOfSides(resolution)
    cyl.SetInputConnection(line.GetOutputPort())

    mapper = ApavMapper()
    mapper.SetInputConnection(cyl.GetOutputPort())
    actor = ApavActor()
    actor.SetMapper(mapper)
    return actor


def point_cloud(array):
    poly = vtkPolyData()
    points = vtkPoints()
    cells = vtkCellArray()
    poly.SetPoints(points)
    poly.SetVerts(cells)
    if len(array.shape) == 1:
        array = array[n.newaxis]

    for coord in array:
        ID = points.InsertNextPoint(*coord[:])
        cells.InsertNextCell(1)
        cells.InsertCellPoint(ID)

    return poly


def point_dataset(points, px, color=(0.5, 0.5, 0.5)):
    mapper = ApavMapper()
    mapper.SetInputData(points)
    actor = ApavActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[:3])
    actor.GetProperty().SetPointSize(px)
    return actor


def sphere_dataset(points,
                   rad,
                   color=(0.5, 0.5, 0.5, 1.0),
                   res_theta=30,
                   res_phi=30,
                   ambient=0.5,
                   specular=0.5):
    sphere = vtkSphereSource()
    sphere.SetRadius(rad)
    sphere.SetThetaResolution(res_theta)
    sphere.SetPhiResolution(res_phi)

    glyph = vtkGlyph3D()
    glyph.SetInputData(points)
    glyph.SetSourceConnection(sphere.GetOutputPort())

    mapper = ApavMapper()
    mapper.SetInputConnection(glyph.GetOutputPort())

    actor = ApavActor()
    actor.SetMapper(mapper)

    if color == "random":
        color = [n.random.random() for i in range(3)]

    actor.GetProperty().SetColor(color[:3])
    if len(color) == 4:
        actor.GetProperty().SetOpacity(color[-1])
    actor.GetProperty().SetSpecular(specular)
    actor.GetProperty().SetAmbient(ambient)

    return actor


def parallelepiped(lengths, angles, celldim=(1,1,1), color=(0.7, 0.7, 0.7), linewidth=1):
    """ Generate cell outline from coordinates """
    nx, ny, nz = celldim

    if isinstance(color, (str)):
        color = helpers.hex2rgbF(color)

    # All parallelepiped coordinates
    xyz_prod = product(range(1, nx+1), range(1, ny+1), range(1, nz+1))

    # For combining all parallelepipeds into single vtk object
    append = vtkAppendPolyData()

    # Create unit outlines
    for x, y, z in xyz_prod:
        # Source
        outl = vtkOutlineSource()
        outl.SetBounds(x-1, x, y-1, y, z-1, z)

    # Mapper/actor boiler plate
    mapper = ApavMapper()
    mapper.SetInputConnection(append.GetOutputPort())
    actor = ApavActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetLineWidth(linewidth)
    return actor
