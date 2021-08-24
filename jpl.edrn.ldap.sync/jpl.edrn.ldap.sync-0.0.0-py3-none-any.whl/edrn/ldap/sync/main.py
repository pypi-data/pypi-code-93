# encoding: utf-8

import click, sys, ldap, getpass


# Defaults
# --------

GROUP_DN   = 'cn=All EDRN,dc=edrn,dc=jpl,dc=nasa,dc=gov'
MANAGER_DN = 'uid=admin,ou=system'
SCOPE      = 'one'
URL        = 'ldaps://edrn-ds.jpl.nasa.gov'
USER_BASE  = 'dc=edrn,dc=jpl,dc=nasa,dc=gov'
USER_CLASS = 'edrnPerson'


# Map from command-line to ldap constants
# ---------------------------------------

_scopes = {
    'base': ldap.SCOPE_BASE,
    'one': ldap.SCOPE_ONELEVEL,
    'sub': ldap.SCOPE_SUBTREE
}


# Let's do it
# -----------

@click.command()
@click.option('--url', default=URL, help='URL to the LDAP server')
@click.option('--manager', default=MANAGER_DN, help='DN of the LDAP admin account')
@click.option('--password', help='Password of the LDAP admin account; if not given you will be prompted')
@click.option('--userbase', default=USER_BASE, help='Base DN where users are found')
@click.option('--scope', default=SCOPE, help='Search scope to find users', type=click.Choice(['base', 'one', 'sub']))
@click.option('--userclass', default=USER_CLASS, help='Object class to determine users')
@click.option('--group', default=GROUP_DN, help='DN of group to update')
def main(url: str, manager: str, password: str, userbase: str, scope: str, userclass: str , group: str):
    if not password:
        password = getpass.getpass()
    connection = ldap.initialize(url)
    connection.simple_bind_s(manager, password)
    allUsers = connection.search_s(userbase, _scopes[scope], '(objectClass={})'.format(userclass), [], attrsonly=1)
    allUsers = set([i[0] for i in allUsers])
    currentMembers = connection.search_s(group, ldap.SCOPE_BASE, '(objectClass=*)', ['uniquemember'])
    currentMembers = set([str(i, 'utf-8') for i in currentMembers[0][1]['uniquemember']])
    usersToAdd = allUsers - currentMembers
    membersToRemove = currentMembers - allUsers
    if usersToAdd:
        connection.modify_s(group, [(ldap.MOD_ADD, 'uniquemember', [i.encode('utf-8') for i in usersToAdd])])
    if membersToRemove:
        connection.modify_s(group, [(ldap.MOD_DELETE, 'uniquemember', [i.encode('utf-8') for i in membersToRemove])])
    sys.exit(0)
