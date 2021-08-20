import math
import struct

from .structures import M2Particle


def get_particle_gravity_value(particle: M2Particle):
    gravity = particle.gravity.value
    compressed = particle['flags'] & 0x800000
    if compressed:
        # Interpret the 4 bytes at pValue as CompressedParticleGravity:
        pass
    for i in range(len(gravity['values'])):
        for j in range(len(gravity['values'][i])):
            val = bytes(gravity['values'][i][j])
            if compressed:
                v_x, v_y, v_z = struct.unpack('<2bh', val)
                mag = v_z * 0.04238648

                v_x *= abs(mag) / 128.0
                v_y *= abs(mag) / 128.0
                v_z = math.copysign(1, mag) * math.sqrt(mag ** 2 - v_x ** 2 - v_y ** 2)

                gravity['values'][i][j] = (v_x, v_y, v_z)
            else:
                gravity['values'][i][j] = (0, 0, -struct.unpack('<f', val)[0])

    return gravity
