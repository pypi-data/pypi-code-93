'''
Created on 21 nov. 2020

  pypos3d.propslim implements a decimate algorithm
  Requires : pypos3d.wftk, numpy

  Decimation function.
  This package 'propslim' contains the port of the QSlim algorithm initially 
  developed and distributed by Michael Garland in July 2004 within the "SlimKit
  Surface Modeling Tools".
  This decimate function applies to "WaveGeom" and preserves 'texture' coordinates.

  **WARNING**
  Original copyrights and credentials are delivered within this independant module.
  The original C++ code was GPL2. I don't know about my partial port, I suspect it to be _copylefted_ by it.
  If it's not the case, I would choose for 'New BSD license'
  For commercial usage in a closed source program, I suggest to remove the package: pypos3d.propslim
'''
import logging
import numpy as np

from langutil import C_OK, C_FAIL
from pypos3d.wftk.WFBasic import Point3d

from pypos3d.propslim import MX_VALID_FLAG, MX_PERVERTEX
from pypos3d.propslim.MxBasic import MxQuadric, MxHeap, MxHeapable, MxQuadric3, MxPairContraction
from pypos3d.propslim.MxStdModel import MxStdModel

#------------------------------------------------------------------------------
# PORTING RULES and MAPPING:
#
# MxVector (GVector) --> np.array()
# MxMatrix (GMatrix) --> np.array()
# MxBlock  (ported): fixed size list of object or pointers
# MXQuadric (GMatrix, GVector, doules) : PORTED
# MxdDynBlock : PORTED --> Finally Replaced by Python lists
# MxSizedDynBlock : Not ported
# edge_list : Not ported
# BoolIntRes replaced in Python by a [Bool, Int] list
# MxVertex : Point3d
#
# MxFaceList : Not Ported extends MxSizedDynBlock<MxInteger> implements Blockable
#   list(int)
# MxVertexList : Not Ported extends MxSizedDynBlock<MxInteger> implements Blockable
#   list(int)
#
#------------------------------------------------------------------------------

class edge_info(MxHeapable): # extends MxHeapable implements Blockable

  Dpb = 0 # static int Dpb
    
  def __init__(self, D = 0): # public edge_info()
    super(edge_info, self).__init__()
    self.target = np.zeros((D,))
    self.v1 = 0
    self.v2 = 0
    edge_info.Dpb = D

  def __str__(self):
    return 'EI[{:d},{:d}, {:g}, {:d}]'.format(self.v1, self.v2, self.heapKey, self.heapPos)
 
 
 
