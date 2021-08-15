__license__ = """
NML is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

NML is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with NML; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA."""

from nml import generic

# fmt: off
raw_palette_data = [
    # DOS palette
    [
         0,   0, 255,     16,  16,  16,     32,  32,  32,     48,  48,  48,
        64,  64,  64,     80,  80,  80,    100, 100, 100,    116, 116, 116,
       132, 132, 132,    148, 148, 148,    168, 168, 168,    184, 184, 184,
       200, 200, 200,    216, 216, 216,    232, 232, 232,    252, 252, 252,
        52,  60,  72,     68,  76,  92,     88,  96, 112,    108, 116, 132,
       132, 140, 152,    156, 160, 172,    176, 184, 196,    204, 208, 220,
        48,  44,   4,     64,  60,  12,     80,  76,  20,     96,  92,  28,
       120, 120,  64,    148, 148, 100,    176, 176, 132,    204, 204, 168,
        72,  44,   4,     88,  60,  20,    104,  80,  44,    124, 104,  72,
       152, 132,  92,    184, 160, 120,    212, 188, 148,    244, 220, 176,
        64,   0,   4,     88,   4,  16,    112,  16,  32,    136,  32,  52,
       160,  56,  76,    188,  84, 108,    204, 104, 124,    220, 132, 144,
       236, 156, 164,    252, 188, 192,    252, 208,   0,    252, 232,  60,
       252, 252, 128,     76,  40,   0,     96,  60,   8,    116,  88,  28,
       136, 116,  56,    156, 136,  80,    176, 156, 108,    196, 180, 136,
        68,  24,   0,     96,  44,   4,    128,  68,   8,    156,  96,  16,
       184, 120,  24,    212, 156,  32,    232, 184,  16,    252, 212,   0,
       252, 248, 128,    252, 252, 192,     32,   4,   0,     64,  20,   8,
        84,  28,  16,    108,  44,  28,    128,  56,  40,    148,  72,  56,
       168,  92,  76,    184, 108,  88,    196, 128, 108,    212, 148, 128,
         8,  52,   0,     16,  64,   0,     32,  80,   4,     48,  96,   4,
        64, 112,  12,     84, 132,  20,    104, 148,  28,    128, 168,  44,
        28,  52,  24,     44,  68,  32,     60,  88,  48,     80, 104,  60,
       104, 124,  76,    128, 148,  92,    152, 176, 108,    180, 204, 124,
        16,  52,  24,     32,  72,  44,     56,  96,  72,     76, 116,  88,
        96, 136, 108,    120, 164, 136,    152, 192, 168,    184, 220, 200,
        32,  24,   0,     56,  28,   0,     72,  40,   4,     88,  52,  12,
       104,  64,  24,    124,  84,  44,    140, 108,  64,    160, 128,  88,
        76,  40,  16,     96,  52,  24,    116,  68,  40,    136,  84,  56,
       164,  96,  64,    184, 112,  80,    204, 128,  96,    212, 148, 112,
       224, 168, 128,    236, 188, 148,     80,  28,   4,    100,  40,  20,
       120,  56,  40,    140,  76,  64,    160, 100,  96,    184, 136, 136,
        36,  40,  68,     48,  52,  84,     64,  64, 100,     80,  80, 116,
       100, 100, 136,    132, 132, 164,    172, 172, 192,    212, 212, 224,
        40,  20, 112,     64,  44, 144,     88,  64, 172,    104,  76, 196,
       120,  88, 224,    140, 104, 252,    160, 136, 252,    188, 168, 252,
         0,  24, 108,      0,  36, 132,      0,  52, 160,      0,  72, 184,
         0,  96, 212,     24, 120, 220,     56, 144, 232,     88, 168, 240,
       128, 196, 252,    188, 224, 252,     16,  64,  96,     24,  80, 108,
        40,  96, 120,     52, 112, 132,     80, 140, 160,    116, 172, 192,
       156, 204, 220,    204, 240, 252,    172,  52,  52,    212,  52,  52,
       252,  52,  52,    252, 100,  88,    252, 144, 124,    252, 184, 160,
       252, 216, 200,    252, 244, 236,     72,  20, 112,     92,  44, 140,
       112,  68, 168,    140, 100, 196,    168, 136, 224,    200, 176, 248,
       208, 184, 255,    232, 208, 252,     60,   0,   0,     92,   0,   0,
       128,   0,   0,    160,   0,   0,    196,   0,   0,    224,   0,   0,
       252,   0,   0,    252,  80,   0,    252, 108,   0,    252, 136,   0,
       252, 164,   0,    252, 192,   0,    252, 220,   0,    252, 252,   0,
       204, 136,   8,    228, 144,   4,    252, 156,   0,    252, 176,  48,
       252, 196, 100,    252, 216, 152,      8,  24,  88,     12,  36, 104,
        20,  52, 124,     28,  68, 140,     40,  92, 164,     56, 120, 188,
        72, 152, 216,    100, 172, 224,     92, 156,  52,    108, 176,  64,
       124, 200,  76,    144, 224,  92,    224, 244, 252,    200, 236, 248,
       180, 220, 236,    132, 188, 216,     88, 152, 172,    244,   0, 244,
       245,   0, 245,    246,   0, 246,    247,   0, 247,    248,   0, 248,
       249,   0, 249,    250,   0, 250,    251,   0, 251,    252,   0, 252,
       253,   0, 253,    254,   0, 254,    255,   0, 255,     76,  24,   8,
       108,  44,  24,    144,  72,  52,    176, 108,  84,    210, 146, 126,
       252,  60,   0,    252,  84,   0,    252, 104,   0,    252, 124,   0,
       252, 148,   0,    252, 172,   0,    252, 196,   0,     64,   0,   0,
       255,   0,   0,     48,  48,   0,     64,  64,   0,     80,  80,   0,
       255, 255,   0,     32,  68, 112,     36,  72, 116,     40,  76, 120,
        44,  80, 124,     48,  84, 128,     72, 100, 144,    100, 132, 168,
       216, 244, 252,     96, 128, 164,     68,  96, 140,    255, 255, 255
    ],  # end of DOS palette

    # Windows palette
    [
         0,   0, 255,    238,   0, 238,    239,   0, 239,    240,   0, 240,
       241,   0, 241,    242,   0, 242,    243,   0, 243,    244,   0, 244,
       245,   0, 245,    246,   0, 246,    168, 168, 168,    184, 184, 184,
       200, 200, 200,    216, 216, 216,    232, 232, 232,    252, 252, 252,
        52,  60,  72,     68,  76,  92,     88,  96, 112,    108, 116, 132,
       132, 140, 152,    156, 160, 172,    176, 184, 196,    204, 208, 220,
        48,  44,   4,     64,  60,  12,     80,  76,  20,     96,  92,  28,
       120, 120,  64,    148, 148, 100,    176, 176, 132,    204, 204, 168,
       100, 100, 100,    116, 116, 116,    104,  80,  44,    124, 104,  72,
       152, 132,  92,    184, 160, 120,    212, 188, 148,    244, 220, 176,
       132, 132, 132,     88,   4,  16,    112,  16,  32,    136,  32,  52,
       160,  56,  76,    188,  84, 108,    204, 104, 124,    220, 132, 144,
       236, 156, 164,    252, 188, 192,    252, 208,   0,    252, 232,  60,
       252, 252, 128,     76,  40,   0,     96,  60,   8,    116,  88,  28,
       136, 116,  56,    156, 136,  80,    176, 156, 108,    196, 180, 136,
        68,  24,   0,     96,  44,   4,    128,  68,   8,    156,  96,  16,
       184, 120,  24,    212, 156,  32,    232, 184,  16,    252, 212,   0,
       252, 248, 128,    252, 252, 192,     32,   4,   0,     64,  20,   8,
        84,  28,  16,    108,  44,  28,    128,  56,  40,    148,  72,  56,
       168,  92,  76,    184, 108,  88,    196, 128, 108,    212, 148, 128,
         8,  52,   0,     16,  64,   0,     32,  80,   4,     48,  96,   4,
        64, 112,  12,     84, 132,  20,    104, 148,  28,    128, 168,  44,
        64,  64,  64,     44,  68,  32,     60,  88,  48,     80, 104,  60,
       104, 124,  76,    128, 148,  92,    152, 176, 108,    180, 204, 124,
        16,  52,  24,     32,  72,  44,     56,  96,  72,     76, 116,  88,
        96, 136, 108,    120, 164, 136,    152, 192, 168,    184, 220, 200,
        32,  24,   0,     56,  28,   0,     80,  80,  80,     88,  52,  12,
       104,  64,  24,    124,  84,  44,    140, 108,  64,    160, 128,  88,
        76,  40,  16,     96,  52,  24,    116,  68,  40,    136,  84,  56,
       164,  96,  64,    184, 112,  80,    204, 128,  96,    212, 148, 112,
       224, 168, 128,    236, 188, 148,     80,  28,   4,    100,  40,  20,
       120,  56,  40,    140,  76,  64,    160, 100,  96,    184, 136, 136,
        36,  40,  68,     48,  52,  84,     64,  64, 100,     80,  80, 116,
       100, 100, 136,    132, 132, 164,    172, 172, 192,    212, 212, 224,
        48,  48,  48,     64,  44, 144,     88,  64, 172,    104,  76, 196,
       120,  88, 224,    140, 104, 252,    160, 136, 252,    188, 168, 252,
         0,  24, 108,      0,  36, 132,      0,  52, 160,      0,  72, 184,
         0,  96, 212,     24, 120, 220,     56, 144, 232,     88, 168, 240,
       128, 196, 252,    188, 224, 252,     16,  64,  96,     24,  80, 108,
        40,  96, 120,     52, 112, 132,     80, 140, 160,    116, 172, 192,
       156, 204, 220,    204, 240, 252,    172,  52,  52,    212,  52,  52,
       252,  52,  52,    252, 100,  88,    252, 144, 124,    252, 184, 160,
       252, 216, 200,    252, 244, 236,     72,  20, 112,     92,  44, 140,
       112,  68, 168,    140, 100, 196,    168, 136, 224,    200, 176, 248,
       208, 184, 255,    232, 208, 252,     60,   0,   0,     92,   0,   0,
       128,   0,   0,    160,   0,   0,    196,   0,   0,    224,   0,   0,
       252,   0,   0,    252,  80,   0,    252, 108,   0,    252, 136,   0,
       252, 164,   0,    252, 192,   0,    252, 220,   0,    252, 252,   0,
       204, 136,   8,    228, 144,   4,    252, 156,   0,    252, 176,  48,
       252, 196, 100,    252, 216, 152,      8,  24,  88,     12,  36, 104,
        20,  52, 124,     28,  68, 140,     40,  92, 164,     56, 120, 188,
        72, 152, 216,    100, 172, 224,     92, 156,  52,    108, 176,  64,
       124, 200,  76,    144, 224,  92,    224, 244, 252,    200, 236, 248,
       180, 220, 236,    132, 188, 216,     88, 152, 172,     16,  16,  16,
        32,  32,  32,     32,  68, 112,     36,  72, 116,     40,  76, 120,
        44,  80, 124,     48,  84, 128,     72, 100, 144,    100, 132, 168,
       216, 244, 252,     96, 128, 164,     68,  96, 140,     76,  24,   8,
       108,  44,  24,    144,  72,  52,    176, 108,  84,    210, 146, 126,
       252,  60,   0,    252,  84,   0,    252, 104,   0,    252, 124,   0,
       252, 148,   0,    252, 172,   0,    252, 196,   0,     64,   0,   0,
       255,   0,   0,     48,  48,   0,     64,  64,   0,     80,  80,   0,
       255, 255,   0,    148, 148, 148,    247,   0, 247,    248,   0, 248,
       249,   0, 249,    250,   0, 250,    251,   0, 251,    252,   0, 252,
       253,   0, 253,    254,   0, 254,    255,   0, 255,    255, 255, 255
    ],  # end of Windows palette

    # DOS Toyland palette
    [
          0,   0, 255,     16,  16,  16,     32,  32,  32,     48,  48,  48,
         64,  64,  64,     80,  80,  80,    100, 100, 100,    116, 116, 116,
        132, 132, 132,    148, 148, 148,    168, 168, 168,    184, 184, 184,
        200, 200, 200,    216, 216, 216,    232, 232, 232,    252, 252, 252,
         52,  60,  72,     68,  76,  92,     88,  96, 112,    108, 116, 132,
        132, 140, 152,    156, 160, 172,    176, 184, 196,    204, 208, 220,
         48,  44,   4,     64,  60,  12,     80,  76,  20,     96,  92,  28,
        120, 120,  64,    148, 148, 100,    176, 176, 132,    204, 204, 168,
         72,  44,   4,     88,  60,  20,    104,  80,  44,    124, 104,  72,
        152, 132,  92,    184, 160, 120,    212, 188, 148,    244, 220, 176,
         64,   0,   4,     88,   4,  16,    112,  16,  32,    136,  32,  52,
        160,  56,  76,    188,  84, 108,    204, 104, 124,    220, 132, 144,
        236, 156, 164,    252, 188, 192,    252, 208,   0,    252, 232,  60,
        252, 252, 128,     76,  40,   0,     96,  60,   8,    116,  88,  28,
        136, 116,  56,    156, 136,  80,    176, 156, 108,    196, 180, 136,
         68,  24,   0,     96,  44,   4,    128,  68,   8,    156,  96,  16,
        184, 120,  24,    212, 156,  32,    232, 184,  16,    252, 212,   0,
        252, 248, 128,    252, 252, 192,     32,   4,   0,     64,  20,   8,
         84,  28,  16,    108,  44,  28,    128,  56,  40,    148,  72,  56,
        168,  92,  76,    184, 108,  88,    196, 128, 108,    212, 148, 128,
          8,  52,   0,     16,  64,   0,     32,  80,   4,     48,  96,   4,
         64, 112,  12,     84, 132,  20,    104, 148,  28,    128, 168,  44,
         28,  52,  24,     44,  68,  32,     60,  88,  48,     80, 104,  60,
        104, 124,  76,    128, 148,  92,    152, 176, 108,    180, 204, 124,
         16,  52,  24,     32,  72,  44,     56,  96,  72,     76, 116,  88,
         96, 136, 108,    120, 164, 136,    152, 192, 168,    184, 220, 200,
         32,  24,   0,     56,  28,   0,     72,  40,   4,     88,  52,  12,
        104,  64,  24,    124,  84,  44,    140, 108,  64,    160, 128,  88,
         76,  40,  16,     96,  52,  24,    116,  68,  40,    136,  84,  56,
        164,  96,  64,    184, 112,  80,    204, 128,  96,    212, 148, 112,
        224, 168, 128,    236, 188, 148,     80,  28,   4,    100,  40,  20,
        120,  56,  40,    140,  76,  64,    160, 100,  96,    184, 136, 136,
         36,  40,  68,     48,  52,  84,     64,  64, 100,     80,  80, 116,
        100, 100, 136,    132, 132, 164,    172, 172, 192,    212, 212, 224,
         40,  20, 112,     64,  44, 144,     88,  64, 172,    104,  76, 196,
        120,  88, 224,    140, 104, 252,    160, 136, 252,    188, 168, 252,
          0,  24, 108,      0,  36, 132,      0,  52, 160,      0,  72, 184,
          0,  96, 212,     24, 120, 220,     56, 144, 232,     88, 168, 240,
        128, 196, 252,    188, 224, 252,     16,  64,  96,     24,  80, 108,
         40,  96, 120,     52, 112, 132,     80, 140, 160,    116, 172, 192,
        156, 204, 220,    204, 240, 252,    172,  52,  52,    212,  52,  52,
        252,  52,  52,    252, 100,  88,    252, 144, 124,    252, 184, 160,
        252, 216, 200,    252, 244, 236,     72,  20, 112,     92,  44, 140,
        112,  68, 168,    140, 100, 196,    168, 136, 224,    200, 176, 248,
        208, 184, 255,    232, 208, 252,     60,   0,   0,     92,   0,   0,
        128,   0,   0,    160,   0,   0,    196,   0,   0,    224,   0,   0,
        252,   0,   0,    252,  80,   0,    252, 108,   0,    252, 136,   0,
        252, 164,   0,    252, 192,   0,    252, 220,   0,    252, 252,   0,
        204, 136,   8,    228, 144,   4,    252, 156,   0,    252, 176,  48,
        252, 196, 100,    252, 216, 152,      8,  24,  88,     12,  36, 104,
         20,  52, 124,     28,  68, 140,     40,  92, 164,     56, 120, 188,
         72, 152, 216,    100, 172, 224,     92, 156,  52,    108, 176,  64,
        124, 200,  76,    144, 224,  92,    224, 244, 252,    200, 236, 248,
        180, 220, 236,    132, 188, 216,     88, 152, 172,    244,   0, 244,
        245,   0, 245,    246,   0, 246,    247,   0, 247,    248,   0, 248,
        249,   0, 249,    250,   0, 250,    251,   0, 251,    252,   0, 252,
        253,   0, 253,    254,   0, 254,    255,   0, 255,     76,  24,   8,
        108,  44,  24,    144,  72,  52,    176, 108,  84,    210, 146, 126,
        252,  60,   0,    252,  84,   0,    252, 104,   0,    252, 124,   0,
        252, 148,   0,    252, 172,   0,    252, 196,   0,     64,   0,   0,
        255,   0,   0,     48,  48,   0,     64,  64,   0,     80,  80,   0,
        255, 255,   0,     28, 108, 124,     32, 112, 128,     36, 116, 132,
         40, 120, 136,     44, 124, 140,     92, 164, 184,    116, 180, 196,
        216, 244, 252,    112, 176, 192,     88, 160, 180,    255, 255, 255
    ],  # end of DOS Toyland palette

    # Windows Toyland palette
    [
          0, 255, 255,    238,   0, 238,    239,   0, 239,    240,   0, 240,
        241,   0, 241,    242,   0, 242,    243,   0, 243,    244,   0, 244,
        245,   0, 245,    246,   0, 246,    168, 168, 168,    184, 184, 184,
        200, 200, 200,    216, 216, 216,    232, 232, 232,    252, 252, 252,
         52,  60,  72,     68,  76,  92,     88,  96, 112,    108, 116, 132,
        132, 140, 152,    156, 160, 172,    176, 184, 196,    204, 208, 220,
         48,  44,   4,     64,  60,  12,     80,  76,  20,     96,  92,  28,
        120, 120,  64,    148, 148, 100,    176, 176, 132,    204, 204, 168,
        100, 100, 100,    116, 116, 116,    104,  80,  44,    124, 104,  72,
        152, 132,  92,    184, 160, 120,    212, 188, 148,    244, 220, 176,
        132, 132, 132,     88,   4,  16,    112,  16,  32,    136,  32,  52,
        160,  56,  76,    188,  84, 108,    204, 104, 124,    220, 132, 144,
        236, 156, 164,    252, 188, 192,    252, 208,   0,    252, 232,  60,
        252, 252, 128,     76,  40,   0,     96,  60,   8,    116,  88,  28,
        136, 116,  56,    156, 136,  80,    176, 156, 108,    196, 180, 136,
         68,  24,   0,     96,  44,   4,    128,  68,   8,    156,  96,  16,
        184, 120,  24,    212, 156,  32,    232, 184,  16,    252, 212,   0,
        252, 248, 128,    252, 252, 192,     32,   4,   0,     64,  20,   8,
         84,  28,  16,    108,  44,  28,    128,  56,  40,    148,  72,  56,
        168,  92,  76,    184, 108,  88,    196, 128, 108,    212, 148, 128,
          8,  52,   0,     16,  64,   0,     32,  80,   4,     48,  96,   4,
         64, 112,  12,     84, 132,  20,    104, 148,  28,    128, 168,  44,
         64,  64,  64,     44,  68,  32,     60,  88,  48,     80, 104,  60,
        104, 124,  76,    128, 148,  92,    152, 176, 108,    180, 204, 124,
         16,  52,  24,     32,  72,  44,     56,  96,  72,     76, 116,  88,
         96, 136, 108,    120, 164, 136,    152, 192, 168,    184, 220, 200,
         32,  24,   0,     56,  28,   0,     80,  80,  80,     88,  52,  12,
        104,  64,  24,    124,  84,  44,    140, 108,  64,    160, 128,  88,
         76,  40,  16,     96,  52,  24,    116,  68,  40,    136,  84,  56,
        164,  96,  64,    184, 112,  80,    204, 128,  96,    212, 148, 112,
        224, 168, 128,    236, 188, 148,     80,  28,   4,    100,  40,  20,
        120,  56,  40,    140,  76,  64,    160, 100,  96,    184, 136, 136,
         36,  40,  68,     48,  52,  84,     64,  64, 100,     80,  80, 116,
        100, 100, 136,    132, 132, 164,    172, 172, 192,    212, 212, 224,
         48,  48,  48,     64,  44, 144,     88,  64, 172,    104,  76, 196,
        120,  88, 224,    140, 104, 252,    160, 136, 252,    188, 168, 252,
          0,  24, 108,      0,  36, 132,      0,  52, 160,      0,  72, 184,
          0,  96, 212,     24, 120, 220,     56, 144, 232,     88, 168, 240,
        128, 196, 252,    188, 224, 252,     16,  64,  96,     24,  80, 108,
         40,  96, 120,     52, 112, 132,     80, 140, 160,    116, 172, 192,
        156, 204, 220,    204, 240, 252,    172,  52,  52,    212,  52,  52,
        252,  52,  52,    252, 100,  88,    252, 144, 124,    252, 184, 160,
        252, 216, 200,    252, 244, 236,     72,  20, 112,     92,  44, 140,
        112,  68, 168,    140, 100, 196,    168, 136, 224,    200, 176, 248,
        208, 184, 255,    232, 208, 252,     60,   0,   0,     92,   0,   0,
        128,   0,   0,    160,   0,   0,    196,   0,   0,    224,   0,   0,
        252,   0,   0,    252,  80,   0,    252, 108,   0,    252, 136,   0,
        252, 164,   0,    252, 192,   0,    252, 220,   0,    252, 252,   0,
        204, 136,   8,    228, 144,   4,    252, 156,   0,    252, 176,  48,
        252, 196, 100,    252, 216, 152,      8,  24,  88,     12,  36, 104,
         20,  52, 124,     28,  68, 140,     40,  92, 164,     56, 120, 188,
         72, 152, 216,    100, 172, 224,     92, 156,  52,    108, 176,  64,
        124, 200,  76,    144, 224,  92,    224, 244, 252,    200, 236, 248,
        180, 220, 236,    132, 188, 216,     88, 152, 172,     16,  16,  16,
         32,  32,  32,     28, 108, 124,     32, 112, 128,     36, 116, 132,
         40, 120, 136,     44, 124, 140,     92, 164, 184,    116, 180, 196,
        216, 244, 252,    112, 176, 192,     88, 160, 180,     76,  24,   8,
        108,  44,  24,    144,  72,  52,    176, 108,  84,    210, 146, 126,
        252,  60,   0,    252,  84,   0,    252, 104,   0,    252, 124,   0,
        252, 148,   0,    252, 172,   0,    252, 196,   0,     64,   0,   0,
        255,   0,   0,     48,  48,   0,     64,  64,   0,     80,  80,   0,
        255, 255,   0,    148, 148, 148,    247,   0, 247,    248,   0, 248,
        249,   0, 249,    250,   0, 250,    251,   0, 251,    252,   0, 252,
        253,   0, 253,    254,   0, 254,    255,   0, 255,    255, 255, 255
    ],  # end of Windows Toyland palette
]
# fmt: on

# Convert palettes to strings for fast comparison.
palette_data = [bytes(pal) for pal in raw_palette_data]

palette_name = ["DEFAULT", "LEGACY", "DEFAULT_TOYLAND", "LEGACY_TOYLAND"]


def validate_palette(image, filename):
    palette = image.palette.palette
    if len(palette) != 768:
        raise generic.ImageError("Invalid palette; does not contain 256 entries.", filename)
    for i, pal in enumerate(palette_data):
        if pal != palette:
            continue
        return palette_name[i]
    raise generic.ImageError("Palette is not recognized as a valid palette.", filename)
