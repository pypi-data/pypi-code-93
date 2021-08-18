# -*- coding: utf-8 -*-
"""BITSdb Class for Slack."""


class Bitsdb:
    """GitHub subclass for BITSdb API."""

    def __init__(self):
        """Initialize a class instance."""

    def user(self, u):
        """Return a slack#usergroups#sync for BITSdb API."""
        bitsdb = {
            "kind": "slack#usergroups#sync",
            "id": u.get("id"),
            "user_id": u.get("id"),
            "name": u.get("name"),
            "real_name": u.get("real_name"),
            "team_id": u.get("team_id"),
            "color": u.get("color"),
            "deleted": u.get("deleted"),
            "has_2fa": u.get("has_2fa"),
            "is_app_user": u.get("is_app_user"),
            "is_bot": u.get("is_bot"),
            "is_owner": u.get("is_owner"),
            "is_primary_owner": u.get("is_primary_owner"),
            "is_restricted": u.get("is_restricted"),
            "is_ultra_restricted": u.get("is_ultra_restricted"),
            "tz": u.get("tz"),
            "tz_label": u.get("tz_label"),
            "tz_offset": str(u.get("tz_offset")),
        }
        return bitsdb

    def usergroup(self, u):
        """Return a slack#usergroups#sync for BITSdb API."""
        bitsdb = {
            "kind": "slack#usergroups#sync",
            "id": u["id"],
            "usergroup_id": u["id"],
            "name": u["name"],
            "handle": u["handle"],
            "description": u["description"],
            "user_count": str(u["user_count"]),
        }
        return bitsdb

    def usergroups_sync(self, u):
        """Return a slack#usergroups#sync for BITSdb API."""
        bitsdb = {
            "kind": "slack#usergroups#sync",
            "id": u["slack_usergroup"],
            "google_group_email": u["google_group"],
            "google_group_name": u.get("google_group_name", "NONAME"),
            "slack_usergroup_id": u["slack_usergroup"],
            "slack_usergroup_name": u["slack_usergroup_name"],
        }
        return bitsdb

    def prep(self, collection, data):
        """Return data prepared for BITSdb API."""
        bitsdb = {}
        for oid in sorted(data):
            s = data[oid]
            k = str(oid)
            if collection == "users":
                bitsdb[k] = self.user(s)
            elif collection == "usergroups":
                bitsdb[k] = self.usergroup(s)
            elif collection == "usergroups_syncs":
                bitsdb[k] = self.usergroups_sync(s)
            else:
                print(f"ERROR: Unknown collection \"{collection}\"" % (collection))
        return bitsdb
