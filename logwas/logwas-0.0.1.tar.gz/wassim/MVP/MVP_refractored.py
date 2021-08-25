class GameState:

    def __init__(self):

        self.__board = [
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

        self.humansTurn = True

        self.humansPieces = 12
        self.orcsPieces = 12

        self.drakesNotation = 'dr'
        self.nbrDrakes = 2

        self.magesNotation = 'ma'
        self.nbrMages = 6

        self.orcsNotation = 'or'
        self.nbrOrcs = 4

        self.cataNotation = 'ca'
        self.nbrCata = 2

        self.achersNotation = 'ar'
        self.nbrArchers = 6

        self.knightsNotation = 'kn'
        self.nbrKnights = 4

    @property
    def board(self):
        return self.__board

    def draw_board(self):
        for i in range(12):
            for x in range(12):
                print(GameState.board[i][x], end='  ')
            print()


gs = GameState()


def main():
    q = ''

    print('règlement')

    print('l\'équipe des humains commence à déposer ses pièces')

    while gs.humansPieces != 0:
        for i in range(gs.nbrKnights):
            placement = input(
                'ou voulez vous placer vos placer vos chevaliers ? ( {} restant(s))\n'.format(gs.nbrKnights))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.knightsNotation
            gs.nbrKnights -= 1
            gs.humansPieces -= 1
            gs.draw_board()

        for i in range(gs.nbrArchers):
            placement = input('ou voulez vous placer vos placer vos archers ? ( {} restant(s))\n'.format(gs.nbrArchers))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.achersNotation
            gs.nbrArchers -= 1
            gs.humansPieces -= 1
            gs.draw_board()

        for i in range(gs.nbrCata):
            placement = input('ou voulez vous placer vos placer vos catapultes ? ( {} restant(s))\n'.format(gs.nbrCata))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.cataNotation
            gs.nbrCata -= 1
            gs.humansPieces -= 1
            gs.draw_board()

    print('c\'est maintenant à l\'équipe des orcs de déposer ses pièces sur le champ de bataille')

    while gs.orcsPieces != 0:
        for i in range(gs.nbrOrcs):
            placement = input('ou voulez vous placer vos placer vos orcs ? ( {} restant(s))\n'.format(gs.nbrOrcs))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.orcsNotation
            gs.nbrOrcs -= 1
            gs.orcsPieces -= 1
            gs.draw_board()

        for i in range(gs.nbrMages):
            placement = input('ou voulez vous placer vos placer vos mages ? ( {} restant(s))\n'.format(gs.nbrMages))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.magesNotation
            gs.nbrMages -= 1
            gs.orcsPieces -= 1
            gs.draw_board()

        for i in range(gs.nbrDrakes):
            placement = input('ou voulez vous placer vos placer vos dragons ? ( {} restant(s))\n'.format(gs.nbrDrakes))
            gs.board[gs.hor.index(placement[0])][gs.ver.index(placement[1:])] = gs.drakesNotation
            gs.nbrDrakes -= 1
            gs.orcsPieces -= 1
            gs.draw_board()

    print('maintenant que toute les pièces que chaqu\'une des équipes sont placées le combat peut enfin commencé')

    while q != 'quit':

        if gs.humansTurn:
            print('c\'est au tour des humain de jouer !\n')
            gs.humansTurn = False
        else:
            print('c\'est au tour des orcs de jouer !\n')
            gs.humansTurn = True

        print("" if gs.humansTurn else "t")

        gs.humansTurn = not gs.humansTurn

        gs.draw_board()

        pos = input('inserez les coordonnées d\'une case contenant l\'une de vos pièces \n')

        while pos != 'ff' and gs.board[gs.hor.index(pos[0])][gs.ver.index(pos[1:])] == '--':
            pos = input('inserez les coordonnées correctes d\'une case contenant l\'une de vos pièce \n')

        if pos == 'ff':
            if gs.humansTurn:
                print('les humains ont gagné car les orcs ont déclaré forfait')

            else:
                print('les orcs ont gagné car les humains ont déclaré forfait')
            break

        else:
            deplacement = input('ou voullez vous déplacer la pièce choisis ?\n')

            gs.board[gs.hor.index(deplacement[0])][gs.ver.index(deplacement[1:])] = \
                gs.board[gs.hor.index(pos[0])][
                    gs.ver.index(pos[1:])]

            gs.board[gs.hor.index(pos[0])][gs.ver.index(pos[1:])] = '--'

        for x in range(len(gs.board)):
            if len(set(gs.board[x])) > 1:
                break
            else:
                q = 'quit'

    print('partie terminé')


if __name__ == "__main__":
    main()
