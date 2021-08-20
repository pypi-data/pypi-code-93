"""
indi game engine - keyboard input
"""
import igeCore as core
from .event import EventType

class KeyEventCode:
    PRESSED = 0
    RELEASED = 1

class KeyCode:
    KEY_NOKEY = -1
    KEY_0 = 0
    KEY_1 = 1
    KEY_2 = 2
    KEY_3 = 3
    KEY_4 = 4
    KEY_5 = 5
    KEY_6 = 6
    KEY_7 = 7
    KEY_8 = 8
    KEY_9 = 9
    KEY_A = 10
    KEY_B = 11
    KEY_C = 12
    KEY_D = 13
    KEY_E = 14
    KEY_F = 15
    KEY_G = 16
    KEY_H = 17
    KEY_I = 18
    KEY_J = 19
    KEY_K = 20
    KEY_L = 21
    KEY_M = 22
    KEY_N = 23
    KEY_O = 24
    KEY_P = 25
    KEY_Q = 26
    KEY_R = 27
    KEY_S = 28
    KEY_T = 29
    KEY_U = 30
    KEY_V = 31
    KEY_W = 32
    KEY_X = 33
    KEY_Y = 34
    KEY_Z = 35
    KEY_UP = 36
    KEY_RIGHT = 37
    KEY_DOWN = 38
    KEY_LEFT= 39
    KEY_F1 = 40
    KEY_F2 = 41
    KEY_F3 = 42
    KEY_F4 = 43
    KEY_F5 = 44
    KEY_F6 = 45
    KEY_F7 = 46
    KEY_F8 = 47
    KEY_F9 = 48
    KEY_F10 = 49
    KEY_F11 = 50
    KEY_F12 = 51
    KEY_ESC = 52
    KEY_TAB = 53
    KEY_BACK = 54
    KEY_RETURN = 55
    KEY_KP0 = 56
    KEY_KP1 = 57
    KEY_KP2 = 58
    KEY_KP3 = 59
    KEY_KP4 = 60
    KEY_KP5 = 61
    KEY_KP6 = 62
    KEY_KP7 = 63
    KEY_KP8 = 64
    KEY_KP9 = 65
    KEY_KPPLUS = 66
    KEY_KPMINUS = 67
    KEY_KPDIV = 68
    KEY_KPMULT = 69
    KEY_KPENTER = 70
    KEY_KPPERIOD = 71
    KEY_PAUSE = 72
    KEY_SPACE = 73
    KEY_PLUS = 74
    KEY_MINUS = 75
    KEY_PERIOD = 76
    KEY_SLASH = 77
    KEY_HASH = 78
    KEY_EQUAL = 79
    KEY_QUOTE = 80
    KEY_BACKQUOTE = 81
    KEY_SEMICOLON = 82
    KEY_LEFTBRACKET = 83
    KEY_RIGHTBRACKET = 84
    KEY_BACKSLASH = 85
    KEY_COMMA = 86
    KEY_INSERT = 87
    KEY_DEL = 88
    KEY_HOME = 89
    KEY_END = 90
    KEY_PAGEUP = 91
    KEY_PAGEDOWN = 92
    KEY_LCTRL = 93
    KEY_RCTRL = 94
    KEY_LALT = 95
    KEY_RALT = 96
    KEY_LWIN = 97
    KEY_RWIN = 98
    KEY_LSHIFT = 99
    KEY_RSHIFT = 100
    KEY_CAPSLOCK = 101
    KEY_NUMLOCK = 102
    KEY_COUNT = 103

class KeyModifier:
    KEY_MOD_NONE = 0
    KEY_MOD_CTRL = 1
    KEY_MOD_ALT = 2
    KEY_MOD_SHIFT = 4

class Keyboard:
    __instance = None

    def __init__(self):
        self.keyPressedCallbacks = set([])
        self.keyReleasedCallbacks = set([])

    def __del__(self):
        self.keyPressedCallbacks.clear()
        self.keyReleasedCallbacks.clear()

    @staticmethod
    def instance():
        if Keyboard.__instance is None:
            Keyboard.__instance = Keyboard()
        return Keyboard.__instance
     
    def getKey(self, keyCode):
        return core.getKeyChar(keyCode)

    def getModifier(self):
        return core.getKeyModifier()

    def isPressed(self, keyCode):
        return core.isKeyPressed(keyCode)

    def isReleased(self, keyCode):
        return core.isKeyReleased(keyCode)
        
    def isHold(self, keyCode):
        return core.isKeyHold(keyCode)

    def registerKeyPressedCallback(self, onKeyPressedFunc):
        self.keyPressedCallbacks.add(onKeyPressedFunc)
        if len(self.keyPressedCallbacks) == 1:
            core.registerEventListener(EventType.KEYBOARD, KeyEventCode.PRESSED, self.onKeyPressed)

    def registerKeyReleasedCallback(self,onKeyReleasedFunc):
        self.keyReleasedCallbacks.add(onKeyReleasedFunc)
        if len(self.keyReleasedCallbacks) == 1:
            core.registerEventListener(EventType.KEYBOARD, KeyEventCode.RELEASED, self.onKeyReleased)
    
    def removeKeyPressedCallback(self, onKeyPressedFunc):
        self.keyPressedCallbacks.remove(onKeyPressedFunc)

    def removeKeyReleasedCallback(self, onKeyReleasedFunc):
        self.keyReleasedCallbacks.remove(onKeyReleasedFunc)

    def onKeyPressed(self, keyCode, eventCode, keyChar, keyModifier):
        for callback in self.keyPressedCallbacks:
            callback(keyCode, eventCode, keyChar, keyModifier)

    def onKeyReleased(self, keyCode, eventCode, keyChar, keyModifier):
        for callback in self.keyReleasedCallbacks:
            callback(keyCode, eventCode, keyChar, keyModifier)
