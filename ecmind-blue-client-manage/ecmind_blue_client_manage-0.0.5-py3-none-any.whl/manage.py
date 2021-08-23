import base64
from ecmind_blue_client_manage.system_role import SystemRole
from typing import List
from ecmind_blue_client import Client, Job, Param, ParamTypes
from XmlElement import XmlElement


def get_users(client:Client) -> dict:
    user_list_result = client.execute(Job('mng.GetUserList', Flags=0))

    if not user_list_result.return_code == 0:
        raise RuntimeError(user_list_result.error_message)

    users_element = XmlElement.from_string(user_list_result.values['UserList']).find('Users')
    users_element.find('User').flag_as_list = True
    result = {}
    for user_entry in users_element.to_dict()['User']:
        result[user_entry['@benutzer']] = {
            'id': user_entry['@id'],
            'login': user_entry['@benutzer'],
            'name': user_entry['@name'],
            'guid': user_entry['@osguid'],
            'mail': user_entry['@osemail'],
            'locked': True if user_entry['@locked'] == 1 else False,
            'profile': user_entry['@profil'],
        }
    return result


def get_user_ids(client:Client) -> dict:
    return { u['id']: u for u in get_users(client).values() }


def get_user_guids(client:Client) -> dict:
    return { u['guid']: u for u in get_users(client).values() }


def get_sessions(client: Client) -> list[dict[str, str]]:
    job = Job('krn.SessionEnumDB', Flags=0)
    
    result_get_sessions = client.execute(job)
    if not result_get_sessions.return_code == 0:
        raise RuntimeError(result_get_sessions.error_message)

    sessions = []
    
    for session_data_encoded in result_get_sessions.values['Sessions'].split(';'):
        if len(session_data_encoded) == 0:
            break

        session_data = base64.b64decode(session_data_encoded.encode('utf-8')).decode('utf-8').split('\x00')
        session = { info: session_data[i] for i, info in enumerate(result_get_sessions.values['SessionInfoType'].split(";")) }

        sessions.append(session)

    return sessions


def get_system_roles(client:Client, login:str) -> List[SystemRole]:
    job = Job('mng.GetUserRoles')
    job.append(Param('Flags', ParamTypes.INTEGER, 0))
    job.append(Param('$$$SwitchContextUserName$$$', ParamTypes.STRING, login))
    result_user_roles = client.execute(job)

    if result_user_roles.return_code != 0:
        raise RuntimeError(result_user_roles.error_message)

    return [ 
        SystemRole(int(r))
        for r 
        in str(result_user_roles.values['Result']).strip(';').split(';') 
        if len(r)
    ]

def get_user_groups_by_guid(client:Client, guid:str) -> List[str]:
    job = Job('mng.GetUserGroups', Flags=0, OutputUnicode=1, UserGUID=guid)
    get_user_groups_result = client.execute(job)
    if get_user_groups_result.return_code != 0:
        raise RuntimeError(get_user_groups_result.error_message)

    groups = XmlElement.from_string(get_user_groups_result.values['utfGroupList'])['Groups'][0]
    first_group = groups.find('Group')
    if first_group == None:
        raise RuntimeError('No groups found.')
    first_group.flag_as_list = True

    result = {}
    for group_entry in groups.to_dict(recognize_bool=False)['Group']:
        result[group_entry['@name']] = {
            'id': group_entry['@id'],
            'name': group_entry['@name'],
            'description': group_entry['@description'],
            'guid': group_entry['@osguid'],
            'profil': True if group_entry['@profil'] == 1 else False,
        }
    return result

def get_user_groups_by_login(client:Client, login:str) -> List[str]:
    '''This is a relatively inefficient comfort function using get_users() beforehand get_user_group_by_guid().'''
    users = get_users(client)
    guid = users[login]['guid']
    return get_user_groups_by_guid(client, guid)