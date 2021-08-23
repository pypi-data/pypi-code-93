import ctypes
import time

import numpy as np
from OpenGL import GL
from OpenGL.GL.ARB.texture_rg import GL_R32F
from PySide6 import QtGui, QtOpenGLWidgets
from PySide6.QtOpenGL import *

# from PyQt5 import QtCore, QtGui, QtOpenGL, QtWidgets

# w, h = 400, 400

# class TestWidget(QGLWidget):
    
#     def __init__(self):
#         QGLWidget.__init__(self)
#         self.resize(w, h)

#         self.t = time.time()        
#         self._update_timer = QtCore.QTimer()
#         self._update_timer.timeout.connect(self.update)        
#         self._update_timer.start(1e3 / 60.)
    
#     def initializeGL(self):
#         # create an image
#         Y, X = np.ogrid[-2.5:2.5:h*1j, -2.5:2.5:w*1j]
#         image = np.empty((h, w), dtype=np.float32)
#         image[:] = np.exp(- X**2 - Y**2)# * (1. + .5*(np.random.rand(h, w)-.5))
#         image[-30:] = np.linspace(0, 1, w)
              
#         # create pixel buffer object for transferring textures
#         self._buffer_id = GL.glGenBuffers(1)
#         GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, self._buffer_id)
#         GL.glBufferData(GL.GL_PIXEL_UNPACK_BUFFER, w*h*4, None, GL.GL_STREAM_DRAW)
#         GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)

#         # map and modify pixel buffer
#         GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, self._buffer_id)
#         pbo_addr = GL.glMapBuffer(GL.GL_PIXEL_UNPACK_BUFFER, GL.GL_WRITE_ONLY)
#         # write to PBO using ctypes memmove
#         ctypes.memmove(pbo_addr, image.ctypes.data, (w*h * image.itemsize))
#         # write to PBO using numpy interface
#         pbo_ptr = ctypes.cast(pbo_addr, ctypes.POINTER(ctypes.c_float))
#         pbo_np = np.ctypeslib.as_array(pbo_ptr, shape=(h, w))
#         pbo_np[:] = image
#         GL.glUnmapBuffer(GL.GL_PIXEL_UNPACK_BUFFER)
#         GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)
        
#         # create texture from pixel buffer object
#         self._texture_id = GL.glGenTextures(1)
#         GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, self._buffer_id)
#         GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
#         GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
#         GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
#         GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL_R32F, w, h, 0, GL.GL_RED, GL.GL_FLOAT, None)
#         GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)
        
#         # create a shader for coloring the texture
#         shader_program = QtGui.QOpenGLShaderProgram()
#         vertex_src = """
#         void main() {
#             gl_TexCoord[0] = gl_MultiTexCoord0;
#             gl_Position = gl_Vertex;
#         }
#         """
#         fragment_src = """
#         uniform highp sampler2D tex;
#         uniform float amp;
#         uniform float r;
        
#         float rand(vec2 co){
#             return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453 * (1.+r));
#         }
        
#         void main() {
#             float val = texture2D(tex, gl_TexCoord[0]).r;
#             val *= .7 + .3*rand(gl_TexCoord[0].xx) + .8*rand(gl_TexCoord[0].xy);
#             vec4 color1 = vec4(0., 0., 0., 1.);
#             vec4 color2 = vec4(3., .5, .2, 1.);
#             gl_FragColor = mix(color1, color2, 3.5 * val * amp);
#         }
#         """
#         shader_program.addShaderFromSourceCode(QtGui.QOpenGLShader.Vertex, vertex_src)
#         shader_program.addShaderFromSourceCode(QtGui.QOpenGLShader.Fragment, fragment_src)
#         shader_program.link()
#         self._shader_program = shader_program
#         self._amp_location = shader_program.uniformLocation("amp")
#         self._r_location = shader_program.uniformLocation("r")

#     def paintGL(self):
#         t = time.time()
#         amp = .6 + .6*np.cos(t*np.pi)**10
#         r = np.random.rand(1)[0]
        
#         target = QtCore.QRectF(-1, -1, 2, 2)
#         self._shader_program.bind()
#         self._shader_program.setUniformValue(self._amp_location, amp)
#         self._shader_program.setUniformValue(self._r_location, r)
#         self.drawTexture(target, self._texture_id)
    
#     def resizeGL(self, w, h):
#         GL.glViewport(0, 0, w, h)


