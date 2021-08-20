"""
graphicsHelper.py

Functions to help build graphics data
"""

import igeCore as core
import igeVmath as vmath
import math

_uvs = (0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0)
_tris = (0, 2, 1, 1, 2, 3)
_pivotoffset = (1,-1, 0,-1, -1,-1, 1,0, 0,0, -1,0, 1,1, 0,1, -1,1)

def textFigure(word, fontpath, fontsize,color=(1.0, 1.0, 1.0, 1.0), pivot=4, scale = 1.0):
    '''
    Create Visible text

    Parameters
    ----------
        word : string
            text
        fontpath : string
            font data file path
        fontsize : string
            font size
        color : (float,float,float,float)
            text color
        pivot : int
            center point of polygon
            0       1       2
             +-------+-------+
             |       |       |
            3|      4|      5|
             +-------+-------+
             |       |       |
            6|      7|      8|
             +-------+-------+
    '''

    w,h = core.calcFontPixelSize(word, fontpath, fontsize)
    tex = core.texture(core.unique("text"),w,h, format=core.GL_RED)
    tex.setText(word, fontpath,fontsize)

    gen = core.shaderGenerator()
    gen.setColorTexture(True)
    gen.setBoneCondition(1, 1)
    gen.discardColorMapRGB()

    hw = w/2 * scale
    hh = h/2 * scale
    px = _pivotoffset[pivot*2+0] * hw;
    py = _pivotoffset[pivot*2+1] * hh;

    points = ((-hw+px,hh+py,0.0), (hw+px,hh+py,0.0), (-hw+px,-hh+py,0.0), (hw+px,-hh+py,0.0))

    efig = createMesh(points, _tris, None, _uvs, gen)

    efig.setMaterialParam("mate", "DiffuseColor", color);
    efig.setMaterialParamTexture("mate", "ColorSampler", tex,
                                    wrap_s=core.SAMPLERSTATE_BORDER,wrap_t=core.SAMPLERSTATE_BORDER,
                                    minfilter=core.SAMPLERSTATE_NEAREST, magfilter=core.SAMPLERSTATE_LINEAR)
    efig.setMaterialRenderState("mate", "blend_enable", True)

    return efig

def createSprite(width:float=100, height:float=100, texture=None, uv_left_top:tuple=(0,0), uv_right_bottom:tuple=(1,1), normal=None, pivot=4, shader=None):
    """
    Create Visible Rectangle

	Parameters
	----------
        width : float (optional)
            sprite width
        height: float (optional)
            sprite height
        texture: string (optional)
            texture file name
        uv_left_top: tuple (optional)
            texture uv value of left top cornar
        uv_right_bottom: tuple (optional)
            texture uv value of right bottom cornar
        normal: pyvmath.vec3 (optional)
            specify rectangle's nomal vector
        pivot : int
            center point of polygon
        shader : igeCore.shader
            shader object
	Returns
	-------
        editableFigure
    """
    hw = width/2
    hh = height/2
    px = _pivotoffset[pivot*2+0] * hw;
    py = _pivotoffset[pivot*2+1] * hh;
    points = ((-hw+px,hh+py,0.0), (hw+px,hh+py,0.0), (-hw+px,-hh+py,0.0), (hw+px,-hh+py,0.0))

    if normal is not None:
        newpoints = []
        nom0 = (0, 0, 1)
        mat = vmath.mat33(vmath.quat_rotation(nom0, normal))
        for p in points:
            newpoints.append(mat * p)
        points = newpoints

    # uvs = (uv_left_top[0], uv_right_bottom[1],
    #        uv_right_bottom[0], uv_right_bottom[1],
    #        uv_left_top[0], uv_left_top[1],
    #        uv_right_bottom[1], uv_left_top[1])
    uvs = ( uv_left_top[0], uv_right_bottom[1],
            uv_right_bottom[0], uv_right_bottom[1],
            uv_left_top[0], uv_left_top[1],
            uv_right_bottom[0], uv_left_top[1])

    return createMesh(points, _tris, texture, uvs, shader)

