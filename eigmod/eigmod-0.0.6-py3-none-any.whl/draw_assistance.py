import sys
import os
import pygame
from pygame import gfxdraw
import math
import numpy as np
if __name__ == "__main__":
    from numpy_assistance import angle_between
else:
    from .numpy_assistance import angle_between


def opacity_line(dimentions, color, op):
    """returns line surface with opacity 

    Args:
        dimentions (tuple): (width , height)
        color (tuble): (c1, c2, c3)
        op (float): number from 0 to 1 (percent of opacity)

    Returns:
        [surface]: surface to blit line
    """
    width, height = dimentions
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill((color[0], color[1], color[2], int(op * 255)))

    return s


def opacity_rect(dimentions, color, op, lines_to_draw=(True, True, True, True), index=0, breite=-1):
    """retruns multible surfaces with relativ drawing cords which together are the rectangle

    Args:
        dimentions (tuple): (width , height)
        color (tuble): (c1, c2, c3)
        op (float): number from 0 to 1 (percent of opacity)
        lines_to_draw (tuple with ints in): left, right, top, bottem
        index (int) : if every round is more relocated
        breite (int, optional): width of single line. Defaults to -1.

    Returns:
        [(rel_x,rel_y), surface]: list of relative_draw_cords, surface
    """
    width, height = dimentions

    if breite == -1:
        gesamt_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        gesamt_surface.fill((color[0], color[1], color[2], int(op * 255)))
    else:
        gesamt_surface = []
        vertical = opacity_line((breite, height), color, op)
        horizontal = opacity_line((width - 2 * breite, breite), color, op)
        if lines_to_draw[0]:
            gesamt_surface.append(((0 + index, 0), vertical))
        if lines_to_draw[1]:
            gesamt_surface.append(((width - breite - index, 0), vertical))
        if lines_to_draw[2]:
            gesamt_surface.append(((breite, 0 + index), horizontal))
        if lines_to_draw[3]:
            gesamt_surface.append(
                ((breite, height - breite - index), horizontal,))

    return gesamt_surface


def draw_aacircle(win, color, cords, radius, filled=True):
    x, y = cords
    x, y, radius = int(x), int(y), int(radius)
    gfxdraw.aacircle(win, x, y, radius, color)
    if filled:
        gfxdraw.filled_circle(win, x, y, radius, color)


def draw_aatriangle(win, color, cords1, cords2, cords3, filled=True):
    x1, y1 = cords1
    x2, y2 = cords2
    x3, y3 = cords3
    x1, y1, x2, y2, x3, y3 = int(x1), int(
        y1), int(x2), int(y2), int(x3), int(y3)

    pygame.gfxdraw.filled_trigon(win, x1, y1, x2, y2, x3, y3, color)
    if filled:
        pygame.gfxdraw.aatrigon(win, x1, y1, x2, y2, x3, y3, color)


def draw_aapolygon(win, color, points):

    pygame.draw.polygon(win, color, points)
    pygame.gfxdraw.aapolygon(win, points, color)


def draw_special_polygon(win, color, points, dicke=0, mitte_zeichen=False, antialiasing=False):

    def get_angle(mitte, point, standart_vektor, smallest_possible=True):
        """returns angle between given matrix point and mitte for reference with standart_vektor

        Args:
            mitte (matirx): mitte
            point (matirx): point
            standart_vektor (matrix): vector which is base for angle comparison
            smallest_possible (bool, optional): when false the max angle is 2 * pi and otherwise if its false the smaller angle
            will always be picked

        Retruns: float: angle between two vectors
        """

        standart_vektor = np.array(standart_vektor)
        mitte = np.array(mitte)
        point = np.array(point)

        # vektor vom mitte punkt zum angegebenen (jetzt zwei vergleichbare verktoren verhanden)
        point_vek = point - mitte

        angle = angle_between(standart_vektor, point_vek)

        # check side of the standart_vector from mitte line the point lies, if on the other one math.pi (180 degree) ist added
        # punkt a und b definieren die linie

        if not smallest_possible:
            pa = mitte  # punkt a
            pb = mitte + standart_vektor  # punkt b
            x = ((pb[0] - pa[0]) * (point[1] - pa[1]) -
                 (pb[1] - pa[1]) * (point[0] - pa[0]))
            if x > 1:
                angle = (math.pi * 2) - angle

        return angle

    # all vectors behind each other
    gesamt_vektor = [sum([pair[0] for pair in points]),
                     sum([pair[1] for pair in points])]
    point_anzahl = len(points)

    # mid between all points
    mitte = [x / point_anzahl for x in gesamt_vektor]

    # vector of refrence
    standart_vektor = [0, -1]

    points_with_angles = []

    # each point with its angle to refrence vector (standart_vector)
    for point in points:
        angle = get_angle(mitte, point, standart_vektor,
                          smallest_possible=False)
        points_with_angles.append([angle, point])

    # sort points by angle and only add points in this order to new draw_points list
    points_with_angles.sort(key=lambda x: x[0])
    draw_points = [x[1] for x in points_with_angles]

    if antialiasing:
        draw_aapolygon(win, color, draw_points)
    else:
        pygame.draw.polygon(win, color, draw_points, dicke)

    ############################## for debugging ############################################################################

    # if mitte_zeichen:
    #     pygame.draw.circle(win, (40, 255, 40), mitte, 3)

    # # drawing draing numers
    # for index, point in enumerate(draw_points):
    #     x = font.render(str(index), False, (255, 255, 255))
    #     win.blit(x, point)

    

    #########################################################################################################################


if __name__ == "__main__":

    points = [(91, 25), (109, 116), (69, 21), (131, 120), (177, 57), (23, 84)]

    pygame.init()
    pygame.font.init()

    font = pygame.font.SysFont("comicsans", 30)

    SCRWIDTH = 600
    SCRHEIGHT = 600

    HW = SCRWIDTH // 2
    HH = SCRHEIGHT // 2

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (100, 100, 100)
    RED = (255, 30, 30)
    GREEN = (30, 255, 30)
    BLUE = (30, 30, 255)

    FPS = 60

    pygame.init()
    WIN = pygame.display.set_mode((SCRWIDTH, SCRHEIGHT))
    pygame.display.set_caption("Space Game")
    FONT = pygame.font.SysFont("comicsans", 30)
    directory_of_file = os.path.normpath(sys.argv[0] + os.sep + os.pardir)

    CLOCK = pygame.time.Clock()

    def draw():
        WIN.fill((0, 0, 0))
        draw_special_polygon(WIN, RED, points, mitte_zeichen=True)

    def main():
        run = True

        while run:
            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()

            draw()

            pygame.display.update()

    main()
    pygame.quit()

    # pygame.gfxdraw.aafilled_circle(WIN, 100, 100, 50, (255,0,0))

    # x = opacity_rect((100,100), (255,255,0), 0.5, 5)
    # print(x)
