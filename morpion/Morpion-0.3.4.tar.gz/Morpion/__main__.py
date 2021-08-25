__version__ = '0.3.4'

import random
from termcolor import colored, cprint

import time
from art import *
import os
import json
pathToScript = os.path.dirname(os.path.abspath(__file__))




from Morpion.datas import variables, loading, setGrid, getPlayers, notDone, isWinner
vars = variables()
colors = vars.colors
cases = vars.scheme
title = vars.title



global grid1
global grid2
global grid3
global grid4
global grid5

global joueurs
joueurs = []
'''
bleu     0
vert     1
rouge    2
jaune    3 
cyan     4
gris     5
'''


global Player1
Player1 = colored("X", colors[2])
global Player2
Player2 = colored("O", colors[0])



global coup
coup = 0

global casesDispo
casesDispo = []

            
def getCoup(p, casesDispo) -> int:
    coup = "test"
    while not str(coup) in str(casesDispo):
        coup = input(f'{p}, quelle case veux-tu marquer ?  ')
        if coup == "":
            coup = "lol"
        try:
            coup = int(coup)
        except ValueError:
            print('Choisi une case disponible (numéros visibles)')
            pass
    return coup 
    
    
    
    """
    #print(casesDispo) 
    coup = input(f'{p}, quelle case veux-tu marquer ?  ')
    try:
        coup = int(coup)
        if str(coup) in str(casesDispo):
            return coup
        else:
            print('Choisi une case disponible (numéros visibles)')
            return getCoup(p, casesDispo)
    except ValueError:
        print('Choisi un des nombres disponible (numéros visibles)')
        getCoup(p, casesDispo)"""


def setGame(joueurs, gameManager):

    for p in gameManager['currentPlayers']:
        joueurs.append(p)
    grid = setGrid(1, 0, 0)
    os.system('clear')
    for ligne in grid:
        print(ligne)
    game(joueurs, gameManager)

def game(joueurs, gameManager):
    casesDispo = [1, 2, 3, 4, 5, 6, 7, 8, 9] 
    turn = 1
    p1 = random.choice(joueurs)
    #print(joueurs)
    p2 = random.choice(joueurs)
    while p2== p1:
        p2 = random.choice(joueurs)
    while notDone(turn):
        turn = turn+1
        if turn%2 == 1:
            p = p1
        else:
            p = p2
        
        coup = getCoup(p, casesDispo)
        try:
            casesDispo.remove(coup)
        except ValueError:
            pass
        #print(casesDispo)
        
        if turn%2 == 1:
            newGrid = setGrid(turn, coup, Player1)
        else:
            newGrid = setGrid(turn, coup, Player2)
        os.system('clear')
        for ligne in newGrid:
            print(ligne)



    time.sleep(2)
    os.system('clear')
    tprint('Game over')
    """print(p)
    print(type(p))
    print(p1)
    print(type(p1))
    print(p2)
    print(type(p2))
    print(gameManager)"""

    p1stats = gameManager[str(p1)]
    
    p2stats = gameManager[str(p2)]
    
    if isWinner() == False:
        trun = 9
    else: 
        turn = 11


    if turn == 11:
        p1stats[2] = p1stats[2] + 1
        p2stats[2] = p2stats[2] + 1
        cprint('Match nul, bien joué à tous les deux !', 'yellow')
    elif p == p1:
        p1stats[0] = p1stats[0] + 1
        p2stats[1] = p2stats[1] + 1
        print(colored(f"Félicitation {p}, tu as gagné ! ", 'yellow'))
    elif p == p2:
        p1stats[1] = p1stats[1] + 1
        p2stats[0] = p2stats[0] + 1
        print(colored(f"Félicitation {p}, tu as gagné ! ", 'yellow'))
    
    gameManager[p1] = p1stats
    gameManager[p2] = p2stats

    with open('save.json', 'w', encoding='utf-8') as file:
        json.dump(gameManager, file)

    print(colored(f"\nSTATS :\n", 'red'))   
    print(f"{p1} : {p1stats[0]} victoires, {p1stats[1]} défaites, {p1stats[2]} matchs nuls   ")
    print(f"{p2} : {p2stats[0]} victoires, {p2stats[1]} défaites, {p2stats[2]} matchs nuls   ")
    print("\nVoulez vous rejouer ?")
    print("1) Quitter le jeu")
    print("2) Rejouer")
    print("3) Changer de joueurs")  
    def endGameChoice() -> str:
        choice = input("")
        if choice == "1" or choice == "2" or choice == "3":
            return choice
        else:
            return endGameChoice()
    mode = int(endGameChoice())
    if mode == 1:
        os.system("""
        osascript -e 'tell application "Terminal" to close first window' && exit
        """)
    elif mode == 2:
        setGame([], gameManager)

    elif mode ==3 :
        os.system('clear')
        players = []
        temp = getPlayers()
        for p in temp.keys():
            players.append(p)
        setGame(players, gameManager)




if __name__ == "__main__":
    loading()
    os.system('clear')
    #pathToScript = os.path.dirname(os.path.abspath(__file__))
    #print(pathToScript)
    gameManager = getPlayers(pathToScript)
    setGame(joueurs, gameManager)
    
