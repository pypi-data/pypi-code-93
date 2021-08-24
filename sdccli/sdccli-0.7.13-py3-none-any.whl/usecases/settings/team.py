from sdcclient import SdMonitorClient


def retrieve_team_by_name_or_id(monitor: SdMonitorClient, team):
    try:
        # By ID
        id = int(team)
        ok, res = monitor.get_teams()
        if not ok:
            raise Exception(res)

        for d in res:
            if id == d["id"]:
                return d

        raise Exception(f"no team with id {id} found")
    except ValueError:
        # By Name
        ok, res = monitor.get_team(team)
        if not ok:
            raise Exception(res)

        return res