def createMesh(points, tris, texture=None, uvs = None, shader = None, normals = None):
    """
    Create a polygon mesh by specifying vertex coordinates and triangle index

	Parameters
	----------
        points: tuple or list
            list or tuple of points
        tris: tuple or list
            list or tuple of triangle indices
        texture: string (optional)
            file path of texture
        uvs: list or tuple (optional)
        shader : igeCore.shader
            shader object
        normals : list or tuple (optional)
            list or tuple of  vertex normal

	Returns
	-------
        editableFigure
   
    """
    if shader is None:
        shader = core.shaderGenerator()
        if texture != None:
            shader.setColorTexture(True)
        shader.setBoneCondition(1, 1)

    efig = core.editableFigure("sprite", True)
    efig.addMaterial("mate", shader)
    efig.addMesh("mesh", "mate");

    efig.setVertexElements("mesh", core.ATTRIBUTE_ID_POSITION, points)
    if uvs:
        efig.setVertexElements("mesh", core.ATTRIBUTE_ID_UV0,uvs)

    if  normals:
        efig.setVertexElements("mesh", core.ATTRIBUTE_ID_NORMAL,normals)

    efig.setTriangles("mesh", tris);
    efig.addJoint("joint");
    efig.setMaterialParam("mate", "DiffuseColor", (1.0, 1.0, 1.0, 1.0));
    #efig.setMaterialRenderState("mate", "cull_face_enable", False)

    if texture != None:
        efig.setMaterialParamTexture("mate", "ColorSampler", texture,
                                     wrap_s=core.SAMPLERSTATE_BORDER,wrap_t=core.SAMPLERSTATE_BORDER,
                                     minfilter=core.SAMPLERSTATE_LINEAR, magfilter=core.SAMPLERSTATE_LINEAR)
        efig.setMaterialRenderState("mate", "blend_enable", True)

    return efig

def __tranform(normal, poss, noms):
	nom0 = (0, 0, 1)

	newpoints = []
	mat = vmath.mat33(vmath.quat_rotation(nom0, normal))
	for p in poss:
		newpoints.append(mat * p)
	poss = newpoints
	newnoms = []
	for n in noms:
		newnoms.append(mat * n)
	noms = newnoms

	return poss, noms

###################################################################################################
plane_triangles=(0, 2, 1, 1, 2, 3)
def makePlane(width:float, height:float, uv_left_top:tuple=(0,0), uv_right_bottom:tuple=(1,1), normal=None, jointIndex=0):
    w = width / 2
    h = height / 2
    poss = (vmath.vec3(-w, h, 0.0), vmath.vec3(w, h, 0.0), vmath.vec3(-w, -h, 0.0), vmath.vec3(w, -h, 0.0))

    uvs = (vmath.vec2(uv_left_top[0], uv_right_bottom[1]),
            vmath.vec2(uv_right_bottom[0], uv_right_bottom[1]),
            vmath.vec2(uv_left_top[0], uv_left_top[1]),
            vmath.vec2(uv_right_bottom[1], uv_left_top[1]))

    nom = vmath.vec3(0,0,1)
    noms = (nom,)*4

    if normal is not None:
        poss, noms = __tranform(normal, poss, noms)

    idxs = ((jointIndex,0,0,0),)*len(poss)

    return poss, noms, uvs, idxs, plane_triangles

###################################################################################################
cubeN = ((-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0),
		 (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0))
cubeF = ((0, 1, 5, 4), (4, 5, 6, 7), (7, 6, 2, 3),
		 ( 1, 0, 3, 2 ), ( 1, 2, 6, 5 ), ( 0, 4, 7, 3 ))
cubeV = ((-.5, -.5, -.5), (-.5, -.5,  .5), ( .5, -.5,  .5), ( .5, -.5, -.5),	# Lower tier (lower in y)
		 (-.5, .5, -.5), (-.5, .5,  .5), ( .5, .5, .5), ( .5, .5, -.5)) 		# Upper tier

cubeT = ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0))

def makeBox(width:float, height:float, depth:float, jointIndex=0):
    poss = []
    noms = []
    uvs = []
    tris = []

    nvrt = 0
    for i in range(6):
        for j in range(4):
            poss.append(vmath.vec3(cubeV[cubeF[i][j]][0] * width, cubeV[cubeF[i][j]][1] * height, cubeV[cubeF[i][j]][2] * depth))
            noms.append(vmath.vec3(cubeN[i][0], cubeN[i][1], cubeN[i][2]))
            uvs.append(vmath.vec2(cubeT[j][0], cubeT[j][1]))
        tris.append(nvrt)
        tris.append(nvrt + 1)
        tris.append(nvrt + 2)
        tris.append(nvrt + 2)
        tris.append(nvrt + 3)
        tris.append(nvrt)
        nvrt += 4

    idxs = ((jointIndex,0,0,0),)*len(poss)

    return poss, noms, uvs, idxs, tris

###################################################################################################
def makeBoxFromAABB(min , max, jointIndex=0):
    cubeV2 = ((min.x, min.y, min.z), (min.x, min.y,  max.z), (max.x, min.y, max.z), (max.x, min.y, min.z),
                (min.x, max.y, min.z), (min.x, max.y,  max.z), (max.x, max.y, max.z), (max.x, max.y, min.z))
    poss = []
    noms = []
    uvs = []
    tris = []

    nvrt = 0
    for i in range(6):
        for j in range(4):
            poss.append((cubeV2[cubeF[i][j]][0], cubeV2[cubeF[i][j]][1], cubeV2[cubeF[i][j]][2]))
            noms.append((cubeN[i][0], cubeN[i][1], cubeN[i][2]))
            uvs.append((cubeT[j][0], cubeT[j][1]))

        tris.append(nvrt)
        tris.append(nvrt + 1)
        tris.append(nvrt + 2)
        tris.append(nvrt + 2)
        tris.append(nvrt + 3)
        tris.append(nvrt)
        nvrt += 4

    idxs = ((jointIndex,0,0,0),)*len(poss)

    return poss, noms, uvs, idxs, tris

