"""
indi game engine - touch input
"""
import igeCore as core
from .event import EventType

class TouchEventCode:
    BEGAN = 0
    MOVED = 1
    ENDED = 2
    SCROLLED = 3

class Touch:
    __instance = None

    def __init__(self):
        self.touchBeganCallbacks = set([])
        self.touchMovedCallbacks = set([])
        self.touchEndedCallbacks = set([])
        self.touchScrolledCallbacks = set([])

    def __del__(self):
        self.touchBeganCallbacks.clear()
        self.touchMovedCallbacks.clear()
        self.touchEndedCallbacks.clear()
        self.touchScrolledCallbacks.clear()

    @staticmethod
    def instance():
        if Touch.__instance is None:
            Touch.__instance = Touch()
        return Touch.__instance

    def getFingerPosition(self, fingerId):
        return core.getFingerPosition(fingerId)

    def isFingerPressed(self, fingerId):
        return core.isFingerPressed(fingerId)

    def isFingerMoved(self, fingerId):
        return core.isFingerMoved(fingerId)

    def isFingerReleased(self, fingerId):
        return core.isFingerReleased(fingerId)

    def isFingerScrolled(self, fingerId):
        return core.isFingerScrolled(fingerId)

    def getFingerScrolledData(self, fingerId):
        return core.getFingerScrolledData(fingerId)

    def getFingerPressure(self, fingerId):
        return core.getFingerPressure(fingerId)

    def getFingersCount(self):
        return core.getFingersCount()

    def getAllFingers(self):
        return core.getAllFingers()

    def registerTouchBeganCallback(self, onTouchBeganFunc):
        self.touchBeganCallbacks.add(onTouchBeganFunc)
        if len(self.touchBeganCallbacks) == 1:
            core.registerEventListener(EventType.TOUCH, TouchEventCode.BEGAN, self.onTouchBegan)

    def registerTouchMovedCallback(self, onTouchMovedFunc):
        self.touchMovedCallbacks.add(onTouchMovedFunc)
        if len(self.touchMovedCallbacks) == 1:
            core.registerEventListener(EventType.TOUCH, TouchEventCode.MOVED, self.onTouchMoved)

    def registerTouchEndedCallback(self, onTouchEndedFunc):
        self.touchEndedCallbacks.add(onTouchEndedFunc)
        if len(self.touchEndedCallbacks) == 1:
            core.registerEventListener(EventType.TOUCH, TouchEventCode.ENDED, self.onTouchEnded)

    def registerTouchScrolledCallback(self, onTouchScrolledFunc):
        self.touchScrolledCallbacks.add(onTouchScrolledFunc)
        if len(self.touchScrolledCallbacks) == 1:
            core.registerEventListener(EventType.TOUCH, TouchEventCode.SCROLLED, self.onTouchScrolled)

    def removeTouchBeganCallback(self, onTouchBeganFunc):
        self.touchBeganCallbacks.remove(onTouchBeganFunc)

    def removeTouchMovedCallback(self, onTouchMovedFunc):
        self.touchMovedCallbacks.remove(onTouchMovedFunc)

    def removeTouchEndedCallback(self, onTouchEndedFunc):
        self.touchEndedCallbacks.remove(onTouchEndedFunc)

    def removeTouchScrolledCallback(self, onTouchScrolledFunc):
        self.touchScrolledCallbacks.remove(onTouchScrolledFunc)

    def onTouchBegan(self, id, x, y, pressure):
        for callback in self.touchBeganCallbacks:
            callback(id, x, y, pressure)

    def onTouchMoved(self, id, x, y, pressure):
        for callback in self.touchMovedCallbacks:
            callback(id, x, y, pressure)

    def onTouchEnded(self, id, x, y, pressure):
        for callback in self.touchEndedCallbacks:
            callback(id, x, y, pressure)

    def onTouchScrolled(self, id, scroll_x, scroll_y, is_inverse):
        for callback in self.touchScrolledCallbacks:
            callback(id, scroll_x, scroll_y, is_inverse)
