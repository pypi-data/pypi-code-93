'''
Created on 23 nov. 2020

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

@author: olivier
'''
import logging

from pypos3d.wftk.WFBasic import Point3d, TexCoord2f, C_FACE_TEXT
from pypos3d.wftk.WaveGeom import WaveGeom

from pypos3d.propslim import MX_UNBOUND, MX_ALL_MASK, MX_VALID_FLAG, MX_PERVERTEX, MX_MAX_BINDING


class MxFace: # implements Blockable
  #public/* MxVertexID */int v[] = new int[3]

  def __init__(self, v0, v1, v2, matIdx, grpNo):
    ''' Constructors: -1 supposed not used for real vertex indexes
        NOMORE:  public MxFace()
        public MxFace(/* MxVertexID */int v0, /* MxVertexID */int v1, /* MxVertexID */int v2)
        NOMORE:  public MxFace(final MxFace f)
    '''
    self.v0 = v0
    self.v1 = v1
    self.v2 = v2
    self.mark = 0
    self.tag = MX_VALID_FLAG
    self.grpNo = grpNo # Original groupe id
    self.matIdx = matIdx # Preserve original material index

  def remap_vertex(self, ifrom:'MxVertexID', ito:'MxVertexID'):
    nmapped = 0
    if self.v0 == ifrom:
      self.v0 = ito
      nmapped+=1
    if self.v1 == ifrom:
      self.v1 = ito
      nmapped+=1
    if self.v2 == ifrom:
      self.v2 = ito
      nmapped+=1

    return nmapped

  def get(self, ptno): return self.v0 if ptno==0 else self.v1 if ptno==1 else self.v2

  def __str__(self):
    return 'F[{:d},{:d},{:d}, mat={:d}]'.format(self.v0, self.v1, self.v2, self.matIdx)


