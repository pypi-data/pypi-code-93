from functools import cached_property

from .common import (
    M2FileReader, M2Root, M2Struct, M2ArrayField, M2TrackField,
    M2UInt16, M2Int16, M2UInt32, M2Float, M2Fixed16, M2Bool, M2Vector, M2String, M2Box
)

from .structures import (
    M2Sequence, M2Bone, M2Vertex, M2Color, M2Texture, M2TextureTransform,
    M2Material, M2Attachment, M2Event, M2Light, M2Camera, M2Ribbon, M2Particle
)


class WrongM2Error(ValueError):
    pass


# Validate version
def validate_version(version):
    if version != 264:
        raise WrongM2Error(f'Unexpected version: {version}')
    return version


class M2(M2Struct, M2Root):
    # Only 264 (3.3.5a) is supported
    version = M2UInt32(validator=validate_version)
    # Should be globally unique, used to reload by name in internal clients
    name = M2String()
    # Extract just one flag here
    has_blending_maps = M2Bool(M2UInt32(validator=lambda x: x & 0x008))
    # Global sequences is a list of timestamps (uint32). Timestamps used in global looping animations.
    global_sequences = M2ArrayField(M2UInt32())
    # Information about the animations in the model.
    sequences = M2ArrayField(M2Sequence())
    # Mapping of sequence IDs to the entries in the Animation sequences block.
    sequence_idx_hash_by_id = M2ArrayField(M2Int16())
    # MAX_BONES = 0x100 => Creature/SlimeGiant/GiantSlime.M2 has 312 bones
    bones = M2ArrayField(M2Bone())
    # Lookup table for key skeletal bones
    key_bone_lookup = M2ArrayField(M2Int16())
    vertices = M2ArrayField(M2Vertex())
    # Views (LOD) are in .skins.
    skin_profiles_num = M2UInt32()
    # Color and alpha animations definitions.
    colors = M2ArrayField(M2Color())
    textures = M2ArrayField(M2Texture())
    # Transparency of textures.
    transparencies = M2ArrayField(M2TrackField(M2Fixed16()))
    # This block contains definitions for texture animations,
    # for example, flowing water or lava in some models. The keyframe values are used in the texture transform matrix.
    texture_transforms = M2ArrayField(M2TextureTransform())
    replacable_texture_lookup = M2ArrayField(M2Int16())
    # Blending modes / render flags.
    materials = M2ArrayField(M2Material())
    bone_lookup = M2ArrayField(M2Int16())
    tex_lookup = M2ArrayField(M2Int16())
    tex_unit_lookup = M2ArrayField(M2Int16())
    transparency_lookup = M2ArrayField(M2Int16())
    tex_transforms_lookup = M2ArrayField(M2Int16())
    # min/max( [1].z, 2.0277779f ) - 0.16f seems to be the maximum camera height
    bounding_box = M2Box()
    # Detail doodad draw dist = clamp(bounding_sphere_radius * detailDoodadDensityFade * detailDoodadDist, …)
    bounding_radius = M2Float()
    collision_box = M2Box()
    collision_radius = M2Float()
    collision_triangles = M2ArrayField(M2UInt16())
    collision_vertices = M2ArrayField(M2Vector(3))
    collision_normals = M2ArrayField(M2Vector(3))
    # Position of equipped weapons or effects
    attachments = M2ArrayField(M2Attachment())
    attachment_lookup = M2ArrayField(M2Int16())
    # Used for playing sounds when dying and a lot else.
    events = M2ArrayField(M2Event())
    # Lights are mainly used in loginscreens but in wands and some doodads too.
    lights = M2ArrayField(M2Light())
    # The cameras are present in most models for having a model in the character tab.
    cameras = M2ArrayField(M2Camera())
    camera_lookup = M2ArrayField(M2UInt16())
    # Things swirling around. See the CoT-entrance for light-trails.
    ribbons = M2ArrayField(M2Ribbon())
    particles = M2ArrayField(M2Particle())

    def __init__(self, **kwargs):
        super(M2, self).__init__(**kwargs)
        self._index_map = {}

    @cached_property
    def anim_number(self):
        return len(self.sequences)

    def load(self, reader: M2FileReader):
        signature = reader.read(4)
        if signature != b'MD20':
            raise WrongM2Error(f'Unexpected m2 signature: {signature}')
        try:
            super(M2, self).load(reader)

            if self['has_blending_maps']:
                self.fields['blending_maps'] = M2ArrayField(M2UInt16())
                self.fields['blending_maps'].bind('blending_maps', self)
                self.fields['blending_maps'].load(reader)
        finally:
            # Close .anim files if any
            for seq in self.sequences:
                if seq.anim_reader:
                    seq.anim_reader.close()

    def get_sequence(self, index):
        if index not in self._index_map:
            real_index = index
            while self.sequences[real_index].is_alias:
                real_index = self.sequences[real_index]['alias_next']
            # Cache real index
            self._index_map[index] = real_index
        real_index = self._index_map[index]
        return real_index, self.sequences[real_index]

    def find_sequence_entry(self, animation_id):
        seq_len = len(self['sequence_idx_hash_by_id'])
        i = animation_id % seq_len
        j = 1
        while True:
            seq_hash = self['sequence_idx_hash_by_id'][i]
            if seq_hash == -1:
                return None
            if self.sequences[seq_hash]['animation_id'] == animation_id:
                return seq_hash, self.sequences[seq_hash]
            i = (i + j * j) % seq_len
            j += 1
            if j > 100:
                raise RuntimeError('Too deep!')
