from board import Board
from move import Move
from attackclass import Attack
from party_class import Party

party = Party()
attack = Attack()
board = Board()
move = Move()

rankstorows = {"a": 11, "b": 10, "c": 9, "d": 8, "e": 7, "f": 6,
               "g": 5, "h": 4, "i": 3, "j": 2, "k": 1, "l": 0}
rowstoranks = {v: k for k, v in rankstorows.items()}
filestocols = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5,
               "7": 6, "8": 7, "9": 8, "10": 9, "11": 10, '12': 11}
colstofiles = {v: k for k, v in filestocols.items()}


def drawnotations():
    for i in range(12):
        for x in range(12):
            print(board.get_lcboard()[i][x], end='  ')
        print()


def drawboard(status):
    for i in range(12):
        for x in range(12):
            print(status[i][x], end='  ')
        print()


def reglement():
    print('Bienvenu dans mon jeu !!\n')

    print('Avant de plonger dans la bataille je vais d\'abord vous expliquez les règles du jeu \n ')

    print('Comme vous pouvez le voir si dessous sur le champ de baitaille il y a deux équipe,')
    print("L\'équipe des chevaliers et des orcs.")
    print("La première équipe ajouer est celle des chvalier.\n")

    print("Un tour est divisé en deux partie. Une partie de déplacement et une autre d'attaque.")
    print("Après avoir terminé ces deux parties c'est alors a l'adversaire de jouer.")
    print(
        "Chaque équipe possède 3 classe de combatant. Du coté des croisés on peut trouver 5 chevaliers, 4 archers et 3 catapultes ")
    print("L'équipe orc quant a elle est composé de 5 orcs, 4 mages et 3 dragon \n")
    print(
        "Les chevaliers et les orcs ne peuvent se déplacer que de deux case dans 4 direction ( haut,bas,droite et gauche")
    print("Ils peuvent attaque sur toutes les cases adjascente celle ou il se trouve \n")

    print("Les mages et les archers ne peuvent se déplacer de deux cases qu'en diagonalement")
    print("Ils peuvent attaque dans les 4 directions avec un portée de 2 a 5 cases \n")
    print(
        "Pour finir, les dragons et les catapultes  ne peuvent se déplacer que d'une cases qui se trouve autour d'eux")
    print("Ils peuvent attaque que vers l'avant sur de cases situé a 6 cases \n")

    print("Une équipe gagne si elle arrive a abbatre toute les pieces de son adversaire")

    drawnotations()

    print("\n---------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------\n")


def lineConsoleGame(status):
    invalidmovemade = True
    reloadmove = False
    invalidattackmade = True
    reloadattack = False

    reglement()
    running = True
    validmoves = move.getallpossiblemoves(status)
    validattacks = attack.getallpossibleattacks(status)
    drawboard(status)

    while running:
        party.knightswin(status)
        party.orcswin(status)
        if party.getorcwinner():
            print('les orcs ont gagné')
            running = False
            break

        if party.getknightwinner():
            print('les chevalier ont gagné')
            running = False
            break

        while invalidmovemade:
            if reloadmove:
                print("\n")
                print("vous venez de réaliser un déplacement incorrect. Veuillez donner des coordonnées correctes.")
                print("\n")

            piece = input("donnez les coordonné de la piece que vous voulez déplacer.")
            destination = input("donnez les coordonné de la piece que vous voulez déplacer.")

            movedone = Move((filestocols[piece[1:]], rankstorows[piece[0]]),
                            (filestocols[destination[1:]], rankstorows[destination[0]]), status)

            if movedone in validmoves:
                move.makemove(movedone, status)
                drawboard(status)
                print("déplacement réussi")
                validmoves = move.getallpossiblemoves(status)
                validattacks = attack.getallpossibleattacks(status)
                invalidmovemade = False
            else:
                reloadmove = True
        print(invalidattackmade, invalidmovemade)
        while invalidattackmade and not invalidmovemade:
            if reloadattack:
                print("\n")
                print("vous venez de réaliser une attaque incorrect. Veuillez donner des coordonnées correctes.")
                print("\n")

            piece = input("donnez les coordonné de la piece avec laquelle vous voulez attaquer.")
            destination = input("donnez les coordonné de la piece que vous voulez attaquer.")

            attackdone = Attack((filestocols[piece[1:]], rankstorows[piece[0]]),
                                (filestocols[destination[1:]], rankstorows[destination[0]]), status)

            if attackdone in validattacks:
                attack.makeattacks(attackdone, status)
                drawboard(status)
                print("attaque réussi")
                invalidmovemade = True
                reloadmove = False
                invalidattackmade = True
                reloadattack = False
            else:
                reloadattack = True