shader_vert_glsl = (
    'glsl('
    '#version 150 core'
    'in vec2 pos_attr;'
    'out vec2 uv_var;'
    'void main()'
    '{'
    'uv_var = pos_attr;'
    'gl_Position = vec4(pos_attr * vec2(2.0, -2.0) + vec2(-1.0, 1.0), 0.0, 1.0);'
    '}'
    ')glsl'
)

yuv420p_shader_frag_glsl = (
    'glsl('
    '#version 150 core'
    'uniform sampler2D plane1; // Y'
    'uniform sampler2D plane2; // U'
    'uniform sampler2D plane3; // V'
    'in vec2 uv_var;'
    'out vec4 out_color;'
    'void main()'
    '{'
    'vec3 yuv = vec3('
    '(texture(plane1, uv_var).r - (16.0 / 255.0)) / ((235.0 - 16.0) / 255.0),'
    '(texture(plane2, uv_var).r - (16.0 / 255.0)) / ((240.0 - 16.0) / 255.0) - 0.5,'
    '(texture(plane3, uv_var).r - (16.0 / 255.0)) / ((240.0 - 16.0) / 255.0) - 0.5);'
    'vec3 rgb = mat3('
    '1.0, 1.0, 1.0,'
    '0.0, -0.21482, 2.12798,'
    '1.28033, -0.38059, 0.0) * yuv;'
    'out_color = vec4(rgb, 1.0);'
    '}'
    ')glsl;'
)

nv12_shader_frag_glsl = (
    'glsl('
    '#version 150 core'
    'uniform sampler2D plane1; // Y'
    'uniform sampler2D plane2; // interlaced UV'
    'in vec2 uv_var;'
    'out vec4 out_color;'
    'void main()'
    '{'
    'vec3 yuv = vec3('
    '(texture(plane1, uv_var).r - (16.0 / 255.0)) / ((235.0 - 16.0) / 255.0),'
    '(texture(plane2, uv_var).r - (16.0 / 255.0)) / ((240.0 - 16.0) / 255.0) - 0.5,'
    '(texture(plane2, uv_var).g - (16.0 / 255.0)) / ((240.0 - 16.0) / 255.0) - 0.5'
    ');'
    'vec3 rgb = mat3('
    '1.0, 1.0, 1.0,'
    '0.0, -0.21482, 2.12798,'
    '1.28033, -0.38059, 0.0) * yuv;'
    'out_color = vec4(rgb, 1.0);'
    '}'
    ')glsl'
)

CONFIG_YUV420P = {
    "fragment": yuv420p_shader_frag_glsl,
    "planes": 3,

}
# ConversionConfig conversion_configs[] = {
#     {
#         AV_PIX_FMT_YUV420P,
#         shader_vert_glsl,
#         yuv420p_shader_frag_glsl,
#         3,
#         {
#             { 1, 1, 1, GL_R8, GL_RED },
#             { 2, 2, 1, GL_R8, GL_RED },
#             { 2, 2, 1, GL_R8, GL_RED }
#         }
#     },
#     {
#         AV_PIX_FMT_NV12,
#         shader_vert_glsl,
#         nv12_shader_frag_glsl,
#         2,
#         {
#             { 1, 1, 1, GL_R8, GL_RED },
#             { 2, 2, 2, GL_RG8, GL_RG }
#         }
#     }
# };

# static const float vert_pos[] = {
#     0.0f, 0.0f,
#     0.0f, 1.0f,
#     1.0f, 0.0f,
#     1.0f, 1.0f
# };


class OpenGLWidget(QtOpenGLWidgets.QOpenGLWidget, QtGui.QOpenGLFunctions):

    def surface_format():
        format = QtGui.QSurfaceFormat()
        format.setDepthBufferSize(0)
        format.setStencilBufferSize(0)
        format.setVersion(3, 2)
        format.setProfile(QtGui.QSurfaceFormat.CoreProfile)
        return format

    PIX_FORMATS = {
        "yuv420p": CONFIG_YUV420P,
    }

    def __init__(self, parent=None, pix_fmt="yuv420p"):
        super().__init__(parent)
        self.config = OpenGLWidget.PIX_FORMATS[pix_fmt]
        self.setFormat(OpenGLWidget.surface_format())

    def initializeGL(self):
        f = self.context().extraFunctions()
        shader_vert = f.glCreateShader(QOpenGLShader.Vertex)
        f.glShaderSource(shader_vert, shader_vert_glsl)
        f.glCompileShader(shader_vert)

        shader_frag = f.glCreateShader(QOpenGLShader.Fragment)
        f.glShaderSource(shader_frag, self.config["fragment"])
        f.glCompileShader(shader_frag)

        program = f.glCreateProgram()
        f.glAttachShader(program, shader_vert)
        f.glAttachShader(program, shader_frag)
        f.glBindAttribLocation(program, 0, "pos_attr")
        f.glLinkProgram(program)

