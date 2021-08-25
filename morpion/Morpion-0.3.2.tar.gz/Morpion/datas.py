from termcolor import colored
from art import *
import os
import time
import json

class variables():
    def __init__(self):
        self.colors = ['blue', 'green', 'red', 'yellow','cyan', 'grey']
        self.title = ["Morpion", ""]
        self.scheme = ["debug", colored("1", 'green'), colored("2", 'green'), colored("3", 'green'), colored("4", 'green'), colored("5", 'green'), colored("6", 'green'), colored("7", 'green'), colored("8", 'green'), colored("9", 'green')]
        self.cases = self.scheme


def loadFormat(x, base=2) -> int:
    return base * round(x/base)

def loading():
    os.system("clear")
    tprint("morpion")
    fill = colored('■', "blue")
    percent = 0
    

    for progress in range(0, 1020):
        progress = progress/10
        percent = progress
        bar = f"Loading  |---------------------------------------------------| {percent} %" #11
        progress = loadFormat(progress)
        if progress!= 0:
            progress = int(progress/2)
            bar = bar.replace('-', fill, progress)
            print(f"{bar}", end="\r")
        else:
            print(f"{bar}", end='\r')
        time.sleep(0.001)
    percent = 100
    bar = f"Loading  |{fill*50}| 100 %        "
    print(bar)
    time.sleep(2)
    os.system('clear')

global cases
cases = []

def setGrid(turn, case, value) ->list:
    global cases
    vars = variables()
    if turn == 1:
        cases = vars.cases
    else:
        cases[case] = value
    global grid1
    global grid2
    global grid3
    global grid4
    global grid5
    grid1 = f"{cases[1]} | {cases[2]} | {cases[3]}"
    grid2 = "--+---+--"
    grid3 = f"{cases[4]} | {cases[5]} | {cases[6]}       tour {turn}"        
    grid4 = "--+---+--"
    grid5 = f"{cases[7]} | {cases[8]} | {cases[9]}"
    return [grid1, grid2, grid3, grid4, grid5]


def getPlayers() -> dict:
    with open('Morpion/save.json', 'r') as save:
        players = {}
        #récupérer les données des joueurs précédents
        players = json.load(save)
        #j1
        p1 = input('Joueur 1, qui êtes vous ?\n')
        if players.get(p1):
            print(f'Content de de te revoir {p1} ')
        else:
            players[p1] = [0, 0, 0]
            print(f'Bienvenue {p1}')
        #j2
        #os.system('clear')
        def P2(p1) -> str:
            p2 = input('Joueur 2, qui êtes vous ?\n')
            if p2 == p1:
                print('Joueur déja dans la partie, entrez un autre nom.')
                return P2(p1)
            else:
                return p2

        p2 = P2(p1)
        if players.get(p2):
            print(f'Content de de te revoir {p2} ')
        else:
            players[p2] = [0, 0, 0]
            print(f'Bienvenue {p2}')
    players['currentPlayers'] = [p1, p2]
    #print(players)
    time.sleep(1.0)
    return players
        
def notDone(turn) -> bool:
    
    global cases
    if cases[1] == cases[2] == cases[3] == cases[4] == cases[5] == cases[6] == cases[7] == cases[8] == cases[9]:
        return True
    elif turn == 10:
        return False
    elif cases[1] == cases[2] == cases[3]:
        return False
    elif cases[4] == cases[5] == cases[6]:
        return False
    elif cases[7] == cases[8] == cases[9]:
        return False
    elif cases[1] == cases[4] == cases[7]:
        return False
    elif cases[2] == cases[5] == cases[8]:
        return False
    elif cases[3] == cases[6] == cases[9]:
        return False
    elif cases[1] == cases[5] == cases[9]:
        return False
    elif cases[3] == cases[5] == cases[7]:
        return False
    else:
        return True

def isWinner() -> bool:
    if cases[1] == cases[2] == cases[3]:
        return False
    elif cases[4] == cases[5] == cases[6]:
        return False
    elif cases[7] == cases[8] == cases[9]:
        return False
    elif cases[1] == cases[4] == cases[7]:
        return False
    elif cases[2] == cases[5] == cases[8]:
        return False
    elif cases[3] == cases[6] == cases[9]:
        return False
    elif cases[1] == cases[5] == cases[9]:
        return False
    elif cases[3] == cases[5] == cases[7]:
        return False
    else:
        return True

    