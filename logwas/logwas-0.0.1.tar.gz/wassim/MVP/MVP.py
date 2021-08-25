class GameState:

    def __init__(self):

        self.board = [
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"]]

        self.hor = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
        self.ver = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'f']

        self.tour_des_humains = True

        self.pieceshumain = 12
        self.piecesorcs = 12

        self.drakesnotation = 'dr'
        self.nbrdrakes = 2

        self.magesnotation = 'ma'
        self.nbrmages = 6

        self.orcsnotation = 'or'
        self.nbrorcs = 4

        self.catanotation = 'ca'
        self.nbrcata = 2

        self.achersnotation = 'ar'
        self.nbrarchers = 6

        self.knightsnotation = 'kn'
        self.nbrknights = 4

    def board(self):
        return self.board

    def drawboard(self):
        for i in range(12):
            for x in range(12):
                print(GameState.board(self)[i][x], end='  ')
            print()


def main():
    gs = GameState()
    q = ''

    print('règlement')

    print('l\'équipe des humains commence à déposer ses pièces')

    while gs.pieceshumain != 0:
        while gs.nbrknights != 0:
            placement = input(
                'ou voulez vous placer vos placer vos chevaliers ? ( {} restant(s))'.format(gs.nbrknights))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.knightsnotation
            gs.nbrknights -= 1
            gs.pieceshumain -= 1
            gs.drawboard()

        while gs.nbrarchers != 0:
            placement = input('ou voulez vous placer vos placer vos archers ? ( {} restant(s))'.format(gs.nbrarchers))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.achersnotation
            gs.nbrarchers -= 1
            gs.pieceshumain -= 1
            gs.drawboard()

        while gs.nbrcata != 0:
            placement = input('ou voulez vous placer vos placer vos catapultes ? ( {} restant(s))'.format(gs.nbrcata))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.catanotation
            gs.nbrcata -= 1
            gs.pieceshumain -= 1
            gs.drawboard()

    print('c\'est maintenant à l\'équipe des orcs de déposer ses pièces sur le champ de bataille')

    while gs.piecesorcs != 0:
        while gs.nbrorcs != 0:
            placement = input('ou voulez vous placer vos placer vos orcs ? ( {} restant(s))'.format(gs.nbrorcs))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.orcsnotation
            gs.nbrorcs -= 1
            gs.piecesorcs -= 1
            gs.drawboard()

        while gs.nbrmages != 0:
            placement = input('ou voulez vous placer vos placer vos mages ? ( {} restant(s))'.format(gs.nbrmages))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.magesnotation
            gs.nbrmages -= 1
            gs.piecesorcs -= 1
            gs.drawboard()

        while gs.nbrdrakes != 0:
            placement = input('ou voulez vous placer vos placer vos dragons ? ( {} restant(s))'.format(gs.nbrdrakes))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.drakesnotation
            gs.nbrdrakes -= 1
            gs.piecesorcs -= 1
            gs.drawboard()

    print('maintenant que toute les pièces que chaqu\'une des équipes sont placées le combat peut enfin commencé')

    while q != 'quit':

        if gs.tour_des_humains:
            print('c\'est au tour des humain de jouer !')
            gs.tour_des_humains = False
        else:
            print('c\'est au tour des orcs de jouer !')
            gs.tour_des_humains = True

        gs.drawboard()

        pos = input('inserez les coordonnées d\'une case contenant l\'une de vos pièces')

        while pos != 'ff' and gs.board[gs.hor.index(pos[0])][gs.ver.index(pos[1:])] == '--':
            position = input('inserez les coordonnées correctes d\'une case contenant l\'une de vos pièce')

        if pos == 'ff':
            if gs.tour_des_humains:
                print('les humains ont gagné car les orcs ont déclaré forfait')
                break
            else:
                print('les orcs ont gagné car les humains ont déclaré forfait')
                break
        else:
            deplacement = input('ou voullez vous déplacer la pièce choisis ?')

            gs.board[gs.hor.index(deplacement[0])][gs.ver.index(deplacement[1:])] = gs.board[gs.hor.index(pos[0])][
                gs.ver.index(pos[1:])]

            gs.board[gs.hor.index(pos[0])][gs.ver.index(pos[1:])] = '--'

        for x in range(len(gs.board)):
            if len(set(gs.board[x])) > 1:
                break
            else:
                q = 'quit'

    print('partie terminé')


def affichage_legende():
    print()


if __name__ == "__main__":
    affichage_legende()

    main()
