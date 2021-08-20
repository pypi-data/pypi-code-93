

"""
    Title: version.py
    Author: Akash Dwivedi
    Language: Python
    Date Created: 26-07-2021
    Date Modified: 14-08-2021
    Description:
        ###############################################################
        ## Checks the version of the cli  ## 
         ###############################################################
 """
import click
import json
import os
@click.command()
def version():
    '''
    Find the version of the buildpan
    '''
    """
    Variables Used:
    a : Carries the description of the cli
    y : stores the instance of the json
    version : stores the version of the cli  
    
    return: Nil
   """
    a = '{"version": "0.1", "languages": "Python"}'
    y = json.loads(a)
    version = y["version"]
    # with open(file_path, 'r') as f:
    #      data = json.load(f)
    #      version = data["Version"]
    
    print(f'Current Buildspan version is {version}')