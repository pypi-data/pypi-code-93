import pandas as pd
from pkg_resources import resource_filename


tabela = pd.read_csv(resource_filename('GeoAPI','Data/Tabela_abreviações.csv'))
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
        clean = item.upper().replace('. ',' ').replace('.',' ').replace(',',', ').split()

        b = []
        for i in clean:
            if i not in list_abv:b.append(i)
            for idx, j in enumerate(list_abv):
                if i == j:
                    b.append(list_exp[idx].upper())
                    break
        
        out_list.append(' '.join(b).capitalize())
    return out_list



def concat_OA_addresses(OA_data: pd.DataFrame) -> pd.DataFrame:
    """
    
    This function will concatenate the parts of an address and make it a complete address.
    Parameters:
    ----------
    
    OA_data: dataframe with open addresses data

    Return:
    -------
    
    OA_data: Dataframe with a new column containing the full address


    
    """
    end_completo = []
    for row in OA_data.itertuples():
        number = row.number
        if number == "SN":
            number = ""
        end_completo.append("{} {} {} {}".format(row.street, number,
            row.city, row.region))

    OA_data = OA_data.assign(end_completo = end_completo)

    return OA_data


def removePunctuantion(df: pd.DataFrame, column: str, caracters: list):
    if column in df.columns:
        for c in caracters:
            print(c)
            df[column] = df[column].apply(lambda x: x.replace(c, ""))
        return df
