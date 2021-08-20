import os

from .vars import SequenceFlags
from .common import (
    M2FileReader, M2Struct, M2ArrayField, M2TrackBaseField, M2TrackField, M2FakeTrack,
    M2Vector, M2CompQuat, M2ByteArray, M2String, M2FixedString,
    M2Byte, M2UInt16, M2Int16, M2UInt32, M2Int32, M2Float, M2Fixed16, M2Bool, M2SplineKey, M2Range, M2Box
)


class M2Sequence(M2Struct):
    # Animation id in AnimationData.dbc
    animation_id = M2UInt16()
    # Sub-animation id: Which number in a row of animations this one is.
    sub_animation_id = M2UInt16()
    # The length of this animation sequence in milliseconds.
    duration = M2UInt32()
    # This is the speed the character moves with in this animation.
    movespeed = M2Float()
    # SequenceFlags
    flags = M2UInt32()
    # This is used to determine how often the animation is played.
    # For all animations of the same type, this adds up to 0x7FFF (32767).
    frequency = M2Int16()
    padding = M2UInt16()
    # Range(min, max). May both be 0 to not repeat.
    # Client will pick a random number of repetitions within bounds if given.
    replay = M2Range()
    # This specifies how long that blending takes. Values: 0, 50, 100, 150, 200, 250, 300, 350, 500
    blend_time = M2UInt32()
    bounding_box = M2Box()
    bounding_radius = M2Float()
    # id of the following animation of this AnimationID, points to an Index or is -1 if none.
    next_animation = M2Int16()
    # id in the list of animations. Used to find actual animation if this sequence is an alias.
    alias_next = M2UInt16()

    def __init__(self, **kwargs):
        super(M2Sequence, self).__init__(**kwargs)
        self.anim_reader = None

    @property
    def is_alias(self):
        return self['flags'] & SequenceFlags.HasNext

    def load(self, reader: M2FileReader):
        super(M2Sequence, self).load(reader)

        # TODO: analize if this is correct
        # if self['flags'] & (SequenceFlags.Looped | SequenceFlags.LowPriority | SequenceFlags.Stored):
        if self['flags'] & (SequenceFlags.Looped | SequenceFlags.HasNext):
            # Sequence is internal or alias (animations will be read from .m2 reader or used already loaded one)
            return

        # Otherwise sequence is external (animations will be read from .anim reader)
        self.anim_reader = M2FileReader('{}{:04d}-{:02d}.anim'.format(
            os.path.splitext(reader.name)[0],
            self['animation_id'], self['sub_animation_id']
        ))
        self.anim_reader.open()


class M2Bone(M2Struct):
    # KeyBone enum. -1 if this is no key bone.
    key_bone_id = M2Int32()
    # BoneFlags enum.
    flags = M2UInt32()
    # Parent bone ID or -1 if there is none.
    parent_bone = M2Int16()
    # Mesh part ID OR uDistToParent? .skin
    submesh_id = M2UInt16()
    # For debugging only
    bone_name_crc = M2UInt32()
    # Track<C3Vector>
    translation = M2TrackField(M2Vector(3))
    # Track<M2CompQuat>. Default is (0,0,0,1) == identity
    rotation = M2TrackField(M2CompQuat())
    # Track<C3Vector>. Default is (1,1,1)
    scale = M2TrackField(M2Vector(3))
    # The pivot point of that bone.
    pivot = M2Vector(3)


class M2Vertex(M2Struct):
    position = M2Vector(3)
    bone_weights = M2ByteArray(4)
    bone_indices = M2ByteArray(4)
    normal = M2Vector(3)
    # Two textures, depending on shader used
    tex_coords_1 = M2Vector(2)
    tex_coords_2 = M2Vector(2)


class M2Color(M2Struct):
    color = M2TrackField(M2Vector(3))
    alpha = M2TrackField(M2Fixed16())


class M2Texture(M2Struct):
    type = M2UInt32()
    flags = M2UInt32()
    filename = M2String()


class M2TextureTransform(M2Struct):
    translation = M2TrackField(M2Vector(3))
    # (x, y, z, w). Rotation center is texture center (0.5, 0.5).
    # Unlike Quaternions elsewhere, the scalar part ('w') is the last element in the struct instead of the first
    rotation = M2TrackField(M2Vector(4))
    scaling = M2TrackField(M2Vector(3))


class M2Material(M2Struct):
    flags = M2UInt16()
    blend_mode = M2UInt16()


class M2Attachment(M2Struct):
    id = M2UInt32()
    # Attachment base
    # TODO: bone = UInt32 or UInt16 + unknown(Uint16)?
    bone = M2UInt16()
    # See BogBeast.m2 in vanilla for a model having values here
    unknown = M2UInt16()
    # Relative to bone; Often this value is the same as bone's pivot point
    position = M2Vector(3)
    # Whether or not the attached model is animated when this model is.
    animate_attachment = M2TrackField(M2Bool(M2Byte()))


