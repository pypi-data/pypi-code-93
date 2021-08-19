import os

def bash(command:str):
    os.system(command)

def create(name,is_folder=False):
    if is_folder==True:
        os.mkdir(name)
        return
    os.mkfifo(name)

def remove(name,is_folder=False):
    if is_folder==True:
        os.rmdir(name)
        return
    os.remove(name)

def ls(path:str='.', contains = [''], not_contains=[''],files=True, directories=True):
    ## just to transform string in list if necessary
    if type(contains)==str:
        contains = [contains]
    if type(contains)==str:
        not_contains = [not_contains]
    
    ## set first list
    if files==True and directories==True:
        final_ls = os.listdir(path)
    elif files==True:
        final_ls = list(filter(os.path.isfile, os.listdir(path)))
    elif directories==True:
        final_ls = list(filter(os.path.isdir, os.listdir(path)))
    else:
        return 'ERROR: DIRECTORIES OF FILES NEED TO BE TRUE'
    
    ## filter list
    for i in contains:
        final_ls = list(filter(lambda k: i in k, final_ls))
    for i in not_contains:
        final_ls = list(filter(lambda k: i in k, final_ls))

    return final_ls

