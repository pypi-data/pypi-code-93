# -*- coding: utf-8 -*-
"""Slack command line client class."""

import os


class Client:
    """Slack client class."""

    def __init__(self, slack):
        """Initialize a class instance."""
        self.slack = slack
        self.env = slack.env
        self.notifications = slack.notifications
        self.unix_user = os.environ.get("USER", "nobody")

    def channels_list(self):
        """Display a list of channels (public conversations)."""
        slack_channels = self.slack.get_conversations(exclude_archived=False)
        print(f"Public Slack Channels [{len(slack_channels)}]:")
        for channel in sorted(slack_channels, key=lambda x: x["name"]):
            channel_id = channel["id"]
            name = channel["name"]
            if channel["is_archived"]:
                print(f"  * {name} [{channel_id}] (archived)")
            else:
                print(f"  * {name} [{channel_id}]")

    def groups_list(self):
        """Display a list of groups (private conversations)."""
        slack_channels = self.slack.get_conversations(types="private_channel", exclude_archived=False)
        print(f"Private Slack Channels [{len(slack_channels)}]:")
        for channel in sorted(slack_channels, key=lambda x: x["name"]):
            channel_id = channel["id"]
            name = channel["name"]
            if channel["is_archived"]:
                print(f"  * {name} [{channel_id}] (archived)")
            else:
                print(f"  * {name} [{channel_id}]")

    def post_message(self, channel=None, text=None, **kwargs):
        """Post a message to a Slack channel."""
        if not channel:
            channel = self.notifications
        if not text and not kwargs.get("blocks"):
            print("ERROR: no \"text\" and no \"blocks\" included in Slack message post.")
            return None
        if text and self.env and self.unix_user:
            text = f"{text} `[{self.unix_user}@{self.env}]`"
        try:
            return self.slack.chat_post_message(
                channel=channel,
                text=text,
                **kwargs,
            )
        except Exception as error:
            print(f"ERROR: Failed to post message to Slack channel: {channel} [{error}]")
            return None

    def report(self):
        """Display a report of Slack information."""
        channels = self.slack.get_conversations(types="public_channel", exclude_archived=False)
        print(f"Channels: {len(channels)}")

        groups = self.slack.get_conversations(types="private_channel", exclude_archived=False)
        print(f"Groups: {len(groups)}")

        usergroups = self.slack.get_usergroups()
        print(f"Usergroups: {len(usergroups)}")

        users = self.slack.get_users()
        print(f"Users: {len(users)}")

    def usergroups_list(self):
        """Display a list of usergroups."""
        slack_usergroups = self.slack.get_usergroups()
        print(f"Slack Usergroups [{len(slack_usergroups)}]:")
        for usergroup in sorted(slack_usergroups, key=lambda x: x["name"]):
            usergroup_id = usergroup["id"]
            name = usergroup["name"]
            print(f"  * {name} [{usergroup_id}]")

    def users_audit(self):
        """List slack users."""
        print("Getting Slack Users...")
        classes = self.slack.get_users_by_class()

        if classes["other"]:
            print("\nOther [%s]:" % (len(classes["other"])))
            for user in sorted(classes["other"], key=lambda x: x["profile"]["real_name"]):
                print("   %s: %s <%s>" % (
                    user["id"],
                    user["name"],
                    user["profile"]["real_name"],
                ))

        if classes["ultra_restricted"]:
            print("\nSingle-Channel Guests [%s]:" % (len(classes["ultra_restricted"])))
            for user in sorted(classes["ultra_restricted"], key=lambda x: x["profile"]["email"].lower()):
                print(f'  {user["profile"]["email"].lower()}: @{user["name"]} [{user["id"]}]')

        if classes["restricted"]:
            print("\nMulti-Channel Guests [%s]:" % (len(classes["restricted"])))
            for user in sorted(classes["restricted"], key=lambda x: x["profile"]["email"].lower()):
                print(f'  {user["profile"]["email"].lower()}: @{user["name"]} [{user["id"]}]')

        if classes["bots"]:
            print("\nBots [%s]:" % (len(classes["bots"])))
            for user in sorted(classes["bots"], key=lambda x: x["profile"]["real_name"]):
                print(f'  {user["profile"]["real_name"]}: @{user["name"]} [{user["id"]}]')

    def users_list(self):
        """Display a list of users."""
        slack_users = self.slack.get_users()
        print(f"Slack Users [{len(slack_users)}]:")
        for user in sorted(slack_users, key=lambda x: x["name"]):
            user_id = user["id"]
            name = user["name"]
            print(f"  * {name} [{user_id}]")
