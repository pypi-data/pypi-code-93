import os

# Clear terminal
def clear_term():
    if(os.name == "nt"): # Check if the user is using windows
        os.system("cls")
    else:
        os.system("claer")