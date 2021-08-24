import click
import json
import sys
from sdccli.printer import print_list, print_item

_list_printable_column_name = ["ID", "status", "image", "network", "processes", "filesystem", "syscalls"]

column_name_to_json_map = {
    "ID"            : "profileId",
    "status"        : "status",
    "image"         : "imageName",
    "network"       : "networkProposal",
    "processes"     : "processesProposal",
    "filesystem"    : "fileSystemProposal",
    "syscalls"      : "syscallProposal"
}

supported_rule_types = ["NETWORK", "SYSCALL", "FILESYSTEM", "PROCESS"]


@click.group(name='profile', short_help='Sysdig Secure image profile operations')
def profile():
    pass


@profile.command(name='list', short_help="List all profiles")
@click.pass_obj
def list_profiles(cnf):
    ok, res = cnf.sdsecure.list_image_profiles()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    # Filter out some fields that will not be printed
    filtered_profiles = []
    for profile in res['profiles']:
        filtered_profiles.append(__map_profile_to_printable_format(profile))

    if ok:
        print_list(filtered_profiles, _list_printable_column_name)
    else:
        print("Error: " + str(res))
        sys.exit(1)


def __map_profile_to_printable_format(raw_profile, fullID=False):
    '''
    **Description**
        Return printable data structure of profile list

    **Arguments**
        - raw_profile: dictionary representing the "profile" field in the json
        - fullID: print or not the first 12 characters of the profile ID

    **Success Return Value**
        Return a dictionary with renamed keys (and lesser number of fields)
    '''

    filt_profile = {}

    for column in _list_printable_column_name:
        if column in ["ID"]:
            if fullID:
                filt_profile[column] = raw_profile[column_name_to_json_map[column]]
            else:
                filt_profile[column] = raw_profile[column_name_to_json_map[column]][0:12]
        elif column in ["status", "image"]:
            filt_profile[column] = raw_profile[column_name_to_json_map[column]]
        else:
            filt_profile[column] = raw_profile[column_name_to_json_map[column]]["score"]

    return filt_profile


@profile.command(name='get', short_help="Get profile by ID")
@click.argument('id', nargs=1)
@click.argument('rule_type', nargs=1)
@click.pass_obj
def get(cnf, id, rule_type):
    """
    PROFILE: PROFILE_ID RULE_TYPE

    Supported RULE_TYPE=[NETWORK | SYSCALL | FILESYSTEM | PROCESS]
    """

    if rule_type not in supported_rule_types:
        print("Error: No such rule type: {}\nRule type list: NETWORK, SYSCALL, FILESYSTEM, PROCESS".format(rule_type))
        sys.exit(1)

    ok, res = cnf.sdsecure.get_image_profile(id)
    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if not ok:
        if isinstance(res, list):
            # Collision detected
            print("Collision detected: " + str(len(res)))
            __print_collision_table(res)
        else:
            # Generic error. For example: ID not found.
            print("Error: " + str(res))

        sys.exit(1)

    rule_found = False

    # If the res is None, it means that there are no information
    # associated to that profile. Print a general message and return.
    if res is None:
        print("Profiles are still in learning state.")
        return

    # Given the provided rule type, return the relevant information
    # to the user. At this moment, there is no possibility to retrieve all
    # the information at once. This is done to be consistent with the usability
    # of the cli.
    # Moreover, please note that the printed subfields depend on the rule type
    for rule in res['proposedRules']:
        ruleDict = {}

        if rule['details']['ruleType'] != rule_type:
            continue

        if rule['details']['ruleType'] == 'NETWORK':
            ruleDict['name'] = rule['name'].split('-')[0].strip()
            ruleDict["size"] = len(rule['details']['tcpListenPorts']['items']) + len(rule['details']['udpListenPorts']['items'])
            ruleDict["tcpListenPorts"] = rule['details']['tcpListenPorts']['items']
            ruleDict["udpListenPorts"] = rule['details']['udpListenPorts']['items']

            print("\n{}".format(ruleDict['name']))
            print_item(ruleDict, ['size', 'tcpListenPorts', 'udpListenPorts'])

            rule_found = True

        elif rule['details']['ruleType'] == 'FILESYSTEM':
            ruleDict['name'] = rule['name'].split('-')[0].strip()
            ruleDict["size"] = len(rule['details']['readWritePaths']['items']) + len(rule['details']['readPaths']['items'])
            ruleDict["readWritePaths"] = rule['details']['readWritePaths']['items']
            ruleDict["readPaths"] = rule['details']['readPaths']['items']

            print("\n{}".format(ruleDict['name']))
            print_item(ruleDict, ['size', 'readWritePaths', 'readPaths'])

            rule_found = True

        elif rule['details']['ruleType'] == 'PROCESS':
            ruleDict['name'] = rule['name'].split('-')[0].strip()
            ruleDict["size"] = len(rule['details']['processes']['items'])
            ruleDict["processes"] = rule['details']['processes']['items']

            print("\n{}".format(ruleDict['name']))
            print_item(ruleDict, ['size', 'processes'])

            rule_found = True

        elif rule['details']['ruleType'] == 'SYSCALL':
            ruleDict['name'] = rule['name'].split('-')[0].strip()
            ruleDict['size'] = len(rule['details']['syscalls']['items'])
            ruleDict['syscalls'] = rule['details']['syscalls']['items']

            print("\n{}".format(ruleDict['name']))
            print_item(ruleDict, ['size', 'syscalls'])

            rule_found = True

    # If the rule_type is not found, print the available  rule types
    if not rule_found:
        print("No data for rule {}".format(
            rule_type
        ))


def __print_collision_table(collisions):
    '''
    **Description**
        Helper function to print the collision table. The user is able to see which are the profiles
        with the common ID prefix (remember that the user can retrieve a profile by the prefix substring of the
        profile ID).

    **Arguments**
        - List of dictionaries, where each dictionary represents the "profiles" field in the retrieved json

    **Success Return Value**
        None. Print the collision table
    '''

    columns = ["imageName", "profileId"]

    table = [{columns[0]: profile[columns[0]], columns[1]: profile[columns[1]]} for profile in collisions]

    print_list(table, columns)
