import sys
import os
import json
import pathlib
import easygui

from pypws.constants import ANALYTICS_REST_API_URI, PWS_CLIENT_ID

def get_datadir() -> pathlib.Path:
    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform == "linux2":
        return home / ".local/share"
    elif sys.platform == "linux":
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"


def getLicenceFolderPath():

    configFile = getConfigFile()
    accessTokenFileName = ''

    if not os.path.isfile(configFile):
        accessTokenFileName = easygui.fileopenbox()
        if not (accessTokenFileName == None):
            config = {'tokenFilePath': accessTokenFileName}
            with open(configFile, 'w') as f:
                json.dump(config, f)
        else:
            print("Unable to obtain the license file.")
            sys.exit()
    else:
        with open(configFile, 'r') as f:
            config = json.load(f)
        accessTokenFileName = config['tokenFilePath']
        if (accessTokenFileName == None):
            print("Unable to obtain the license file.")
            sys.exit()

    return accessTokenFileName


def getAccessToken():

    accessTokenFileName = getLicenceFolderPath()

    try:
        with open(accessTokenFileName, 'r') as file:
            accessToken = file.read().replace('\n', '')
    except OSError as ose:
        print('Could not read access token file (%s): %s' % (accessTokenFileName, ose.strerror))
        sys.exit()

    except:
        print('Could not read access token file (%s): %s' % (accessTokenFileName, sys.exc_info()[0]))
        sys.exit()

    return accessToken

def getConfigFile() -> str:

    os_datadir = get_datadir() / "DNV"
    try:
        os_datadir.mkdir(parents=True)
    except FileExistsError:
        pass

    os_datadir = get_datadir() / "DNV" / "Phast Web Services"

    try:
        os_datadir.mkdir(parents=True)
    except FileExistsError:
        pass
    
    userSettingsFileName = os.path.join(os_datadir, 'UserSettings.json')

    path = pathlib.Path(userSettingsFileName)

    if not path.exists():
        print('User settings file (%s) not found' % path)

        try:
            jObject = {}
            jObject['tokenFilePath'] = '<Enter the fully qualified path to your token file here>'
            jObject['selectedAnalyticsAPIEndpoint'] = 'https://phastwebservices-preview.dnv.com/api/analytics/v1/'
            jObject['selectedClientAliasId'] = 'c02aee6b-4ab8-4fd8-9524-8bcd14617f1e'

            with open(path,'w') as jsonFile:
                json.dump(jObject, jsonFile)

            print('One has been created for you but you will need to update it to specify the location of your access token file')

        except OSError as ose:
            print('Tried to create a user settings file but was not able to: %s' % ose.strerror)

        except:
            print('Tried to create a user settings file but was not able to: %s' % sys.exc_info()[0])

        sys.exit()

    return path

def getApiTarget() -> str:

    configFile = getConfigFile()

    with open(configFile, 'r') as f:
        config = json.load(f)

        try:

            apiTarget = config['selectedAnalyticsAPIEndpoint']

            if (apiTarget == None):
                return ANALYTICS_REST_API_URI

            return apiTarget

        except KeyError:
            pass
        
    return ANALYTICS_REST_API_URI

def getClientAliasId() -> str:

    configFile = getConfigFile()

    with open(configFile, 'r') as f:

        config = json.load(f)

        try:

            clientAliasId = config['selectedClientAliasId']

            if (clientAliasId == None):
                return PWS_CLIENT_ID

            return clientAliasId

        except KeyError:
            pass

    return PWS_CLIENT_ID