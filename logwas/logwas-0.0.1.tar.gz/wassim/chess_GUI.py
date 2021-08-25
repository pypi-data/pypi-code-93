import pygame as p

from board import Board
from attackclass import Attack
from party_class import Party
from move import Move

moves = Move()
attack = Attack()


class GUI:
    def __init__(self, dimension=12, width=720, height=720):

        self.__dim = dimension
        self.__width = width
        self.__height = height
        self.__dimcar = int(self.__width // self.__dim)
        self.__maxfps = 15

    def chargimg(self):
        images = ["ar", "ca", "dr", "kn", "ma", "or", "og"]
        loadedimg = {}
        for image in images:
            loadedimg[image] = p.transform.scale(p.image.load("images/" + image + ".png"),
                                                 (self.__dimcar, self.__dimcar))
        return loadedimg

    def dessplat(self, screen):
        colors = [p.Color("white"), p.Color("gray")]
        for i in range(self.__dim):
            for x in range(self.__dim):
                color = colors[((i + x) % 2)]
                p.draw.rect(screen, color, p.Rect(i * self.__dimcar, x * self.__dimcar, self.__dimcar, self.__dimcar))

    def desspieces(self, screen, board, img):
        for i in range(self.__dim):
            for x in range(self.__dim):
                piece = board[x][i]
                if piece != "--":
                    screen.blit(img[piece],
                                p.Rect(i * self.__dimcar, x * self.__dimcar, self.__dimcar, self.__dimcar))

    def desstatut(self, interface, screen, stat, img):
        interface.dessplat(screen)
        interface.desspieces(screen, stat, img)

    def lancement(self, status):
        p.init()
        clock = p.time.Clock()
        interface = GUI()
        window = p.display.set_mode((720, 720))
        running = True
        board = Board()
        validmoves = moves.getallpossiblemoves(status)
        validattacks = attack.getallpossibleattacks(status)
        validemovemade = False
        sqselected = ()
        playerclicks = []

        while running:
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False

                party = Party()
                party.knightswin(status)

                party.orcswin(status)
                if not validemovemade:

                    if event.type == p.MOUSEBUTTONDOWN:
                        if event.button == 1:

                            selection = p.mouse.get_pos()
                            row = selection[0] // self.__dimcar
                            col = selection[1] // self.__dimcar
                            if sqselected == (row, col):
                                sqselected = ()
                                playerclicks = []
                            else:
                                sqselected = (row, col)
                                playerclicks.append(sqselected)
                            if len(playerclicks) == 2:
                                move = Move(playerclicks[0], playerclicks[1], status)
                                if move in validmoves:
                                    move.makemove(move, status)
                                    validemovemade = True
                                sqselected = ()
                                playerclicks = []
                elif validemovemade:

                    if event.type == p.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            selection = p.mouse.get_pos()
                            row = selection[0] // self.__dimcar
                            col = selection[1] // self.__dimcar

                            if sqselected == (row, col):
                                sqselected = ()
                                playerclicks = []
                            else:
                                sqselected = (row, col)
                                playerclicks.append(sqselected)
                            if len(playerclicks) == 2:
                                validattacks = attack.getallpossibleattacks(status)
                                attacks = Attack(playerclicks[0], playerclicks[1], status)
                                if attacks in validattacks:
                                    print("attaque réussie !")
                                    attack.makeattacks(attacks, status)
                                    validemovemade = False
                                sqselected = ()
                                playerclicks = []
                            validmoves = moves.getallpossiblemoves(status)
                            validattacks = attack.getallpossibleattacks(status)

                party.knightswin(status)
                party.orcswin(status)

                if party.getorcwinner():
                    print('les orcs ont gagné')
                    if event.type == p.MOUSEBUTTONDOWN:
                        if event.button == 3:
                            status = board.get_filledboard()
                            validmoves = moves.getallpossiblemoves(status)
                            validattacks = attack.getallpossibleattacks(status)

                if party.getknightwinner():
                    print('les chevalier ont gagné')
                    if event.type == p.MOUSEBUTTONDOWN:
                        if event.button == 3:
                            status = board.get_filledboard()
                            validmoves = moves.getallpossiblemoves(status)
                            validattacks = attack.getallpossibleattacks(status)

            interface.desstatut(interface, window, status, interface.chargimg())
            clock.tick(self.__maxfps)
            p.display.flip()
