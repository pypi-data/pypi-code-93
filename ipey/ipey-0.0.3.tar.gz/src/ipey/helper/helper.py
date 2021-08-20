import re

def convertColor(color):
    '''
    Converts a hex color to the 'standard' that is used by IPE. 


    '''

    if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
        c = color.lstrip('#')
        
        if len(c) == 3:
            c = ''.join([char*2 for char in c])

        c = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

        return True, f"{(c[0] / 255):.2f} {(c[1] / 255):.2f} {(c[2] / 255):.2f}"

    return False, color