# -*- coding: utf-8 -*-
# package: pypos3d.wftk
import sys
import numpy as np

from pypos3d.wftk.WFBasic import Point3d, Vector3d, Invert2x2, MxProd, MxProdMatVect


#
# TODO: Merge with CoordSyst
#
class Repere(object):
  ''' Another Coordinate system (for hole filling and morph enhancement)
  DO NOT use externaly ... Should be merged with 'CoordSyst'
  '''

  def __init__(self, nbLoopPt, edgeLoopPtIdx, tabpt):
    ''' Create a repere at the center of a Cloud of indexed vertex. Using SVD algorithm.

    Parameters
    ----------
    nbLoopPt : int
      Number of index to use
    edgeLoopPtIdx : list of int
      Index of vertex in the vertex table
    tabpt : list of Point3d
      Vertex table
    '''    
    self.origin = Point3d()
    self.u = Vector3d()
    self.v = Vector3d()
    self.n = Vector3d()
    self.init(nbLoopPt, edgeLoopPtIdx, tabpt)

  # 
  #    
  def init(self, nbLoopPt, edgeLoopPtIdx, tabpt):
    ''' Initialize a repere (coord syst) at the center of a Cloud of indexed vertex.
    Using SVD algorithm.

    Parameters
    ----------
    nbLoopPt : int
      Number of index to use
    edgeLoopPtIdx : list of int
      Index of vertex in the vertex table
    tabpt : list of Point3d
      Vertex table
    '''
    avg = Point3d()
    M1 = [ None ] * nbLoopPt
    
    for i in range(0, nbLoopPt):
      M1[i] = [ tabpt[edgeLoopPtIdx[i]].x, tabpt[edgeLoopPtIdx[i]].y, tabpt[edgeLoopPtIdx[i]].z ]
      avg.add(M1[i])

    avg.scale( 1.0 / nbLoopPt)
    self.origin = Point3d(avg)
    M = [ [ pv[0]-avg.x, pv[1]-avg.y, pv[2]-avg.z ] for pv in M1 ]
    # ODY 20200513 : Swap Y and Z, because of behaviors of svd !
    # M = [ [ pv[0]-avg.x, pv[2]-avg.z, pv[1]-avg.y ] for pv in M1 ]

    npM = np.array(M)
    # w = [ 0.0 ]*3
    # V = [ [0.0, 0.0, 0.0] ]*3
    oldV,w,V = np.linalg.svd(M)

    # Search for minimal value of D
    minidx = 0
    minval = sys.float_info.max
        
    for i in range(0, 3):
      if w[i] < minval:
        minidx = i
        minval = w[i]

    # C'est (u,n,v) qui est direct
    self.n = Vector3d(V[minidx][0], V[minidx][1], V[minidx][2])
    # self.n = Vector3d(V[0][minidx], V[1][minidx], V[2][minidx])
    vidx = (minidx + 1) % 3
    uidx = (minidx + 2) % 3
    self.u = Vector3d(V[uidx][0], V[uidx][1], V[uidx][2])
    self.v = Vector3d(V[vidx][0], V[vidx][1], V[vidx][2])


  def project(self, startIdx, destIdx, nbPt, edgeLoopPtIdx, tabpt, destTabpt=None):
    ''' Project the nbLoopPt vertex indexed by edgeLoopPtIdx onto the UV plan.

    Parameters
    ----------
    startIdx : int
      Start Position in source table
 
    destIdx : int
      Start Position in result table

    nbPt    : int
      Number of index to consider

    edgeLoopPtIdx : list of int
      Index table

    tabpt : list of Point3d
      Vertex table (Read-Only)

    destTabPt : list       
      Destination Table. Allocated by 'project' if null

    Returns
    -------
    list of Point3d
      A new table of vertex (destIdx+nbLoopPt vertex allocated)
 
    '''
    # Distance to the plane Calc
    dn = Vector3d()

    # Prepare the projection matrix onto U,V plane
    B = [ [self.u.x, self.v.x], \
          [self.u.y, self.v.y], \
          [self.u.z, self.v.z] ]

    # BT.transpose(B)
    BT = [ [self.u.x, self.u.y, self.u.z], \
           [self.v.x, self.v.y, self.v.z] ]

    #BTB = GMatrix(2, 2)
    #BTB.mul(BT, B)
    BTB = MxProd(BT, B)

    BTB = Invert2x2(BTB)

    #BTBBT = GMatrix(2, 3)
    BTBBT = MxProd(BTB, BT)
        
    # Vab = GVector(2)
    Vab = [ 0.0, 0.0 ]
    tabproj = [ None ]*(destIdx + nbPt) if not destTabpt else destTabpt
    tmp = Vector3d()
    for i in range(0,nbPt):
      tmp.set(tabpt[edgeLoopPtIdx[startIdx + i]])
      tmp.sub(self.origin)
    
      d = self.n.dot(tmp)

      # OXp = OX - d.n
      dn.set(self.n)
      dn.scale(d)
      tmp.sub(dn)

      # Solve : xp = alpha.u + beta.v
      # Vab = (alpha, beta) : Projection de tabpt[i] sur le plan U,V
      OXp = Vector3d(tmp)
      Vab = MxProdMatVect(BTBBT, [OXp.x, OXp.y, OXp.z])
      tabproj[destIdx + i] = Point3d(Vab[0], Vab[1], d)
      
    return tabproj

  def reserveProject(self, startIdx, destIdx, nbPt, edgeSamp, destTabpt = None):
    ''' Reverse Project the nPt vertex of edgeSamp.

    Parameters
    ----------
    startIdx : int
      Start Position in source table
 
    destIdx : int
      Start Position in result table

    nbPt    : int
      Number of index to consider

    edgeSamp : list of Point3d
      Vertex to Reverse Project

    destTabPt : list       
      Destination Table. Allocated by 'project' if null

    Returns
    -------
    list of Point3d
      A (new) table of vertex (destIdx+nbPt vertex allocated)
      Padded with None, where vertex where not reversed [0..destIdx[
 
    '''
    resTab = [None]*(destIdx + nbPt) if not destTabpt else destTabpt

    mtrans = [ [self.u.x, self.v.x, self.n.x], \
          [self.u.y, self.v.y, self.n.y], \
          [self.u.z, self.v.z, self.n.z] ]

    j = destIdx
    for i in range(startIdx, startIdx + nbPt):
      vtmp = edgeSamp[i].Lin33(mtrans)
      vtmp.add(self.origin)
      resTab[j] = vtmp
      j += 1

    return resTab

