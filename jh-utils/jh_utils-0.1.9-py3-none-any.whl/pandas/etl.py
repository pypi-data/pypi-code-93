import pandas as pd
import ast

def create_dimension(dataframe, column_name):
    """
    [summary]

    Args:
        dataframe (dataframe): [description]
        column_name (string): [description]

    Returns:
        dataframe: [description]
    """ 
    
    dimension = dataframe[column_name]
    dimension = pd.DataFrame(dimension.unique()).reset_index()
    dimension.columns = ['id'+column_name, column_name]
    return dimension

def create_bridge_dimension(dataframe,column_name, index_column):
    temp_df = dataframe[[column_name, index_column]]
    temp_df.iloc[:,0] = temp_df.iloc[:,0].fillna(value='[]').apply(ast.literal_eval)
    
    ## ! clean NA and explode the list
    temp_df = temp_df.explode(column_name)
    temp_df = temp_df[temp_df.iloc[:,0].isna() == False]
    
    ## ! create dimension
    dimension = create_dimension(temp_df,column_name)
    temp_df = temp_df.merge(dimension,on=column_name,how='left').iloc[:,1:]
    return (temp_df, dimension)

def modelate_database(dataframe, columns = [], bridge_columns = [], index_column = None):
    ret = dict()
    
    ## create the dimensions
    if columns != []:
        for i in columns:
            dim_temp = create_dimension(dataframe,i)
            ret[i] = dim_temp
            dataframe = dataframe.merge(dim_temp,on=i,how='left')

    if bridge_columns != []:
        if index_column == None:
            return "ERROR: Bridge tables need index column parameter"
        
        for i in bridge_columns:
            bridge_temp, dim_temp = create_bridge_dimension(dataframe,i, index_column)
            ret[i] = dim_temp
            ret['bridge_'+i] = bridge_temp

    ## add fact to return
    ret['fact'] = dataframe.drop(columns + bridge_columns,axis=1)
    return ret