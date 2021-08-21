
import click
import emoji
from twitteralert.db import db_instance, api_client
import twitteralert as ta

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")

@cli.command('info')
@click.option('--version/--no-version', default=False)
def info(version):
    if version:
        click.echo('twitteralert version: {}'.format(ta.__version__))

@cli.command('friends')
@click.option('-d','--database',
              help='Filename with the sqlite database')
@click.option('-S','--state',
              help='Path to state file')
@click.option('-s','--secrets',
              help='Path to twitter api secrets')
@click.option('-e','--emoji_new',
              help='Emoji to display for new friends',
              default=":busts_in_silhouette:")
@click.option('-E','--emoji_lost',
              help='Emoji to display for lost friends',
              default=":eyes:")
@click.option('-t','--text_new',
              help='Text for new friends',
              default="ha començat a seguir")
@click.option('-T','--text_lost',
              help='Text for lost friends',
              default="ha deixat de seguir")
@click.option('-P','--production/--debug',
              help='Flag to send tweets using secrtets instead of printing them',
              default=False)
def cli_users_alert(database, 
                    state,
                    secrets,
                    emoji_new,
                    emoji_lost,
                    text_new,
                    text_lost,
                    production):
    dbinst = db_instance(database)
    ## if the file exists, won't overwrite it
    dbinst.create_state_file(state)
    users_in_db = [i for i in dbinst.state.keys()]
    for user_name in users_in_db:
        state_q = dbinst.state[user_name]
        last_q = dbinst.extract_last_query(user_name)
        if last_q == state_q:
            click.echo("Queries are not updated for {}".format(user_name))
            continue
        click.echo("Queries updated, retrieving list for {}".format(user_name))
        usrs_state = dbinst.obtain_list_friends(state_q)
        usrs_last = dbinst.obtain_list_friends(last_q)
        ## with the set it do not get the duplicates or order
        if set(usrs_state) != set(usrs_last):
            new_friends = [i for i in usrs_last if i not in usrs_state]
            lost_friends = [i for i in usrs_state if i not in usrs_last]
            #
            new_friends_names = [dbinst.get_user_screenName(i) for i in new_friends]
            lost_friends_names = [dbinst.get_user_screenName(i) for i in lost_friends]
            #
            text_new_friends = "{} @{} {} a @{}"
            text_lost_friends = "{} @{} {} a @{}"
            #
            e_new_inst =  emoji.emojize(emoji_new)
            e_lost_inst = emoji.emojize(emoji_lost)
            tweets_to_send1 = [text_new_friends.format(e_new_inst, user_name, text_new, i) for i in new_friends_names]
            tweets_to_send2 = [text_lost_friends.format(e_lost_inst, user_name, text_lost, i) for i in lost_friends_names]
            #  
            tweets_to_send = tweets_to_send1 + tweets_to_send2
            #
            if production:
                click.echo("PRODUCTION INITIATED")
                api = api_client(secrets)
                api.send_tweets(tweets_to_send)
            else:
                click.echo(tweets_to_send)
        else:
            click.echo("No changes in {}".format(user_name))
        dbinst.update_state(user_name, last_q)
    dbinst.overwrite_state()