###################################################################################################
def makeCylinder(radius1:float, radius2:float, length:float, slices:int, stacks:int, normal=None, jointIndex=0):

    # Sin/Cos caches
    sinI = []
    cosI = []
    for i in range(slices):
        angle = 2.0 * math.pi * i / slices
        sinI.append(math.sin(angle))
        cosI.append(math.cos(angle))

    # Compute side normal angle
    deltaRadius = radius2 - radius1
    sideLength = math.sqrt( deltaRadius * deltaRadius + length * length )

    normalXY = 1.0
    if sideLength > 0.00001:
        normalXY =  length / sideLength

    normalZ = 0.0
    if sideLength > 0.00001:
        normalZ = deltaRadius / sideLength

    # Base cap (uSlices + 1)
    fZ = length * -0.5
    radius = radius1

    poss = []
    noms = []
    uvs = []
    tris = []

    poss.append((0.0, 0.0, fZ))
    noms.append((0.0, 0.0, -1.0))
    uvs.append((0.0, 0.0))

    for i in range(slices):
        poss.append((radius * sinI[i], radius * cosI[i], fZ))
        noms.append((0.0, 0.0, -1.0))
        uvs.append((0.0, 0.0))

    # Stacks ((uStacks + 1)*uSlices)
    for j in range(stacks+1):
        f = j / stacks
        fZ = length * ( f - 0.5 )
        radius = radius1 + f * deltaRadius

        for i in range(slices):
            poss.append((radius * sinI[i], radius * cosI[i], fZ))
            noms.append((normalXY * sinI[i], normalXY * cosI[i], normalZ))
            uvs.append((0.0, 0.0))

    # Top cap (uSlices + 1)
    fZ = length * 0.5
    radius = radius2

    for i in range(slices):
        poss.append((radius * sinI[i], radius * cosI[i], fZ))
        noms.append((0.0, 0.0, 1.0))
        uvs.append((0.0, 0.0))
    poss.append((0.0, 0.0, fZ))
    noms.append((0.0, 0.0, 1.0))
    uvs.append((0.0, 0.0))

    if normal is not None:
        poss, noms = __tranform(normal, poss, noms)


    # Generate indices

    # Z+ pole (uSlices)
    rowA = 0
    rowB = 1

    for i in range(slices - 1):
        tris.append( rowA )
        tris.append( rowB + i )
        tris.append( rowB + i + 1 )

    tris.append( rowA )
    tris.append( rowB + slices - 1 )
    tris.append( rowB )

    # Interior stacks (uStacks * uSlices * 2)
    for j in range(stacks):
        rowA = 1 + ( j + 1 ) * slices
        rowB = rowA + slices
        for i in range(slices - 1):
            tris.append( rowA + i )
            tris.append( rowB + i )
            tris.append( rowA + i + 1 )
            tris.append( rowA + i + 1 )
            tris.append( rowB + i )
            tris.append( rowB + i + 1 )

        tris.append( rowA + slices - 1 )
        tris.append( rowB + slices - 1 )
        tris.append( rowA )

        tris.append( rowA )
        tris.append( rowB + slices - 1 )
        tris.append( rowB )

    # Z- pole (uSlices)
    rowA = 1 + ( stacks + 2 ) * slices
    rowB = rowA + slices

    for i in range(slices - 1):
        tris.append( rowA + i )
        tris.append( rowB )
        tris.append( rowA + i + 1 )

    tris.append( rowA + slices - 1 )
    tris.append( rowB )
    tris.append( rowA )

    idxs = ((jointIndex,0,0,0),) * len(poss)

    return poss, noms, uvs, idxs, tris

