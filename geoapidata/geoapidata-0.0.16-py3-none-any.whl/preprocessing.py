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


def removeCaracters(df: pd.DataFrame, column: str, caracters: list):
    """
    
    Parameters:
    ----------
    df: DataFrame
    
    column: str

    caracters: list[str]

    Return:
    -------

    df: Dataframe
    
    """
    dataframe = df.copy()
    if column in dataframe.columns:
        for c in caracters:
            dataframe[column] = dataframe[column].apply(lambda x: x.replace(c, ""))
        return dataframe
    else:
        raise ValueError("the column entered does not exist in the dataframe")

def splitFullAddress(dataframe: pd.DataFrame, address_column: str = "end_completo") -> pd.DataFrame: 
    """
    This function decomposes a string referring to the complete address into smaller parts.
    
    Parameters:
	----------
	dataframe: DataFrame
		dataframe containing a column with full address information
	
	Return:
	-------
	
	DataFrame
        A new dataframe with new columns referring to the decomposition
        of this address, with street, number, city and state.
    
    """
  
    numbers = []
    cities = []
    states = []
    addresses = []

    

    df = dataframe.copy()
    if address_column not in df.columns:
        raise ValueError("Address column does not exists in dataframe")

    for i in df.iloc():
        addresses.append(i[address_column].split(",")[0])
        numbers.append(i[address_column].split(",")[1].strip())
        cities.append(i[address_column].split(",")[2].split("-")[0].strip())
        states.append(i[address_column].split(",")[2].split("-")[1].strip())

    df['endereco'] = pd.Series(data=addresses, dtype='str')
    df['numero'] = pd.Series(data=numbers, dtype='str')
    df['cidade'] = pd.Series(data=cities, dtype='str')
    df['estado'] = pd.Series(data=states, dtype='str')

    return df


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function receives a dataframe, decomposes the complete address into smaller parts 
    and then this dataframe is submitted to a function that checks points outside the city's geometry.
    
    Parameters:
    ----------
    df: pd.DataFrame
        Dataframe with end_completo column

    Return:
    ------
    df: pd.DataFrame
        dataframe resulting from the transformation

    """

    df = splitFullAddress(df)
    df.cidade = df.cidade.apply(lambda x: x.lower())
    #df = batch_outside_geometry_limits(df)
    return df