# -*- coding: utf-8 -*-
"""Slack SCIM client."""

import requests

from slack_scim import Group, SCIMClient


class SCIM:
    """SCIM Class."""

    def __init__(self, token):
        """Initialize a class instance."""
        self.client = SCIMClient(token=token)

        # settings for python requests module
        self.base_url = "https://api.slack.com/scim/v1"
        self.headers = {
            "accept": "application/json",
            "authorization": f"Bearer {token}"
        }

        self.groups = None
        self.groups_dict = None
        self.users = None
        self.users_dict = None

    @classmethod
    def get_group_member_ids(cls, group):
        """Return the primary email address of a SCIM user."""
        member_ids = []
        for member in group["members"]:
            member_ids.append(member["value"])
        return sorted(set(member_ids))

    @classmethod
    def get_user_primary_email(cls, user):
        """Return the primary email address of a SCIM user."""
        for email in user["emails"]:
            if email.get("primary"):
                return email["value"]
        return None

    @classmethod
    def get_user_primary_phone(cls, user):
        """Return the primary phone number of a SCIM user."""
        phone_numbers = user.get("phoneNumbers")
        if phone_numbers is None:
            return None
        for phone in phone_numbers:
            if phone.get("primary"):
                return phone["value"]
        return None

    @classmethod
    def prepare_group_members(cls, user_ids):
        """Return a list of group members, given a list of users."""
        group_members = []
        for user_id in user_ids:
            group_members.append({"value": user_id})
        return group_members

    def create_group(self, name, external_id=None, members=None, users=None):
        """Create an IDP Group."""
        body = {"displayName": name}
        if external_id:
            body["id"] = external_id
        if members:
            body["members"] = members
        elif users:
            body["members"] = self.prepare_group_members(users)
        group: Group = Group.from_dict(body)
        creation_result: Group = self.client.create_group(group)
        return creation_result

    def delete_group(self, group_id):
        """Delete an IDP Group."""
        return self.client.delete_group(group_id)

    def get_group(self, group_id):
        """Return a list of groups."""
        return self.client.read_group(group_id)

    def get_groups(self, search_filter=None):
        """Return a list of groups in Slack Enterprise Grid."""
        url = f"{self.base_url}/Groups"

        count = 1000
        params = {
            "count": count,
            "startIndex": 0,
            "filter": search_filter,
        }

        groups = []
        while True:
            response = requests.get(url, headers=self.headers, params=params).json()
            results = response["Resources"]
            if results:
                groups.extend(results)
            if len(results) < count:
                break
            params["startIndex"] += count
        return groups

    def get_groups_dict(self):
        """Return a dict of SCIM groups by name."""
        groups = {}
        for group in self.get_groups():
            index = group["displayName"]
            groups[index] = group
        return groups

    def get_user(self, user_id):
        """Return an SCIM user."""
        url = f"{self.base_url}/Users/{user_id}"
        return requests.get(url, headers=self.headers).json()

    def get_users(self, search_filter=None):
        """Return a list of users in Slack Enterprise Grid."""
        url = f"{self.base_url}/Users"

        count = 1000
        params = {
            "count": count,
            "startIndex": 0,
            "filter": search_filter,
        }

        users = []
        while True:
            response = requests.get(url, headers=self.headers, params=params).json()
            results = response["Resources"]
            if results:
                users.extend(results)
            if len(results) < count:
                break
            params["startIndex"] += count
        return users

    def get_users_dict(self, key="id"):
        """Return a dict of SCIM users by key."""
        users = {}
        for user in self.get_users():
            if key == "email":
                index = self.get_user_primary_email(user)
            else:
                index = user[key]
            users[index] = user
        return users

    def patch_group(self, group_id, body):
        """Return a group after patching the IDP group."""
        return self.client.patch_group(group_id, body)

    def patch_user(self, user_id, body):
        """Return a user after patching the IDP group."""
        return self.client.patch_user(user_id, body)

    def update_group(self, group_id, group):
        """Overwrite an IDP group."""
        return self.client.update_group(group_id, group)

    def update_user(self, user_id, user):
        """Overwrite an IDP user."""
        return self.client.update_user(user_id, user)