class M2Event(M2Struct):
    # Mostly a 3 character name prefixed with '$'.
    identifier = M2FixedString(4)
    # This data is passed when the event is fired.
    data = M2Int32()
    # Somewhere it has to be attached.
    bone = M2UInt16()
    unknown = M2UInt16()
    # Relative to that bone of course, animated. Pivot without animating.
    position = M2Vector(3)
    # This is a timestamp-only animation block. It is built up the same as a normal AnimationBlocks,
    # but is missing values, as every timestamp is an implicit "fire now".
    enabled = M2TrackBaseField()


class M2Light(M2Struct):
    type = M2UInt16()
    bone = M2Int16()
    position = M2Vector(3)
    ambient_color = M2TrackField(M2Vector(3))
    ambient_intensity = M2TrackField(M2Float())
    diffuse_color = M2TrackField(M2Vector(3))
    diffuse_intensity = M2TrackField(M2Float())
    attenuation_start = M2TrackField(M2Float())
    attenuation_end = M2TrackField(M2Float())
    visibility = M2TrackField(M2Byte())


class M2Camera(M2Struct):
    type = M2Int32()
    fov = M2Float()
    far_clip = M2Float()
    near_clip = M2Float()
    positions = M2TrackField(M2SplineKey(M2Vector(3)))
    position_base = M2Vector(3)
    target_position = M2TrackField(M2SplineKey(M2Vector(3)))
    target_position_base = M2Vector(3)
    roll = M2TrackField(M2SplineKey(M2Float()))


class M2Ribbon(M2Struct):
    # Always (as I have seen): -1.
    # TODO: check it
    identifier = M2Int32()
    # A bone to attach to.
    bone = M2UInt32()
    # A position, relative to that bone.
    position = M2Vector(3)
    texture_refs = M2ArrayField(M2UInt16())
    blend_refs = M2ArrayField(M2UInt16())
    # An RGB multiple for the material.
    color = M2TrackField(M2Vector(3))
    # An alpha value in a short, where: 0 - transparent, 0x7FFF - opaque.
    alpha = M2TrackField(M2Fixed16())
    # Above and Below – These fields define the width of a ribbon in units based on their offset from the origin.
    height_above = M2TrackField(M2Float())
    # Do not set to same!
    height_below = M2TrackField(M2Float())
    # This defines how smooth the ribbon is. A low value may produce a lot of edges.
    # Edges/Sec – The number of quads generated.
    edges_per_second = M2Float()
    # Time in seconds that the quads stay around after being generated.
    # Use arcsin(val) to get the emission angle in degree. The length aka Lifespan. In seconds.
    edge_lifetime = M2Float()
    # Can be positive or negative. Will cause the ribbon to sink or rise in the z axis over time.
    gravity = M2Float()
    # Tiles in texture. Texture Rows and Cols – Allows an animating texture similar to BlizParticle.
    # Set the number of rows and columns equal to the texture.
    texture_rows = M2UInt16()
    texture_cols = M2UInt16()
    # Pick the index number of rows and columns, and animate this number to get a cycle.
    tex_slot = M2TrackField(M2UInt16())
    data_enabled = M2TrackField(M2Bool(M2Byte()))
    priority_plane = M2Int16()
    padding = M2UInt16()


class M2Particle(M2Struct):
    """
    See particle.m2 for documentation.
    """
    id = M2Int32()
    flags = M2UInt32()
    position = M2Vector(3)
    bone = M2Int16()
    texture = M2Int16()
    model_filename = M2String()
    particle_filename = M2String()
    blending_type = M2Byte()
    emitter_type = M2Byte()
    particle_color_id = M2UInt16()
    particle_type = M2Byte()
    head_or_tail = M2Byte()
    texture_tile_rotation = M2Int16()
    texture_dimensions_rows = M2UInt16()
    texture_dimensions_columns = M2UInt16()
    emission_speed = M2TrackField(M2Float())
    speed_variation = M2TrackField(M2Float())
    vertical_range = M2TrackField(M2Float())
    horizontal_range = M2TrackField(M2Float())
    gravity = M2TrackField(M2ByteArray(4))
    lifespan = M2TrackField(M2Float())
    lifespan_vary = M2Float()
    emission_rate = M2TrackField(M2Float())
    emission_rate_vary = M2Float()
    emission_area_length = M2TrackField(M2Float())
    emission_area_width = M2TrackField(M2Float())
    z_source = M2TrackField(M2Float())
    color_track = M2FakeTrack(M2Vector(3))
    alpha_track = M2FakeTrack(M2Fixed16())
    scale_track = M2FakeTrack(M2Vector(2))
    scale_vary = M2Vector(2)
    head_cell_track = M2FakeTrack(M2UInt16())
    tail_cell_track = M2FakeTrack(M2UInt16())
    tail_length = M2Float()
    twinkle_speed = M2Float()
    twinkle_percent = M2Float()
    twinkle_scale = M2Vector(2)
    burst_multiplier = M2Float()
    drag = M2Float()
    base_spin = M2Float()
    base_spin_vary = M2Float()
    spin = M2Float()
    spin_vary = M2Float()
    unknown1 = M2Float()
    model1_rotation = M2Vector(3)
    model2_rotation = M2Vector(3)
    model_translation = M2Vector(3)
    unknown2 = M2Vector(4)
    spline_points = M2ArrayField(M2Vector(3))
    enabled_in = M2TrackField(M2Bool(M2UInt16()))
