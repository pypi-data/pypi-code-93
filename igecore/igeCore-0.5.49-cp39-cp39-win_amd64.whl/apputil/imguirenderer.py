import imgui
import igeCore as core
import igeVmath as vmath
import igeCore.input as input

class ImgiIGERenderer(object):
    def __init__(self):
        if not imgui.get_current_context():
            raise RuntimeError(
                "No valid ImGui context. Use imgui.create_context() first and/or "
                "imgui.set_current_context()."
            )
        self.io = imgui.get_io()
        self._font_texture = None
        self.editableFigure = None
        self.camera = None
        self.showcase = None
        self._create_device_objects()
        self.refresh_font_texture()
        self.touch = input.getTouch()
        self.touch.registerTouchBeganCallback(self.onTouchBegan)
        self.touch.registerTouchMovedCallback(self.onTouchMoved)
        self.touch.registerTouchEndedCallback(self.onTouchEnded)
        self.touch.registerTouchScrolledCallback(self.onTouchScrolled)

    def render(self, draw_data, clearColor = True):

        io = self.io
        display_width, display_height = io.display_size
        fb_width = int(display_width * io.display_fb_scale[0])
        fb_height = int(display_height * io.display_fb_scale[1])
        if fb_width == 0 or fb_height == 0:
            return
        draw_data.scale_clip_rects(*io.display_fb_scale)

        self.editableFigure.clearMesh()

        idx = 0
        for commands in draw_data.commands_lists:
            idx_buffer_offset = 0
            mesh_name = "m"+str(idx)
            self.editableFigure.addMesh(mesh_name, "mate01")

            #Vertex format description
            #(ID, size, normalize, type)
            attr = ((core.ATTRIBUTE_ID_POSITION,2,False,core.GL_FLOAT),
                    (core.ATTRIBUTE_ID_UV0,2,False,core.GL_FLOAT),
                    (core.ATTRIBUTE_ID_COLOR,4,True,core.GL_UNSIGNED_BYTE))
            self.editableFigure.setVertexPtr(mesh_name, commands.vtx_buffer_data, commands.vtx_buffer_size,attr)
            self.editableFigure.setTrianglePtr(mesh_name, commands.idx_buffer_data, commands.idx_buffer_size//3, imgui.INDEX_SIZE)

            drawset=0
            for command in commands.commands:
                self.editableFigure.addDrawSet(mesh_name, idx_buffer_offset//3, command.elem_count//3)
                self.editableFigure.setDrawSetRenderState(mesh_name,drawset, "scissor_test_enable", True)
                x, y, z, w = command.clip_rect
                self.editableFigure.setDrawSetRenderState(mesh_name, drawset, 'scissor', int(x), int(fb_height - w), int(z - x), int(w - y))
                self.editableFigure.setDrawSetRenderState(mesh_name,drawset, "blend_enable", True)
                self.editableFigure.setDrawSetRenderState(mesh_name,drawset, "cull_face_enable", False)
                self.editableFigure.setDrawSetRenderState(mesh_name,drawset, "depth_test_enable", False)

                idx_buffer_offset += command.elem_count * imgui.INDEX_SIZE
                drawset+=1
            idx+=1

        self.camera.shoot(self.showcase, clearColor=clearColor)

    def refresh_font_texture(self):
        w, h, pixels = self.io.fonts.get_tex_data_as_alpha8()
        fonttexture = core.texture("fonttex", w, h, core.GL_RED, False, False, pixels)
        self.editableFigure.setMaterialParamTexture("mate01", "ColorSampler", fonttexture,
                                                    minfilter=core.SAMPLERSTATE_LINEAR, mipfilter=core.SAMPLERSTATE_LINEAR)

    def _create_device_objects(self):
        self.camera = core.camera('2dcamera')
        self.camera.orthographicProjection = True
        self.camera.position = vmath.vec3(0,0,1)
        self.camera.screenScale = (1,-1)
        w,h = core.viewSize();
        self.camera.screenOffset = -w , h

        gen = core.shaderGenerator()
        gen.setColorTexture(True)
        gen.setVertexColor(True)
        gen.discardColorMapRGB()
        self.editableFigure = core.editableFigure('font', True)
        self.editableFigure.addMaterial("mate01", gen)
        self.editableFigure.setMaterialParam("mate01", "DiffuseColor", (1.0, 1.0, 1.0, 1.0))
        self.editableFigure.setMaterialRenderState("mate01", "blend_enable", True)
        self.editableFigure.addJoint('joint')
        self.showcase = core.showcase('imgui')
        self.showcase.add(self.editableFigure)

    def _invalidate_device_objects(self):
        print('_invalidate_device_objects')

    def shutdown(self):
        self._invalidate_device_objects()

    def process_inputs(self):
        self.io.display_size = core.viewSize()
        w,h = core.viewSize()
        self.camera.screenOffset = -w , h

        # touch = core.singleTouch()
        # if touch != None:
            # curX = touch['cur_x'] + w//2
            # curY = -touch['cur_y'] + h//2
            # self.io.mouse_pos = curX, curY
            # self.io.mouse_down[0] = touch['is_holded']|touch['is_moved']

    def onTouchBegan(self, id, x, y, pressure):
        w,h = core.viewSize()
        curX = x + w//2
        curY = -y + h//2
        self.io.mouse_pos = curX, curY
        
        if id == 0:
            self.io.mouse_down[0] = True
        if id == 2:
            self.io.mouse_down[1] = True

    def onTouchMoved(self, id, x, y, pressure):
        w,h = core.viewSize()
        curX = x + w//2
        curY = -y + h//2
        self.io.mouse_pos = curX, curY

    def onTouchScrolled(self, id, x, y, is_inverse):
        if is_inverse:
            y *= -1
        self.io.mouse_wheel = y
    
    def onTouchEnded(self, id, x, y, pressure):
        if id == 0:
            self.io.mouse_down[0] = False
        if id == 2:
            self.io.mouse_down[1] = False