class MxPropSlim():
  '''
  Python port of DATA3D MxPropSlim, limited to 'texture' optional management
  '''
  PLACE_ENDPOINTS = 0
  MX_PLACE_ENDORMID = 1
  MX_PLACE_LINE = 2
  MX_PLACE_OPTIMAL = 3
  MX_WEIGHT_UNIFORM = 0
  MX_WEIGHT_AREA = 1
  MX_WEIGHT_ANGLE = 2
  MX_WEIGHT_AVERAGE = 3
  MX_WEIGHT_AREA_AVG = 4
  MX_WEIGHT_RAWNORMALS = 5

  def __init__(self, m0:'MxStdModel'):
    logging.info('Create with %d vertex and %d faces and %s binding', len(m0.vertices), len(m0.faces), m0.binding_name(m0.tbinding))
    self.heap = MxHeap(64)
    self.m = m0

    # Externally visible variables
    self.boundary_weight = 1000.0
    self.valid_faces = 0
    self.valid_verts = 0
    self.is_initialized = False

    for fa in m0.faces: 
      if fa.tag & MX_VALID_FLAG!=0:
        self.valid_faces+=1

    for vtx in m0.vertices:
      if vtx.tag & MX_VALID_FLAG!=0: 
        self.valid_verts+=1

    self.consider_texture(True)

    self.D = self.compute_dimension(self.m)
    self.star = []
    # ODY = MxBlock<MxQuadric *> !!! 
    self.__quadrics = [ MxQuadric(self.D) for _ in range(len(m0.vertices)) ]
    self.edge_links = [ [ ] for _ in range(len(m0.vertices)) ]

    # Never Set elsewhere self.will_decouple_quadrics = False

  def dim(self): return self.D
  def prop_count(self): return 2 if self.use_texture else 1
  #def quadric_count(self): return self.__quadrics.length()

  def initialize(self):
    self.collect_quadrics()
    if self.boundary_weight > 0.0:
      self.constrain_boundaries()
    self.collect_edges()
    self.is_initialized = True

  def collect_quadrics(self):
    v1 = np.zeros( (self.D, ) )
    v2 = np.zeros( (self.D, ) )
    v3 = np.zeros( (self.D, ) )

    #for (/*MxFaceID */int i = 0; i < m.face_count()):
    for f in self.m.faces:
      self.pack_to_vector(f.v0, v1)
      self.pack_to_vector(f.v1, v2)
      self.pack_to_vector(f.v2, v3)

      Q = MxQuadric(p1=v1, p2=v2, p3=v3, area=self.m.compute_face_area(f))
      if not Q.valid:
        print("Null surface face:", str(f))
      
      self.__quadrics[f.v0].add(Q)
      self.__quadrics[f.v1].add(Q)
      self.__quadrics[f.v2].add(Q)

  def pack_to_vector(self, vid, v):
    vtx = self.m.vertices[vid]
    if self.use_texture:
      v[:] = [ vtx.x, vtx.y, vtx.z, self.m.tcoords[vid].x, self.m.tcoords[vid].y ]
    else:
      v[:] = [ vtx.x, vtx.y, vtx.z ]


  def compute_target_placement(self, info:'edge_info'):
    #/* MxVertexID */int 
    i,j =  info.v1, info.v2

    Qj = self.__quadrics[j]
    Q = MxQuadric(src=self.__quadrics[i])
    Q.add(Qj)

    err = 0.0

    if Q.optimize(info.target):
      err = Q.evaluate(info.target)
    else:
      # Fall back only on endpoints
      v_i = np.zeros((self.D, )) # new MxVector(dim())
      v_j = np.zeros((self.D, )) # new MxVector(dim())

      self.pack_to_vector(i, v_i)
      self.pack_to_vector(j, v_j)

      e_i = Q.evaluate(v_i)
      e_j = Q.evaluate(v_j)

      if e_i <= e_j:
        info.target = v_i
        err = e_i
      else:
        info.target = v_j
        err = e_j

    info.heap_key(float(-err))

  def finalize_edge_update(self, info:'edge_info'):
    if info.is_in_heap():
      self.heap.update(info)
    else:
      self.heap.insert(info)

  def compute_edge_info(self, info:'edge_info'):
    self.compute_target_placement(info)
    self.finalize_edge_update(info)

  def create_edge(self, i, j):
    info = edge_info(self.D)

    self.edge_links[i].append(info)
    self.edge_links[j].append(info)

    info.v1 = i
    info.v2 = j

    self.compute_edge_info(info)

  def collect_edges(self):
    #MxVertexList star = new MxVertexList()
    star = []

    for i in range(0,len(self.m.vertices)): # range(0,  self.m.vert_count()):
      del star[:] # .reset()
      self.m.collect_vertex_star(i, star)

      for ej in star:
        if i < ej: # Only add particular edge once
          self.create_edge(i, ej)

  def constrain_boundaries(self):
    star = []
    faces = []

    for i in range(0, len(self.m.vertices)):
      del star[:] # .reset()
      self.m.collect_vertex_star(i, star)

      for ej in star:
        if i < ej:
          del faces[:] # .reset()
          self.m.collect_edge_neighbors(i, ej, faces)
          if len(faces)==1:
            self.discontinuity_constraint(i, ej, faces)

  # void discontinuity_constraint(/*MxVertexID */int i, /*MxVertexID */int j, MxFaceList faces)
  def discontinuity_constraint(self, i, j, faces):
    for f in range(0, len(faces)):
      org = self.m.vertices[i]
      e = Point3d(self.m.vertices[j]).sub(org) # e  = dest - org

      fa = self.m.faces[faces[f]]
    
      n = Point3d.triangle_normal(self.m.vertices[fa.v0],self.m.vertices[fa.v1],self.m.vertices[fa.v2])

      n2 = e.cross(n) # n2 = e ^ n
      n2.normalize()  # unitize(n2)

      Q3 = MxQuadric3(n2, - n2.dot(org), 1.0)
      Q3.mul(self.boundary_weight)

      Q = MxQuadric(n=self.D, Q3=Q3)

      self.__quadrics[i].add(Q)
      self.__quadrics[j].add(Q)

  def update_pre_contract(self, conx):
    v1 = conx.v1
    v2 = conx.v2

    star = []
    self.m.collect_vertex_star(v1, star)

    for e in self.edge_links[v2]:
      u = e.v2 if e.v1==v2 else e.v1
      if (u==v1) or u in star: 
        # This is a useless link --- kill it
        self.edge_links[u].remove(e)
        self.heap.remove(e)
        # ODY if( u!=v1 ) delete e; // (v1,v2) will be deleted later
      else:
        # Relink this to v1
        e.v1 = v1
        e.v2 = u
        self.edge_links[v1].append(e)

    del self.edge_links[v2][:]

  def unpack_from_vector(self, vid, v):
    self.m.vertices[vid].set(v[0], v[1], v[2])

    if self.use_texture:
      self.m.tcoords[vid].set(v[3], v[4])

  def apply_contraction(self, conx, info):
    self.valid_verts -= 1
    self.valid_faces -= len(conx.dead_faces)
    self.__quadrics[conx.v1].add(self.__quadrics[conx.v2])

    self.update_pre_contract(conx)

    self.m.apply_contraction(conx)

    self.unpack_from_vector(conx.v1, info.target)

    # Must update edge_info here so that the meshing penalties
    # will be computed with respect to the new mesh rather than the old
    for ei in self.edge_links[conx.v1]:
      self.compute_edge_info(ei)

  def decimate(self, target):
    ret = C_OK
    
    conx = MxPairContraction()

    while self.valid_faces>target:
      info = self.heap.extract()
      if not info:
        return C_FAIL

      v1 = info.v1
      v2 = info.v2

      #if self.m.vertex_is_valid(v1) and self.m.vertex_is_valid(v2):
      if self.m.vertices[v1].tag & MX_VALID_FLAG and self.m.vertices[v2].tag & MX_VALID_FLAG \
        and not v1 in self.m.protvert and not v2 in self.m.protvert:
        self.m.compute_contraction(v1, v2, conx, None)

        conx.dv1.x = info.target[0] - self.m.vertices[v1].x
        conx.dv1.y = info.target[1] - self.m.vertices[v1].y
        conx.dv1.z = info.target[2] - self.m.vertices[v1].z
        conx.dv2.x = info.target[0] - self.m.vertices[v2].x
        conx.dv2.y = info.target[1] - self.m.vertices[v2].y
        conx.dv2.z = info.target[2] - self.m.vertices[v2].z

        self.apply_contraction(conx, info)

    return ret

  def consider_texture(self, will=True):
    self.use_texture = will and (self.m.texcoord_binding()==MX_PERVERTEX)
    self.D = self.compute_dimension(self.m)

  def compute_dimension(self, m):
    return 5 if self.use_texture else 3

 
