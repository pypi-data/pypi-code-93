from app import app, dm
from jobs import sleepy


if __name__ == "__main__":
    from bws_daemon import  bws_daemon_cli
    # print("-" , app.name, dm.daemons)
    bws_daemon_cli()