###################################################################################################
def makeSphere(radius:float, slices:int, stacks:int, jointIndex=0 ):

    # Sin/Cos caches
    sinI = []
    cosI = []
    sinJ = []
    cosJ = []

    for i in range(slices):
        angle = 2.0 * math.pi * i / slices
        sinI.append(math.sin(angle))
        cosI.append(math.cos(angle))

    for j in range(stacks):
        angle = math.pi * j / stacks
        sinJ.append(math.sin(angle))
        cosJ.append(math.cos(angle))

    poss = []
    noms = []
    uvs = []
    tris = []

    # +Z pole
    poss.append(vmath.vec3(0.0, 0.0, radius))
    noms.append(vmath.vec3(0.0, 0.0, 1.0))
    uvs.append(vmath.vec2(0.0, 0.0))

    # Stacks
    for j in range(stacks):
        for i in range(slices):
            norm = vmath.vec3(sinI[i] * sinJ[j], cosI[i] * sinJ[j], cosJ[j])
            poss.append(vmath.vec3(norm.x * radius, norm.y * radius, norm.z * radius))
            noms.append(norm)
            uvs.append(vmath.vec2(0.0, 0.0))

    # Z- pole
    poss.append(vmath.vec3(0.0, 0.0, -radius))
    noms.append(vmath.vec3(0.0, 0.0, -1.0))
    uvs.append(vmath.vec2(0.0, 0.0))

    # Generate indices
    # Z+ pole
    rowA = 0
    rowB = 1

    # for i in range(slices-1):
    #     tris.append( rowA )
    #     tris.append( rowB + i + 1 )
    #     tris.append( rowB + i )
    # tris.append( rowA )
    # tris.append( rowB )
    # tris.append( rowB + slices-1 )

    # Interior stacks
    for j in range(1,stacks):
        rowA = 1 + (j - 1) * slices
        rowB = rowA + slices
        for i in range(slices - 1):
            tris.append(rowA + i)
            tris.append(rowA + i + 1)
            tris.append(rowB + i)

            tris.append(rowA + i + 1)
            tris.append(rowB + i + 1)
            tris.append(rowB + i)

        tris.append(rowA + slices - 1)
        tris.append(rowA)
        tris.append(rowB + slices - 1)

        tris.append(rowA)
        tris.append(rowB)
        tris.append(rowB + slices - 1)

    #Z- pole
    rowA = 1 + (stacks - 1) * slices
    rowB = rowA + slices

    for i in range(slices - 1):
        tris.append(rowA + i)
        tris.append(rowA + i + 1)
        tris.append(rowB)

    tris.append(rowA + slices - 1)
    tris.append(rowA)
    tris.append(rowB)

    idxs = ((jointIndex,0,0,0),) * len(poss)

    return poss, noms, uvs, idxs, tris

###################################################################################################
def makeTorus(innerRadius:float, outerRadius:float, sides:int, rings:int, normal=None, jointIndex=0):

    poss = []
    noms = []
    uvs = []
    tris = []

    # Compute the vertices
    for i in range(rings):
        theta = i * 2.0 * math.pi / rings
        st = math.sin(theta)
        ct = math.cos(theta)
        for j in range(sides):
            phi = j * 2.0 * math.pi / sides
            sp = math.sin(phi)
            cp = math.cos(phi)
            poss.append((ct * ( outerRadius + innerRadius * cp ), -st * ( outerRadius + innerRadius * cp ), sp * innerRadius))
            noms.append((ct * cp, -st * cp, sp))
            uvs.append((0.0, 0.0))

    if normal is not None:
    	poss, noms = __tranform(normal, poss, noms)

    for i in range(rings - 1):
        for j in range(sides - 1):
            # Tri 1 (Top-Left tri, CCW)
            tris.append( i * sides + j )
            tris.append( i * sides + j + 1 )
            tris.append( ( i + 1 ) * sides + j )

            # Tri 2 (Bottom-Right tri, CCW)
            tris.append( ( i + 1 ) * sides + j )
            tris.append( i * sides + j + 1 )
            tris.append( ( i + 1 ) * sides + j + 1 )

        j = sides - 1
        # Tri 1 (Top-Left tri, CCW)
        tris.append( i * sides + j )
        tris.append( i * sides )
        tris.append( ( i + 1 ) * sides + j )

        # Tri 2 (Bottom-Right tri, CCW)
        tris.append( ( i + 1 ) * sides + j )
        tris.append( i * sides + 0 )
        tris.append( ( i + 1 ) * sides + 0 )

    i = rings-1
    #join the two ends of the tube
    for j in range(sides - 1):
        # Tri 1 (Top-Left tri, CCW)
        tris.append( i * sides + j )
        tris.append( i * sides + j + 1 )
        tris.append( j )

        # Tri 2 (Bottom-Right tri, CCW)
        tris.append( j )
        tris.append( i * sides + j + 1 )
        tris.append( j + 1 )

    j = sides-1
    # Tri 1 (Top-Left tri, CCW)
    tris.append( i * sides + j )
    tris.append( i * sides )
    tris.append( j )

    # Tri 2 (Bottom-Right tri, CCW)
    tris.append( j )
    tris.append( i * sides )
    tris.append( 0 )

    idxs = ((jointIndex,0,0,0),) * len(poss)

    return poss, noms, uvs, idxs, tris

