# -*- coding: utf-8 -*-
'''
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
__version__ = '1.0'
__author__  = 'Olivier DUFAILLY (python3 code), Michael Garland (algorithm)'
__license__ = 'BSD or GPL v2'

MX_VALID_FLAG = 0x01
#MX_PROXY_FLAG = 0x02
#MX_TOUCHED_FLAG = 0x04
MX_UNBOUND = 0x0
#MX_PERFACE = 0x1
MX_PERVERTEX = 0x2
MX_MAX_BINDING = 0x2
MX_NORMAL_MASK = 0x3
MX_COLOR_MASK = (0x3 << 2)
MX_TEXTURE_MASK = (0x3 << 4)
MX_ALL_MASK = (MX_NORMAL_MASK | MX_COLOR_MASK | MX_TEXTURE_MASK)