# 
class MxStdModel(object):
  '''
  public class MxStdModel extends MxBlockModel implements MixKit
  MxBlockModel inlined
  '''

  # public int binding_mask
  def __init__(self):
    self.vertices = [ ] # MxDynBlock(nvert, Point3d()) # MxVertex())
    self.protvert = set() # Set of protected vertices
    self.lstMat = [ 'default' ]
    self.faces = [ ] #MxDynBlock(nface, MxFace())
    self.tcoords = None
    self.tbinding = MX_UNBOUND
    self.binding_mask = MX_ALL_MASK
    #self.v_data = MxDynBlock(nvert, vertex_data()) --> v_data will be hold in Point3d (new attributes)
    #self.f_data = MxDynBlock(nface, face_data()) --> f_data are hold in MxFace
  
    # Replaced by a list(list(int))
    self.face_links = [] # MxDynBloc(nvert, MxDynBlock(6, int()), True)

  def add_vertex(self, x, y, z):
    np = Point3d(x, y, z)
    np.mark = 0
    np.tag = MX_VALID_FLAG
    self.vertices.append(np)
    self.face_links.append([])
    l = len(self.face_links)-1 # .last_id()
    return l
    
  #public/* MxFaceID */int add_face(int v1, int v2, int v3, boolean will_link /* =True */)
  def add_face(self, v1, v2, v3, isProtected, matIdx, grpNo):
    f = MxFace(v1, v2, v3, matIdx, grpNo)
    self.faces.append(f)
    vid = len(self.faces)-1

    # We always link if will_link: # self.init_face(vid)
    self.face_links[v1].append(vid)
    self.face_links[v2].append(vid)
    self.face_links[v3].append(vid)

    if isProtected:
      self.protvert.add(v1)
      self.protvert.add(v2)
      self.protvert.add(v3)

    return vid

  def add_texcoord(self, s, t):
    self.tcoords.append(TexCoord2f(s, t))
    return len(self.tcoords)-1 # .last_id()

  # Never called by PropSlim Algo
  def remove_vertex(self, v): 
    del self.face_links[v]
    del self.vertices[v]
    
    if self.texcoord_binding() == MX_PERVERTEX:
      del self.tcoords[v]


  @classmethod
  def binding_size(cls, m, i:'byte'):
    if i==MX_UNBOUND:
      return 0
    elif i==MX_PERVERTEX:
      return max(1, len(m.vertices))
    else:
      return 0

  def texcoord_binding(self, b:'byte'=0xffffffff):
    if b==0xffffffff: return (self.tbinding & (self.binding_mask >> 4))
    
    if b!=MX_UNBOUND and b!=MX_PERVERTEX:
      raise Exception("Illegal texture coordinate binding.")

    MxStdModel.binding_size(self, b)
    if self.tcoords:
      del self.tcoords[:] # .reset()
    else:
      self.tcoords = [] # MxDynBlock(size, TexCoord2f())

    self.tbinding = b

  bindings = [ "unbound", "face", "vertex" ]

  def binding_name(self, b):
    return None if b > MX_MAX_BINDING else MxStdModel.bindings[b]


  def compute_face_normal(self, f:MxFace, will_unitize=True):
    v1 = self.vertices[f.v0]     

    a = Point3d(self.vertices[f.v1]).sub(v1) # mixmops.mxv_sub(a, v2, v1, 3)
    b = Point3d(self.vertices[f.v2]).sub(v1) # mixmops.mxv_sub(b, v3, v1, 3)
    n = a.cross(b)       # mixmops.mxv_cross3(n, a, b)

    if will_unitize:
      n.normalize() # mixmops.mxv_unitize(n, 3)

    return n
  
  def compute_face_area(self, f):
    return 0.5 * self.compute_face_normal(f, False).norme()



  #///////////////////////////////////////////////////////////////////////
  #/ Contraction and related operations
  #/
  def compact_vertices(self):
    newID = 0 # /*MxVertexID*/int newID = 0

    for oldID,vtx in enumerate(self.vertices):
      #if self.vertex_is_valid(oldID):
      if vtx.tag & MX_VALID_FLAG:
        if newID!=oldID:
          self.vertices[newID].set(vtx)

          if self.texcoord_binding()==MX_PERVERTEX:
            self.tcoords[newID].set(self.tcoords[oldID])

          # Because we'll be freeing the link lists for the
          # old vertices, we actually have to swap values instead
          # of the simple copying in the block above.
          t = self.face_links[newID][:]
          self.face_links[newID][:] = self.face_links[oldID][:]
          self.face_links[oldID][:] = t[:] # .deepSet(t)

          # self.vertex_mark_valid(newID)
          self.vertices[newID].tag |= MX_VALID_FLAG

          for fid in self.face_links[newID]:
            self.faces[fid].remap_vertex(oldID, newID)
        newID+=1

    del self.face_links[newID:]
    del self.vertices[newID:]
    if self.texcoord_binding() == MX_PERVERTEX:
      del self.tcoords[newID:]
  
    

  def mark_neighborhood(self, vid, mark):
    for fi in self.face_links[vid]:
      self.faces[fi].mark = mark

  def collect_unmarked_neighbors(self, vid, faces:'list(int))'):
    for fid in self.face_links[vid]:
      if self.faces[fid].mark==0:
        faces.append(fid)
        self.faces[fid].mark = 1

  #public void collect_edge_neighbors(/* MxVertexID */int v1, /* MxVertexID */int v2, MxFaceList faces)
  def collect_edge_neighbors(self, v1, v2, faces):
    self.mark_neighborhood(v1, 1)
    self.mark_neighborhood(v2, 0)
    self.collect_unmarked_neighbors(v1, faces)

  def mark_neighborhood_delta(self, vid, delta):
    for fid in self.face_links[vid]:
      self.faces[fid].mark = 0xff & (self.faces[fid].mark + delta)

  #void partition_marked_neighbors(/*MxVertexID **/int v, int pivot, MxFaceList lo, MxFaceList hi)
  def partition_marked_neighbors(self, v, pivot, lo, hi):
    for fid in self.face_links[v]:
      if self.faces[fid].mark!=0:
        if self.faces[fid].mark < pivot:
          lo.append(fid)
        else:
          hi.append(fid)
        self.faces[fid].mark = 0

  #void mark_corners(MxFaceList faces, byte mark)
  def mark_corners(self, faces, mark):
    for fa in faces:
      self.vertices[self.faces[fa].v0].mark = mark
      self.vertices[self.faces[fa].v1].mark = mark
      self.vertices[self.faces[fa].v2].mark = mark
    
  #void collect_unmarked_corners(MxFaceList faces, MxVertexList verts)
  def collect_unmarked_corners(self, faces, verts):
    for fa in faces:
      for v in (self.faces[fa].v0,self.faces[fa].v1,self.faces[fa].v2):
        if self.vertices[v].mark==0:
          verts.append(v)
          self.vertices[v].mark = 1

  #public void collect_vertex_star(/* MxVertexID */int v, MxVertexList verts)
  def collect_vertex_star(self, v, verts):
    N = self.face_links[v] # list of int
    self.mark_corners(N, 0)
    self.vertices[v].mark = 1
    self.collect_unmarked_corners(N, verts)

  #void compute_contraction(/*MxVertexID*/int v1, /*MxVertexID*/int v2, MxPairContraction conx, float[] vnew /* = null */)
  def compute_contraction(self, v1, v2, conx, vnew=None):
    conx.v1 = v1
    conx.v2 = v2

    if vnew:
      #mixmops.mxv_sub(conx.dv1, vnew, vertex(v1).pos, 3)
      conx.dv1.sub(vnew, self.vetices[v1])
      conx.dv2.sub(vnew, self.vetices[v2])
    else:
      conx.dv1.set(0.0, 0.0, 0.0)
      conx.dv2.set(0.0, 0.0, 0.0)

    del conx.delta_faces[:] # .reset()
    del conx.dead_faces[:]

    # Mark the neighborhood of (v1,v2) such that each face is
    # tagged with the number of times the vertices v1,v2 occur
    # in it.  Possible values are 1 or 2.
    self.mark_neighborhood(v2, 0)
    self.mark_neighborhood(v1, 1)
    self.mark_neighborhood_delta(v2, 1)

    # Now partition the neighborhood of (v1,v2) into those faces
    # which degenerate during contraction and those which are merely
    # reshaped.
    self.partition_marked_neighbors(v1, 2, conx.delta_faces, conx.dead_faces)
    conx.delta_pivot = len(conx.delta_faces)
    self.partition_marked_neighbors(v2, 2, conx.delta_faces, conx.dead_faces)

  def unlink_face(self, fid):
    f = self.faces[fid]
    # self.face_mark_invalid(fid)
    f.tag &= ~MX_VALID_FLAG

    for flnk in (self.face_links[f.v0], self.face_links[f.v1], self.face_links[f.v2]):
      try:
        flnk.remove(fid)
      except ValueError:
        pass
    
      

  def apply_contraction(self, conx):
    v1 = conx.v1
    v2 = conx.v2

    # Move v1 to new position
    self.vertices[v1].add(conx.dv1)

    # Remove dead faces
    for fid in conx.dead_faces:
      self.unlink_face(fid)

    # Update changed faces
    for fid in conx.delta_faces[conx.delta_pivot:]:
      self.faces[fid].remap_vertex(v2, v1)
      self.face_links[v1].append(fid)

    # Kill v2
    self.vertices[v2].mark &= ~MX_VALID_FLAG
    del self.face_links[v2][:] # .reset()
  
 


  def read(self, geom:'WaveGeom', protEdges=False, protMat:'string'=None, lstProtFaces = None):
    ''' Convert a WaveGeom to an MxStdModel.
    
    Parameters:
    -----------
     protEdges: Boolean, optional, default False
      Indicate to the algorithm to freeze edges vertex.
      (It provides the means to protect interfaces between figures parts)
      
    protMat: str, optional, default None
      Indicate to the algorithm ot protect the faces with the given
      material name.
      
    lstProtFaces: iterable, optional, default None
      Indicate to the algorithm ot protect a given set of faces.
      Faces' numbers are relative to the input geometry (of course)
    
    '''
    # Copy Material list
    self.lstMat = geom.getMaterialList().copy()
    self.lstGrpName = [ g.getName() for g in geom.getGroups() ]
    
    # Copy all vertex
    for p in geom.coordList: # Avoid the getter who creates a copy
      self.add_vertex(p.x, p.y, p.z)

    # Create a tex coord mapping table
    # SMF format supporte one texture coord per vertex
    hasTexture = (geom.texList!=None) and (len(geom.texList) > 0)
    
    self.texcoord_binding(MX_PERVERTEX if hasTexture else MX_UNBOUND)

    if protMat:
      try:
        protMatIdx = geom.getMaterialList().index(protMat)
      except ValueError:
        logging.warning("Material[%s] is missing", protMat )

    if hasTexture:
      mapVT = [-1] * geom.getCoordListLength()
      try:
        for grp in geom.getGroups():
          vertIdxTbl = grp.vertIdx
          tvertIdxTbl = [-1] * len(grp.vertIdx) # grp.tvertIdx
          
          # I must admit that this kind of Vertex --> Texture mapping is FALSE!!
          for faceno, fao in enumerate(grp.matIdx):
            if fao.fAttr & C_FACE_TEXT:
              si = grp.getFaceStartIdx(faceno)
              ei = grp.getFaceLastIdx(faceno)
              tvertIdxTbl[si:ei] = fao.tvertIdx

          for i,v in enumerate(vertIdxTbl):
            mapVT[v] = tvertIdxTbl[i]
          
            
      except IndexError:
        logging.warning("Geom[%s] has bad texture index", geom.getName())
        hasTexture = False
        
      # Write out the texture coordinates
      nberror = 0
      for i in range(0, geom.getCoordListLength()):
        if mapVT[i]>=0:
          t = geom.texList[mapVT[i]]
        else:
          t = TexCoord2f(0, 0)
          nberror+=1
        self.add_texcoord(t.x, t.y)

    # Write the face of each group
    for grpNo, grp in enumerate(geom.getGroups()):
      
      # Keep group names
      self.lstGrpName.append(grp.getName())
      
      # Compute group edges (if required) and protect vertices   
      if protEdges:
        edges = grp.findEdges()
        for ed in edges:
          self.protvert.add(ed.idx0)
          self.protvert.add(ed.idx1)
          
      vertIdxTbl = grp.vertIdx
      for noface in range(0, grp.getNbFace()):
        startIdx = grp.getFaceStartIdx(noface)
        lastIdx = grp.getFaceLastIdx(noface)
        argc = lastIdx - startIdx
        matIdx = grp.getMatIdx(noface)

        isprotected = (protMat and protMatIdx==matIdx) or \
          (lstProtFaces and (noface in lstProtFaces))

        v0 = vertIdxTbl[startIdx]
        v1 = vertIdxTbl[startIdx+1]
        v2 = vertIdxTbl[startIdx+2]

        if argc==3:
          self.add_face(v0, v1, v2, isprotected, matIdx, grpNo)
        elif argc==4:
          v3 = vertIdxTbl[startIdx+3]          

          e0 = Point3d(self.vertices[v1]).sub(self.vertices[v0]).normalize()
          e1 = Point3d(self.vertices[v2]).sub(self.vertices[v1]).normalize()
          e2 = Point3d(self.vertices[v3]).sub(self.vertices[v2]).normalize()
          e3 = Point3d(self.vertices[v0]).sub(self.vertices[v3]).normalize()

          a_02 = (1 - e0.dot(e3)) + (1 - e1.dot(e2))
          a_13 = (1 - e1.dot(e0)) + (1 - e3.dot(e2))
          # Comparison with Java Algo : Accuracy changes
          if a_02 <= a_13:
            self.add_face(v0, v1, v2, isprotected, matIdx, grpNo)
            self.add_face(v0, v2, v3, isprotected, matIdx, grpNo)
          else:
            self.add_face(v0, v1, v3, isprotected, matIdx, grpNo)
            self.add_face(v1, v2, v3, isprotected, matIdx, grpNo)
        else:
          # print('Input polygon #{:d} has {:d} sides. Triangularize it.'.format(noface, argc))
          
          # Compute the  isobarycentre
          isoG = Point3d()
          t= TexCoord2f()
          for vno in vertIdxTbl[startIdx:lastIdx]:
            isoG.add(self.vertices[vno])
            if hasTexture:
              t.add(geom.texList[mapVT[vno]])
          gno = len(self.vertices)
          isoG.scale(1.0/float(argc))
          t.scale(1.0/float(argc))
          self.add_vertex(isoG.x, isoG.y, isoG.z)
            
          if hasTexture:
            self.add_texcoord(t.x, t.y)
              
          for i in range(startIdx, lastIdx-1):
            self.add_face(gno, vertIdxTbl[i], vertIdxTbl[i+1], isprotected, matIdx, grpNo)
            
          self.add_face(gno, vertIdxTbl[lastIdx-1], vertIdxTbl[startIdx], isprotected, matIdx, grpNo)

    logging.info("Geom[%s] with %d polygons has %d triangles", geom.getName(), geom.getNbFace(), len(self.faces))
    return self


  def createWaveGeom(self, restoreGrp=False, restoreQuad=False):
    ''' Convert a MxStdModel into a WaveGeom.
    
    Parameters
    ----------
    restoreQuad: Boolean, optional, default False
      Try to merge triangles to rebuild 'quadrangle' faces
      
    restoreGrp: Boolean, optional, default False
      Preserve (and recreate) the groups in the result geometry.
      
    Returns
    -------
      WaveGeom
        A new WaveGeom
    '''      
    # Create the new (output) WaveGeom
    nwg = WaveGeom()
    nwg.lstMat = self.lstMat.copy()

    # Rebuild all groups (to preserve group indexes)
    for grpname in self.lstGrpName if restoreGrp else [ 'decimate',]:
      nwg.createGeomGroup(grpname)

    # Create new Point3d, because they've been modified with .mark and .tag
    nwg.coordList += [ Point3d(v) for v in self.vertices ]

    hasTexture = (self.texcoord_binding()!=MX_UNBOUND)
    if hasTexture:
      nwg.texList += self.tcoords

    prevFace = None
    prefGrpNo = -1
    curGroup = nwg.getGroups()[0]
    
    for fx in self.faces: # range(0, self.face_count()):
      
      if restoreGrp and (prefGrpNo!=fx.grpNo):
        curGroup  = nwg.getGroups()[fx.grpNo]
        prefGrpNo = fx.grpNo
        prevFace  = None  
      
      if fx.tag & MX_VALID_FLAG:
        # Add face to current groups
        if restoreQuad and prevFace and (curGroup.curMatIdx == fx.matIdx):
          lprevEdge = ( (prevFace[2], prevFace[1]), (prevFace[0], prevFace[2]), (prevFace[1], prevFace[0]) )
           
          try:
            keepNo = lprevEdge.index( (fx.v0, fx.v1) )            
          except ValueError:
            keepNo = -1
            
          if keepNo>0: # Keep pv2, remove edge v0, v1
            # Remove previous face (the last one)
            curGroup.removeFace(faceno=curGroup.getNbFace()-1)
            
            # Previous face as a common edge - Merge along this edge
            l = [fx.v0, prevFace[keepNo], fx.v1, fx.v2]
            curGroup.curMatIdx = fx.matIdx
            curGroup.addFace(l, l if hasTexture else [], [])
            prevFace = None
            continue

          try:
            keepNo = lprevEdge.index( (fx.v1, fx.v2) )            
          except ValueError:
            keepNo = -1
            
          if keepNo>0: # Keep pv0, remove edge v1, v2
            # Remove previous face (the last one)
            curGroup.removeFace(faceno=curGroup.getNbFace()-1)
            
            # Previous face as a common edge - Merge along this edge
            l = [fx.v0, fx.v1, prevFace[keepNo], fx.v2]
            curGroup.curMatIdx = fx.matIdx
            curGroup.addFace(l, l if hasTexture else [], [])
            prevFace = None
            continue

          try:
            keepNo = lprevEdge.index( (fx.v2, fx.v0) )            
          except ValueError:
            keepNo = -1
            
          if keepNo>0: # Keep pv1, remove edge v2, v0
            # Remove previous face (the last one)
            curGroup.removeFace(faceno=curGroup.getNbFace()-1)
            
            # Previous face as a common edge - Merge along this edge
            l = [fx.v0, fx.v1, fx.v2, prevFace[keepNo]]
            curGroup.curMatIdx = fx.matIdx
            curGroup.addFace(l, l if hasTexture else [], [])
            prevFace = None
            continue

        #else:
        # No Quadrangle restoration OR
        # Previous face as a different material OR
        # Not 'continue' (ie. faces are not sharing any edge)
        prevFace = [fx.v0, fx.v1, fx.v2]
        curGroup.curMatIdx = fx.matIdx
        curGroup.addFace(prevFace, prevFace if hasTexture else [], [])

    # Close Groups
    nwg.optimizeGroups(cleaning=False)

    return nwg