#     for(int i=0; i<2; i++)
#     {
#         frames[i].conversion_config = conversion_config
#         f.glGenTextures(conversion_config->planes, frames[i].tex)
#         f.glGenBuffers(conversion_config->planes, frames[i].pbo)
#         uint8_t uv_default[] = {0x7f, 0x7f};
#         for(int j=0; j<conversion_config->planes; j++)
#         {
#             f.glBindTexture(QOpenGLTexture.Target2D, frames[i].tex[j])
#             f.glTexParameterf(QOpenGLTexture.Target2D, QOpenGLTexture.magnificationFilter(QOpenGLTexture.Linear))
#             f.glTexParameterf(QOpenGLTexture.Target2D, QOpenGLTexture.magnificationFilter(QOpenGLTexture.Linear))
#             f.glTexParameterf(QOpenGLTexture.Target2D, QOpenGLTexture.DirectionS, QOpenGLTexture.ClampToEdge)
#             f.glTexParameterf(QOpenGLTexture.Target2D, QOpenGLTexture.DirectionT, QOpenGLTexture.ClampToEdge)
#             f.glTexImage2D(QOpenGLTexture.Target2D, 0, conversion_config->plane_configs[j].internal_format, 1, 1, 0, conversion_config->plane_configs[j].format, GL_UNSIGNED_BYTE, j > 0 ? uv_default : nullptr);
#         }
#         frames[i].width = 0
#         frames[i].height = 0
#     }

#     f.glUseProgram(program)

#     // bind only as many planes as we need
#     const char *plane_names[] = {"plane1", "plane2", "plane3"};
#     for(int i=0; i<sizeof(plane_names)/sizeof(char *); i++)
#     {
#         f.glUniform1i(f.glGetUniformLocation(program, plane_names[i]), i);
#     }

#     f.glGenVertexArrays(1, &vao);
#     f.glBindVertexArray(vao);

#     f.glGenBuffers(1, &vbo);
#     f.glBindBuffer(QOpenGLBuffer(QOpenGLBuffer.IndexBuffer), vbo);
#     f.glBufferData(QOpenGLBuffer(QOpenGLBuffer.IndexBuffer), sizeof(vert_pos), vert_pos, QOpenGLBuffer.StaticDraw);

#     f.glBindBuffer(GL_ARRAY_BUFFER, vbo);
#     f.glVertexAttribPointer(0, 2, QOpenGLTexture.Float32, 0, 0, nullptr);
#     f.glEnableVertexAttribArray(0);

#     f.glCullFace(GL_BACK);
#     f.glEnable(GL_CULL_FACE);
#     f.glClearColor(0.0, 0.0, 0.0, 1.0);

#     frame_uploader_context = new QOpenGLContext(nullptr);
#     frame_uploader_context->setFormat(context()->format());
#     frame_uploader_context->setShareContext(context());
#     if(!frame_uploader_context->create())
#     {
#         CHIAKI_LOGE(session->GetChiakiLog(), "Failed to create upload OpenGL context");
#         return;
#     }

#     frame_uploader_surface = new QOffscreenSurface();
#     frame_uploader_surface->setFormat(context()->format());
#     frame_uploader_surface->create();
#     frame_uploader = new AVOpenGLFrameUploader(session, this, frame_uploader_context, frame_uploader_surface);
#     frame_fg = 0;

#     frame_uploader_thread = new QThread(this);
#     frame_uploader_thread->setObjectName("Frame Uploader");
#     frame_uploader_context->moveToThread(frame_uploader_thread);
#     frame_uploader->moveToThread(frame_uploader_thread);
#     frame_uploader_thread->start();

#     # def update(self):
#     #     self.funcs.GL_PIXEL_UNPACK_BUFFER

#     def resizeGL(self, width, height):
#         print("resize")
#         funcs = QtGui.QOpenGLContext.currentContext().extraFunctions()
#         funcs.glViewport(0, 0, width, height)
