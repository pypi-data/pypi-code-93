import setting

def add_Function(function,saveTpye = 'public',returnInformation = True):
    if saveTpye == 'public':
        try:
            cache = open(setting.PublicInstallationDirectory,'a')
            cache.write(function)
            cache.close()
        except:
            if returnInformation:
                return False
        else:
            if returnInformation:
                return True
    elif saveTpye == 'private':
        try:
            cache = open(setting.PrivateInstallationDirectory,'a')
            cache.write(function)
            cache.close()
        except:
            if returnInformation:
                return False
        else:
            if returnInformation:
                return True
    else:
        return False

def run_function(function,parameter):
    import functions
    try:
        eval('functions.{0}({1})'.format(function,parameter))
    except:
        return False
    else:
        return True