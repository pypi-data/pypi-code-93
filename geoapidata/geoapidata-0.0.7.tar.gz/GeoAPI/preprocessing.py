import pandas as pd


tabela = pd.read_csv('GeoAPI/Data/Tabela_abreviações.csv')
list_abv = tabela['Abreviatura'].to_list()
list_exp = tabela['Expressão'].to_list()

def trata_abv(input:list) -> list:
    '''
    Function to pre process slangs and abreviantions in the input adress.

    Parameters:
    -----------
    input:list
          list of adress to pre process.

    Returns:
    --------
    List:
        List of string contaning the processed addresses.
    '''
    out_list = []
    for item in input:
        clean = item.upper().replace('.','').replace(',',', ').split()

        b = []
        for i in clean:
            if i not in list_abv:b.append(i)
            for idx, j in enumerate(list_abv):
                if i == j:
                    b.append(list_exp[idx].upper())
                    break
        
        out_list.append(' '.join(b).capitalize())
    return out_list
