from .common import (
    M2FileReader, M2Struct, M2ArrayField, M2Byte, M2ByteArray, M2UInt16, M2Int16, M2UInt32, M2Vector, M2Float
)


class WrongSkinError(ValueError):
    pass


class M2SkinSection(M2Struct):
    # Mesh part ID, see below.
    skin_section_id = M2UInt16()
    level = M2UInt16()
    # Starting vertex number. first vertex as index into skin's index list.
    vertex_start = M2UInt16()
    # Number of vertices. number of indices into the skin's index list.
    vertex_count = M2UInt16()
    # Starting triangle index (that's 3* the number of triangles drawn so far).
    # First triangle as index into skin's triangle list, which if you want the real triangle index, divide by 3.
    triangle_index_start = M2UInt16()
    # Number of triangle indices.
    # Length of triangle list for this subset, which if you want the real triangle count, divide by 3.
    triangle_index_count = M2UInt16()
    # Number of elements in the bone lookup table. Max seems to be 256. Shall be ≠ 0.
    # Number of bones to upload to GPU shader constant registers.
    bone_count = M2UInt16()
    # Starting index in the bone lookup table.
    bone_combo_index = M2UInt16()
    # <= 4, Highest number of bones referenced by a vertex of this submesh
    bone_influences = M2UInt16()
    center_bone_index = M2UInt16()
    # Average position of all the vertices in the sub mesh.
    center_position = M2Vector(3)
    # The center of the box when an axis aligned box is built around the vertices in the submesh.
    sort_center_position = M2Vector(3)
    # Distance of the vertex farthest from CenterBoundingBox.
    sort_radius = M2Float()

    @property
    def value(self):
        value = super(M2SkinSection, self).value
        if value['level'] is not None:
            value['triangle_index_start'] = (value['level'] << 16) + value['triangle_index_start']
            value['level'] = None
        return value


class M2Batch(M2Struct):
    # Usually 16 for static textures, and 0 for animated textures.
    # &0x1: materials invert something; &0x2: transform &0x4: projected texture;
    # &0x10: something batch compatible; &0x20: projected texture?;
    # &0x40: possibly don't multiply transparency by texture weight transparency to get final transparency value(?)
    flags = M2Byte()
    priority_plane = M2Byte()
    shader_id = M2UInt16()
    # A duplicate entry of a submesh from the list above.
    skin_section_index = M2UInt16()
    # See below. New name: flags2. 0x2 - projected.
    # 0x8 - EDGF chunk in m2 is mandatory and data from is applied to this mesh
    geoset_index = M2UInt16()
    # A Color out of the Colors-Block or -1 if none.
    color_index = M2Int16()
    # The renderflags used on this texture-unit.
    material_index = M2UInt16()
    # Capped at 7 (see CM2Scene::BeginDraw)
    material_layer = M2UInt16()
    # 1 to 4. See below. Also seems to be the number of textures to load, starting at the texture lookup in the next field (0x10).
    texture_count = M2UInt16()
    # Index into Texture lookup table
    texture_combo_index = M2UInt16()
    # Index into the texture unit lookup table.
    texture_coord_combo_index = M2Int16()
    # Index into transparency lookup table.
    texture_weight_combo_index = M2UInt16()
    # Index into uvanimation lookup table.
    texture_transform_combo_index = M2UInt16()


class M2Skin(M2Struct):
    vertices = M2ArrayField(M2UInt16())
    indices = M2ArrayField(M2UInt16())
    bones = M2ArrayField(M2ByteArray(4))
    submeshes = M2ArrayField(M2SkinSection())
    batches = M2ArrayField(M2Batch())
    bone_count_max = M2UInt32()

    def load(self, reader: M2FileReader):
        signature = reader.read(4)
        if signature != b'SKIN':
            raise WrongSkinError(f'Unexpected skin signature: {signature}')
        super(M2Skin, self).load(reader)
