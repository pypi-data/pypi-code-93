import tetry
import time

old = None

user = input('pick a user to look at: ')

while True:
    played = tetry.getUser(user).gamesplayed
    if not old:
        old = played
    if played > old:
        print(f'{user} finished a game (found on {time.ctime()})')
    old = max(played, old)
    time.sleep(10)