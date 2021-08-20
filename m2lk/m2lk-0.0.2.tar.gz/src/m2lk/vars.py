import enum


class InterpolationType(enum.Enum):
    Instant = 0
    Linear = 1
    Bezier = 2  # TODO: check that Bezier is 2 and Hermite is 3
    Hermite = 3


class SequenceFlags(enum.IntFlag):
    RuntimeBlended = 0x1
    LowPriority = 0x10
    Looped = 0x20
    HasNext = 0x40
    Blended = 0x80
    Stored = 0x100


class KeyBone(enum.Enum):
    Other = -1
    ArmL = 0
    ArmR = 1
    ShoulderL = 2
    ShoulderR = 3
    SpineLow = 4
    Waist = 5
    Head = 6
    Jaw = 7
    IndexFingerR = 8
    MiddleFingerR = 9
    PinkyFingerR = 10
    RingFingerR = 11
    ThumbR = 12
    IndexFingerL = 13
    MiddleFingerL = 14
    PinkyFingerL = 15
    RingFingerL = 16
    ThumbL = 17
    Bth = 18
    Csr = 19
    Csl = 20
    Breath = 21
    Name = 22
    NameMount = 23
    Chd = 24
    Cch = 25
    Root = 26
    Wheel1 = 27
    Wheel2 = 28
    Wheel3 = 29
    Wheel4 = 30
    Wheel5 = 31
    Wheel6 = 32
    Wheel7 = 33
    Wheel8 = 34


class BoneFlags(enum.IntFlag):
    Null = 0
    SphericalBillboard = 0x8
    CylindricalBillboardLockX = 0x10
    CylindricalBillboardLockY = 0x20
    CylindricalBillboardLockZ = 0x40
    Transformed = 0x200
    KinematicBone = 0x400  # MoP+: allow physics to influence this bone
    HelmetAnimScaled = 0x1000  # set blend_modificator to helmetAnimScalingRec.m_amount for this bone
    SmthSequenceID = 0x2000  # <=bfa+, parent_bone+submesh_id are a sequence id instead?!


class TextureType(enum.Enum):
    Null = 0
    Skin = 1
    ObjectSkin = 2
    WeaponBlade = 3
    WeaponHandle = 4
    Environment = 5
    CharacterHair = 6
    CharacterFacialHair = 7
    SkinExtra = 8
    UiSkin = 9
    TaurenMane = 10
    MonsterSkin1 = 11
    MonsterSkin2 = 12
    MonsterSkin3 = 13
    ItemIcon = 14
    GuildBackgroundColor = 15
    GuildEmblemColor = 16
    GuildBorderColor = 17
    GuildEmblem = 18


class RenderFlags:
    Unlit = 0x01
    Unfogged = 0x02
    TwoSided = 0x04
    Billboarded = 0x08
    DisableZBuffer = 0x10
    ShadowBatchRelated1 = 0x40
    ShadowBatchRelated2 = 0x80
    Unknown = 0x400
    DisableAlpha = 0x800


class BlendingMode(enum.Enum):
    Opaque = 0
    Mod = 1
    Decal = 2
    Add = 3
    Mod2X = 4
    Fade = 5
    Unknown6 = 6
    Unknown7 = 7


ATTACHMENT_ID_NAME = {
    "0": "Shield / MountMain / ItemVisual0",
    "1": "HandRight / ItemVisual1",
    "2": "HandLeft / ItemVisual2",
    "3": "ElbowRight / ItemVisual3",
    "4": "ElbowLeft / ItemVisual4",
    "5": "ShoulderRight",
    "6": "ShoulderLeft",
    "7": "KneeRight",
    "8": "KneeLeft",
    "9": "HipRight",
    "10": "HipLeft",
    "11": "Helm",
    "12": "Back",
    "13": "ShoulderFlapRight",
    "14": "ShoulderFlapLeft",
    "15": "ChestBloodFront",
    "16": "ChestBloodBack",
    "17": "Breath",
    "18": "PlayerName",
    "19": "Base",
    "20": "Head",
    "21": "SpellLeftHand",
    "22": "SpellRightHand",
    "23": "Special1",
    "24": "Special2",
    "25": "Special3",
    "26": "SheathMainHand",
    "27": "SheathOffHand",
    "28": "SheathShield",
    "29": "PlayerNameMounted",
    "30": "LargeWeaponLeft",
    "31": "LargeWeaponRight",
    "32": "HipWeaponLeft",
    "33": "HipWeaponRight",
    "34": "Chest",
    "35": "HandArrow",
    "36": "Bullet",
    "37": "SpellHandOmni",
    "38": "SpellHandDirected",
    "39": "VehicleSeat1",
    "40": "VehicleSeat2",
    "41": "VehicleSeat3",
    "42": "VehicleSeat4",
    "43": "VehicleSeat5",
    "44": "VehicleSeat6",
    "45": "VehicleSeat7",
    "46": "VehicleSeat8",
    "47": "LeftFoot",
    "48": "RightFoot",
    "49": "ShieldNoGlove",
    "50": "SpineLow",
    "51": "AlteredShoulderR",
    "52": "AlteredShoulderL",
    "53": "BeltBuckle",
    "54": "SheathCrossbow",
    "55": "HeadTop",
    "57": "Backpack?",
    "60": "Unknown"
}


class LightType(enum.Enum):
    Directional = 0
    Point = 1


class CameraType(enum.IntEnum):
    FlyBy = -1
    Portrait = 0
    CharacterInfo = 1

    @enum.DynamicClassAttribute
    def description(self):
        if self._name_ == 'FlyBy':
            return 'FlyBy camera (movies)'
        elif self._name_ == 'Portrait':
            return 'Portrait camera (character bar)'
        elif self._name_ == 'CharacterInfo':
            return 'Portrait camera (character menu)'
        return ''