def decimate(face_target, srcGeom:'WaveGeom', protEdges=False, protMat=None, lstProtFaces=None, restoreQuad=False, restoreGrp=False):
  ''' Decimate a Wavefront geometry and create a new one.
    This algorithm respects the texture coordinates.

    Parameters
    ----------
    face_target: int
      Expected Number of faces in the target geometry (more or less 2)
      The target geometry is the triangularized version of the geometry
      
    srcGeom: WaveGeom
      Geometry to decimate. Not modified
      
    protEdges: Boolean, optional, default False
      Indicate to the algorithm to freeze edges vertex.
      (It provides the means to protect interfaces between figures parts)
      
    protMat: str, optional, default None
      Indicate to the algorithm ot protect the faces with the given
      material name.
      
    lstProtFaces: iterable, optional, default None
      Indicate to the algorithm ot protect a given set of faces.
      Faces' numbers are relative to the input geometry (of course)
      
    restoreQuad: Boolean, optional, default False
      Try to merge triangles to rebuild 'quadrangle' faces
      
    restoreGrp: Boolean, optional, default False
      Preserve (and recreate) the groups in the result geometry.
      
    Returns
    -------
      WaveGeom
        A new WaveGeom
  '''
  logging.info('Start target=%d, WaveGeom[%d faces, %d vertex]', face_target, srcGeom.getNbFace(), len(srcGeom.coordList))

  m = MxStdModel()

  # Convert Wavefront file into mxkit internal format.
  m.read(srcGeom, protEdges=protEdges, protMat=protMat, lstProtFaces=lstProtFaces)

  slim = MxPropSlim(m)
  
  slim.initialize()
  ret = slim.decimate(face_target)
  #Do not compact, "optimizeGroups" will do the job faster
  m.compact_vertices()

  # Create the result geometry fro the 'MxStdModel'
  geom = m.createWaveGeom(restoreQuad=restoreQuad, restoreGrp=restoreGrp)
  logging.info('Stop Result %s WaveGeom[%d faces, %d vertex]', 'OK' if ret==C_OK else 'Failed', geom.getNbFace(), len(geom.coordList))
  return geom
   
