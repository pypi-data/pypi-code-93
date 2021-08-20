"""
indi game engine - input module
"""
import igeCore as core
from .event import EventType
from .keyboard import KeyEventCode, KeyCode, KeyModifier, Keyboard
from .touch import TouchEventCode, Touch

def getKeyboard():
    return Keyboard.instance()

def getTouch():
    return Touch.instance()

eventListenerFuncs = set([])

def onEvent(event):
    for func in eventListenerFuncs:
        func(event)

def registerEventListener(func):
    eventListenerFuncs.add(func)
    if len(eventListenerFuncs) == 1:
        core.registerEventListener(EventType.ALL, -1, onEvent)
