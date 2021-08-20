import os
def gui():
    path = os.path.dirname(os.path.realpath(__file__))
    os.system('voila "' + os.path.join(path,'asiva.ipynb') +'"')
