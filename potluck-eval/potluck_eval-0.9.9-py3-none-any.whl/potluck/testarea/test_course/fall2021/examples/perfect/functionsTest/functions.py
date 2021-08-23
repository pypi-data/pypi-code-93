"""
functions.py

Your name: Peter Mawhorter
Your username: pmwh
Submission date: 2021-6-22

A few functions to practice with.
"""

import optimism as opt


def indentMessage(message, targetLength):
    """
    Returns a string that's at least the given target length. If given a
    longer string, it returns it as-is, but if given a shorter string, it
    adds spaces to the front of the string to make it the required
    length.
    """
    indent = max(0, targetLength - len(message))
    return ' ' * indent + message


opt.testCase(indentMessage('hi', 4))
opt.expectResult('  hi')
opt.testCase(indentMessage('hello', 4))
opt.expectResult('hello')


def printMessage(message, width):
    """
    Prints a message, taking up at least the required width (will be
    wider if the message itself is wider). Uses indentMessage.
    """
    print(indentMessage(message, width))


opt.captureOutput()
opt.testCase(printMessage('hi', 4))
opt.expectOutputContains('  hi')
opt.testCase(printMessage('hello', 4))
opt.expectOutputContains('hello')


import math # noqa


def ellipseArea(radius1, radius2):
    """
    Computes the area of an ellipse with the given radii (you may specify
    the major and minor radii in either order). Returns the result as a
    floating-point number.
    """
    return radius1 * radius2 * math.pi


opt.testCase(ellipseArea(1, 1))
opt.expectResult(math.pi)
opt.testCase(ellipseArea(2, 3))
opt.expectResult(6 * math.pi)


from turtle import * # noqa


def polygon(sideLength, nSides):
    """
    Draws a polygon with the given side length and number of sides.
    """
    for _ in range(nSides):
        fd(sideLength) # noqa
        lt(360 / nSides) # noqa
