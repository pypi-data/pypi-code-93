import os
import click
from twitterobserver.apiclient import api_client
import twitterobserver as to

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")

@cli.command('info')
@click.option('--version/--no-version', default=False)
def info(version):
    if version:
        click.echo('twitteralert version: {}'.format(to.__version__))

@cli.command('ff')
@click.option('-u','--user',
              help='user to track')
@click.option('-d','--database',
              help='path to sqlite database')
@click.option('-s','--secrets',
              help='path to twitter api secrets')
def cli_users(user, database, secrets):
    api_inst = api_client(secrets, user, database )
    api_inst.get_followers()
    api_inst.get_friends()
    api_inst.update_db()

@cli.command('friends')
@click.option('-u','--user',
              help='user or list of users to track')
@click.option('-d','--database',
              help='path to sqlite database')
@click.option('-s','--secrets',
              help='path to twitter api secrets')
def cli_users(user, database, secrets):
    users_to_track = []
    if os.path.isfile(user):
        with open(user) as f:
            for line in f:
                users_to_track.append(line.strip())
    else:
        users_to_track.append(user)
    ## now loop over users
    print(users_to_track)
    for userInst in users_to_track:
        ## send a message to the command line indicating which user is 
        ## being tracked
        click.echo(f"Tracking user {userInst}")
        api_inst = api_client(secrets, userInst, database )
        api_inst.get_friends()
        api_inst.update_db()

@cli.command('followers')
@click.option('-u','--user',
              help='user to track')
@click.option('-d','--database',
              help='path to sqlite database')
@click.option('-s','--secrets',
              help='path to twitter api secrets')
def cli_users(user, database, secrets):
    api_inst = api_client(secrets, user, database )
    api_inst.get_followers()
    api_inst.update_db()

