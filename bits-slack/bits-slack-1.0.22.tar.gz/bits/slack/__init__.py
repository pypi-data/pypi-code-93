# -*- coding: utf-8 -*-
"""Slack class file."""

import re

import slack
from slack.signature import SignatureVerifier

from .bitsdb import Bitsdb
from .client import Client
from .update import Update


class Slack:
    """Slack class."""

    def __init__(
            self,
            token,
            signing_secret=None,
            env="sandbox",
            notifications="#bitsdb-dev"
    ):
        """Initialize an Slack class instance."""
        # connect to slack web client
        self.webclient = slack.WebClient(token=token)

        # signing secret for validating requests
        self.signing_secret = signing_secret

        # set environment and channel for notifications
        self.env = env
        self.notifications = notifications

        # check the token type
        self.token = token
        self.token_type = "unknown"
        if token.startswith("xoxp-"):
            self.token_type = "user"
        elif token.startswith("xoxb-"):
            self.token_type = "bot"

        # create instance of the client class
        self.Bitsdb = Bitsdb
        self.client = Client(self)

    def update(self, args, auth):
        """Return an instance of the update class."""
        return Update(self, args, auth)

    #
    # admin conversations
    #
    def admin_conversations_set_teams(self, channel_id, org_channel=False, target_team_ids=None, team_id=None):
        """Set teams for a channel."""
        params = {
            "channel_id": channel_id,
            "org_channel": org_channel,
            "target_team_ids": target_team_ids,
            "team_id": team_id,
        }
        return self.webclient.admin_conversations_setTeams(**params)

    #
    # admin teams
    #
    def admin_teams_list(self):
        """Set teams for a channel."""
        return self.webclient.admin_teams_list()

    #
    # admin usergroups
    #
    def admin_usergroups_add_channels(self, usergroup_id, channel_ids, team_id):
        """Add a list of channels to a usergroup.."""
        params = {
            "usergroup_id": usergroup_id,
            "channel_ids": ",".join(channel_ids),
            "team_id": team_id,
        }
        return self.webclient.admin_usergroups_addChannels(**params)

    def admin_usergroups_add_teams(self, usergroup_id, team_ids, auto_provision=False):
        """Add a list of teams to a usergroup."""
        params = {
            "usergroup_id": usergroup_id,
            "team_ids": ",".join(team_ids),
            "auto_provision": auto_provision,
        }
        return self.webclient.admin_usergroups_addTeams(**params)

    def admin_usergroups_list_channels(self, usergroup_id, include_num_members=False, team_id=None):
        """Return a list of channels linked to an IDP Group."""
        params = {
            "usergroup_id": usergroup_id,
            "include_num_members": include_num_members,
        }
        if team_id:
            params["team_id"] = team_id
        return self.webclient.admin_usergroups_listChannels(**params).data.get("channels", [])

    def admin_usergroups_remove_channels(self, usergroup_id, channel_ids, team_id):
        """Remove a list of channels from a usergroup.."""
        params = {
            "usergroup_id": usergroup_id,
            "channel_ids": ",".join(channel_ids),
            "team_id": team_id,
        }
        return self.webclient.admin_usergroups_removeChannels(**params)

    #
    # chat
    #
    def chat_post_message(self, channel, text, **kwargs):
        """Post a message to Slack."""
        return self.webclient.chat_postMessage(
            channel=channel,
            text=text,
            **kwargs
        ).data

    def chat_update(self, channel, timestamp, text, **kwargs):
        """Update a previously-posted Slack message."""
        return self.webclient.chat_update(
            channel=channel,
            text=text,
            ts=timestamp,
            **kwargs,
        ).data

    def post_message(self, channel, text, **kwargs):
        """Alias for chat_post_message."""
        return self.chat_post_message(
            channel=channel,
            text=text,
            **kwargs
        )

    #
    # conversations
    #
    def get_channels(self, exclude_archived=True):
        """Return a list of public channels."""
        return self.get_conversations(types="public_channel", exclude_archived=exclude_archived)

    def get_channels_dict(self, exclude_archived=True):
        """Return a dict of public channels."""
        return self.get_conversations_dict(types="public_channel", exclude_archived=exclude_archived)

    def get_conversation(self, channel, include_locale=False, include_num_members=False):
        """Return info about a specific conversation."""
        return self.webclient.conversations_info(
            channel=channel,
            include_locale=include_locale,
            include_num_members=include_num_members,
        ).data

    def get_conversation_members(self, channel):
        """Return members of a specific conversation."""
        response = self.webclient.conversations_members(channel=channel).data
        members = response.get("members", [])
        next_cursor = response.get("response_metadata", {}).get("next_cursor")
        while next_cursor:
            response = self.webclient.conversations_members(
                channel=channel,
                cursor=next_cursor
            ).data
            members.extend(response.get("members", []))
            next_cursor = response.get("response_metadata", {}).get("next_cursor")
        return members

    def get_conversations(self, types="public_channel", exclude_archived=True):
        """Return a list of Slack conversations."""
        conversations = []

        # get first page of results
        response = self.webclient.conversations_list(
            types=types,
            exclude_archived=exclude_archived,
            limit=200,
        )
        conversations.extend(response["channels"])
        cursor = response["response_metadata"]["next_cursor"]

        # get additional pages
        while cursor:
            response = self.webclient.conversations_list(
                types=types,
                exclude_archived=exclude_archived,
                limit=200,
                cursor=cursor,
            )
            conversations.extend(response["channels"])
            cursor = response["response_metadata"]["next_cursor"]

        return conversations

    def get_conversations_dict(self, types="public_channel", exclude_archived=True):
        """Return a dict of Slack conversations by id."""
        conversations = {}
        for conversation in self.get_conversations(types, exclude_archived):
            cid = conversation["id"]
            conversations[cid] = conversation
        return conversations

    def get_groups(self, exclude_archived=True):
        """Return a list of public channels."""
        return self.get_conversations(types="private_channel", exclude_archived=exclude_archived)

    def get_groups_dict(self, exclude_archived=True):
        """Return a doct of public channels."""
        return self.get_conversations_dict(types="private_channel", exclude_archived=exclude_archived)

    def invite_conversation_users(self, channel, users):
        """Invite one or more users to a conversation."""
        return self.webclient.conversations_invite(channel=channel, users=users).data

    def kick_conversation_user(self, channel, user):
        """Kick a user from a conversation."""
        return self.webclient.conversations_kick(channel=channel, user=user).data

    def search_conversations(self, query):
        """Return results of a conversations search query."""
        return self.webclient.conversations_search(query=query).data

    #
    # teams (workspaces)
    #
    def get_team_info(self, team=None):
        """Return the info about the given team (workspace)."""
        return self.webclient.team_info(team=team).data

    def get_team_profile(self, visibility="all"):
        """Return the profile of the current team (workspace)."""
        return self.webclient.team_profile_get(visibility=visibility).data

    #
    # usergroups
    #
    def get_usergroup_users(self, usergroup, include_disabled=False):
        """Return a list of Slack usergroup users."""
        return self.webclient.usergroups_users_list(usergroup=usergroup).get("users", [])

    def get_usergroups(self, include_count=False, include_disabled=False, include_users=False):
        """Return a list of Slack usergroups."""
        return self.webclient.usergroups_list(
            include_count=include_count,
            include_disabled=include_disabled,
            include_users=include_users
        ).get("usergroups", [])

    def get_usergroups_dict(self, include_count=False, include_disabled=False, include_users=False):
        """Return a dict of Slack usergroups by id."""
        usergroups = {}
        for usergroup in self.get_usergroups(
                include_count=include_count,
                include_disabled=include_disabled,
                include_users=include_users
        ):
            uid = usergroup["id"]
            usergroups[uid] = usergroup
        return usergroups

    def update_usergroup_users(self, usergroup, users, include_count=False):
        """Return a list of Slack usergroup users."""
        return self.webclient.usergroups_users_update(
            usergroup=usergroup,
            users=users,
            include_count=False
        ).data

    #
    # users
    #
    def get_user_identity(self):
        """Return info about the logged-in user."""
        return self.webclient.users_identity().data

    def get_user_info(self, user, include_locale=False):
        """Return info about a user."""
        return self.webclient.users_info(user=user, include_locale=include_locale).get("user")

    def get_users(self, include_locale=False):
        """Return a list of Slack users."""
        users = []

        # get first page of results
        response = self.webclient.users_list(include_locale=include_locale)
        users.extend(response["members"])
        cursor = None
        if response["response_metadata"]:
            cursor = response["response_metadata"]["next_cursor"]

        # get additional pages
        while cursor:
            response = self.webclient.users_list(include_locale=include_locale, cursor=cursor)
            users.extend(response["members"])
            cursor = None
            if response["response_metadata"]:
                cursor = response["response_metadata"]["next_cursor"]

        return users

    def get_users_dict(self, key="id", users=None):
        """Return a dict of Slack users by id."""
        if not users:
            users = self.get_users()

        users_dict = {}
        for user in users:
            k = user[key]
            if k:
                users_dict[k] = user
        return users_dict

    def get_users_by_class(self, users=None):
        """Return a dict of users by class."""
        if not users:
            users = self.get_users()

        # initialize classes
        classes = {
            "bots": [],
            "broad": [],
            "deleted": [],
            "restricted": [],
            "ultra_restricted": [],
            "other": [],
        }

        for user in users:

            # skip deleted users
            if user["deleted"]:
                classes["deleted"].append(user)
                continue

            # get user email address
            email = user["profile"].get("email", "")

            # sort bot users
            if not email:
                classes["bots"].append(user)

            # sort single-channel guests
            elif user["is_ultra_restricted"]:
                classes["ultra_restricted"].append(user)

            # sort multi-channel guests
            elif user["is_restricted"]:
                classes["restricted"].append(user)

            # sort broad users
            elif re.search("@broadinstitute.org", email):
                classes["broad"].append(user)

            # sort others
            else:
                classes["other"].append(user)

        return classes

    def get_users_by_email(self, users=None):
        """Return a dict of slack users."""
        if not users:
            users = self.get_users()

        emails = {}
        for user in users:
            email = user["profile"].get("email")
            if email:
                emails[email] = user
        return emails

    def get_user_profile(self, user=None, include_labels=False):
        """Get the profile for a user."""
        return self.webclient.users_profile_get(
            user=user,
            include_labels=include_labels,
        ).data

    def set_user_profile(self, user, profile=None, name=None, value=None):
        """Get the profile for a user."""
        if profile:
            return self.webclient.users_profile_set(
                user=user,
                profile=profile,
            ).data
        if name and value:
            return self.webclient.users_profile_set(
                user=user,
                name=name,
                value=value,
            ).data
        return None

    #
    # signature verification
    #
    def validate_request(self, request, signing_secret):
        """Validate an incoming Flask request from Slack to make sure it is trusted."""
        body = request.get_data().decode("utf-8")
        headers = request.headers
        return SignatureVerifier(signing_secret).is_valid_request(body, headers)
