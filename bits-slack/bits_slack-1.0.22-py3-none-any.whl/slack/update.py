# -*- coding: utf-8 -*-
"""Slack Update class file."""
import re

from bits.mongo import Mongo
from .scim import SCIM


class Update:
    """Slack Update class."""

    def __init__(self, slack, args, auth):
        """Initialize a class instance."""
        self.slack = slack
        self.args = args
        self.auth = auth

        self.email = False
        if "email" in args:
            self.email = True

        self.verbose = False
        if "verbose" in args or auth.verbose:
            self.verbose = True

        self.emplids = None
        self.github_profile_id = None
        self.google_users = None
        self.other_accounts = None
        self.people = None
        self.scim_users = None
        self.slack_emails = None
        self.slack_users = None
        self.team_profile = None

    def _auth_mongo(self):
        """Return an authenticated Mongo class."""
        mongo_db = self.auth.settings['mongo']['bitsdb']['db']
        mongo_uri = self.auth.settings['mongo']['bitsdb']['uri']
        return Mongo(mongo_uri, mongo_db)

    def _check_user(self, user):
        """Check a single user."""
        user_id = user["id"]
        profile = user["profile"]

        # get profile fields
        email = profile.get("email", "").lower()
        first_name = profile.get("first_name")
        last_name = profile.get("last_name")
        real_name = profile.get("real_name")
        phone = profile.get("phone")
        title = profile.get("title")

        # skip users with no email
        if not email:
            print(f"ERROR: User with no email: {real_name}")
            return None

        # check for an existing other account
        if email in self.other_accounts:
            return None

        # check for an existing person
        if email not in self.people:
            if not user["deleted"]:
                print(f"ERROR: Unknown user: {real_name} <{email}>")
            return None

        # get person
        person = self.people[email]
        person_first_name = person["first_name_ascii"]
        person_last_name = person["last_name_ascii"]
        person_phone = person.get("primary_work_phone")
        person_title = person["title"]

        suffix = self._get_pronouns_suffix(last_name)
        if suffix:
            person_last_name = f"{person_last_name} {suffix}"

        changes = []

        # check first name
        if person_first_name != first_name:
            changes.append(f"  first_name: {first_name} -> {person_first_name}")
            profile["first_name"] = person_first_name

        # check last name
        if person_last_name != last_name:
            changes.append(f"  last_name: {last_name} -> {person_last_name}")
            profile["last_name"] = person_last_name

        # check phone
        if person_phone and person_phone != phone:
            changes.append(f"  phone: {phone} -> {person_phone}")
            profile["phone"] = person_phone

        # check title
        if person_title != title:
            changes.append(f"  title: {title} -> {person_title}")
            profile["title"] = person_title

        # display changes
        if changes:
            print(f"\n{email}:")
            print("\n".join(changes))
            try:
                self.slack.set_user_profile(user_id, profile)
            except Exception as e:
                print(f"ERROR: Failed to update profile for user: {email} [{e}")

        # check activate
        if not person["terminated"] and user["deleted"]:
            return "activate"

        # check terminated
        if person["terminated"] and not user["deleted"]:
            return "deactivate"

        return None

    def _get_github_profile_field(self):
        """Return the ID of the field that represents the GitHub Profile."""
        label = "GitHub Profile"
        for field in self.team_profile.get("fields", {}):
            if field["label"] == label:
                return field["id"]
        return None

    def _get_google_group_emails(self, email):
        """Return the list of Slack users in a Google group."""
        g = self.auth.google()
        g.auth_service_account(g.scopes, g.subject)
        members = g.directory().get_derived_members(email)
        emails = []
        for member in members:
            if member["type"] != "USER":
                continue
            member_id = member["id"]
            if member_id in self.google_users:
                email = self.google_users[member_id]["primaryEmail"]
            else:
                email = member["email"].lower()
            emails.append(email)
        return emails

    def _get_google_group_users(self, email):
        """Return the list of Slack users in a Google group."""
        g = self.auth.google()
        g.auth_service_account(g.scopes, g.subject)
        members = g.directory().get_derived_members(email)
        users = []
        for member in members:
            if member["type"] != "USER":
                continue
            member_id = member["id"]
            if member_id in self.google_users:
                email = self.google_users[member_id]["primaryEmail"]
            else:
                email = member["email"].lower()
            if email not in self.slack_emails:
                continue
            user = self.slack_emails[email]
            user_id = user["id"]
            # skip deleted and single-channel guest users
            if not user["deleted"] and not user["is_restricted"] and not user["is_ultra_restricted"] and user_id not in users:
                users.append(user_id)
        return users

    def _get_google_users(self):
        """Return a dict of Google users."""
        g = self.auth.google()
        g.auth_service_account(g.scopes, g.subject)
        fields = "nextPageToken,users(id,primaryEmail,name/fullName,suspended)"
        return g.directory().get_users_dict(fields=fields)

    def _get_manager_user_id(self, person):
        """Return the manager value for scim."""
        manager_user_id = None
        manager_id = person["manager_id"]
        if manager_id in self.emplids:
            manager_email = self.emplids[manager_id]["email_username"]
            if manager_email in self.scim_users:
                manager_user_id = self.scim_users[manager_email]["id"]
        return manager_user_id

    def _get_people(self):
        """Return a dict of people from BITSdb."""
        collection = "gaia_people"
        project = "broad-gaia-prod"
        g = self.auth.google()
        firestore = g.firestore(project)
        people = {}
        self.emplids = {}
        for person in firestore.get_collection(collection):
            emplid = person["emplid"]
            self.emplids[emplid] = person
            key = person["email_username"]
            if not key:
                continue
            key = key.lower()
            if key in people:
                print(f"ERROR: Duplicate email in people: {key}")
                continue
            people[key] = person
        return people

    def _get_pronouns_suffix(self, last_name):
        """Return the pronouns suffix for the given last name."""
        suffix = ""
        if last_name and re.search(r"\(.*/.*\)$", last_name):
            suffix = re.sub(r".* (\(.*/.*\))$", r"\1", last_name).replace(" ", "")
        return suffix

    def _get_other_accounts(self):
        """Return a dict of other accounts from BITSdb."""
        mongo = self._auth_mongo()
        other_accounts = {}
        for account in mongo.get_collection("other_accounts"):
            key = account.get("slack_username")
            if not key:
                continue
            key = key.lower()
            if key in other_accounts:
                print(f"ERROR: Duplicate email in other accounts: {key}")
                continue
            other_accounts[key] = account
        return other_accounts

    def _get_slack_user_emails(self):
        """Return a dict of Slack users by email address."""
        if not self.slack_users:
            if self.verbose:
                print("Getting Slack users...")
            self.slack_users = self.slack.get_users_dict()
            if self.verbose:
                print(f"Found {len(self.slack_users)} Slack users.")
        emails = {}
        for user_id in self.slack_users:
            user = self.slack_users[user_id]
            email = user["profile"].get("email")
            if not email:
                continue
            if email in emails:
                print(f"ERROR: Duplicate email: {email}")
                continue
            emails[email.lower()] = user
        self.slack_emails = emails
        return self.slack_emails

    def _get_slack_group_sync_emails(self):
        """Return a list of Slack Group sync emails from BITSdb Cloud."""
        emails = []
        for sync in self.auth.bitsdbapi().get_slack_group_syncs():
            email = sync["google_group_email"]
            emails.append(email)
        return emails

    def _get_slack_usergroup_syncs(self):
        """Return a list of Slack Usergroup syncs from BITSdb."""
        emails = []
        usergroup_ids = []
        syncs = []
        mongo = self._auth_mongo()
        for sync in mongo.get_collection("slack_usergroup_sync"):
            email = sync["google_group"]
            usergroup_id = sync["slack_usergroup"]
            usergroup_name = sync["slack_usergroup_name"]
            if email in emails:
                print(f"WARNING: Duplicate sync email: {email}")
                continue
            emails.append(email)
            if usergroup_id in usergroup_ids:
                print(f"WARNING: Duplicate sync usergroup: {usergroup_name} [{usergroup_id}]")
                continue
            usergroup_ids.append(usergroup_id)
            syncs.append(sync)
        return syncs

    def _get_sync_group_emails(self):
        """Return a list of Google Group emails to sync."""
        if self.verbose:
            print("Getting Slack Group Syncs from BITSdb Cloud API...")
        emails = self._get_slack_group_sync_emails()
        if self.verbose:
            print(f"Group Sync Emails: {len(emails)}")

        if self.verbose:
            print("Getting Slack Usergroups Syncs from BITSdb Mongo DB...")
        syncs = self._get_slack_usergroup_syncs()
        if self.verbose:
            print(f"Usergroup Sync: {len(syncs)}")

        # create missing groups and update groups
        for sync in sorted(syncs, key=lambda x: x["google_group"]):

            # get google group email
            email = sync["google_group"].lower()
            if not email.endswith("@broadinstitute.org"):
                print(f"Skipping non-Broad group: {email}")
                continue

            if email not in emails:
                emails.append(email)
            else:
                print(f"Warning: Duplicate Sync Email: {email}")

        return sorted(set(emails))

    def _prepare_idp_user(self, person):
        """Prepare a user for the Slack IDP."""
        user = {
            "active": not person["terminated"],
            "name": {
                "familyName": person["last_name_ascii"],
                "givenName": person["first_name_ascii"],
                "honorificPrefix": None,
            },
            "phoneNumbers": [
                {
                    "type": "mobile",
                    "value": None,
                },
                {
                    "primary": True,
                    "value": person["primary_work_phone"],
                }
            ],
            "profileUrl": f"https://people-cloud.broadinstitute.org/people/{person['emplid']}",
            "timezone": "US/New_York",
            "title": person["title"],
            "urn:scim:schemas:extension:enterprise:1.0": {
                "costCenter": None,
                "department": person["department_name"],
                "division": person["org_unit"] or None,
                "employeeNumber": person["emplid"],
                "organization": person["home_institution"],
            },
            "userName": person["username"],
            "userType": person["worker_type"],
        }

        manager_id = self._get_manager_user_id(person)
        if manager_id:
            user["urn:scim:schemas:extension:enterprise:1.0"]["manager"] = {
                "managerId": manager_id
            }

        return user

    # def channels(self):
    #     """Update Channels in a Slack Workspace."""
    #     config = {
    #         # announcements
    #         # "C018J162V08": "activebroadies@broadinstitute.org",
    #         # workbench-userliaiason
    #         "CBJJ7U293": "workbench-userliaison@broadinstitute.org",
    #     }
    #     self._get_slack_user_emails()
    #     self.google_users = self._get_google_users()
    #     for channel_id, group_email in config.items():
    #         print(f"Syncing members from {group_email} -> {channel_id}...")
    #         group_members = self._get_google_group_emails(group_email)
    #         print(f"  Google Group Members: {len(group_members)}")
    #         group_ids = ["U205T4WV9"]
    #         for email in group_members:
    #             if email in self.slack_emails:
    #                 group_ids.append(self.slack_emails[email]["id"])
    #         print(f"  Google Group Slack Users: {len(group_ids)}")
    #         members = self.slack.get_conversation_members(channel_id)
    #         print(f"  Conversation Members: {len(members)}")

    #         add = list(set(group_ids) - set(members))
    #         remove = list(set(members) - set(group_ids))
    #         print(f"  Add: {len(add)}")
    #         print(f"  Remove: {len(remove)}")
    #         for user_id in remove:
    #             print(f"   - {user_id}")
    #             self.slack.kick_conversation_user(channel_id, user_id)

    def idp_groups(self):
        """Update the IDP Groups in Slack Enterprise Grid."""
        scim = SCIM(self.slack.token)

        if self.verbose:
            print("Getting Slack Groups from SCIM API...")
        groups = scim.get_groups_dict()
        if self.verbose:
            print(f"Groups: {len(groups)}")

        if self.verbose:
            print("Getting Slack Users from SCIM API...")
        users = scim.get_users_dict(key="email")
        if self.verbose:
            print(f"Users: {len(users)}")

        self.google_users = self._get_google_users()

        google_group_emails = self._get_sync_group_emails()

        # create missing groups and update groups
        for google_group_email in google_group_emails:

            # get google group email
            if not google_group_email.endswith("@broadinstitute.org"):
                print(f"Skipping non-Broad group: {google_group_email}")
                continue

            name = google_group_email.replace("@broadinstitute.org", "")

            # get google group members
            google_group_members = self._get_google_group_emails(google_group_email)

            if self.verbose:
                print(f"Syncing group: {google_group_email}")

            # assemble group member emails into slack users
            google_group_slack_user_ids = []
            for email in google_group_members:
                if email in users:
                    user = users[email]
                    user_id = user["id"]
                    # skip deleted and single-channel guest users
                    if user["active"] and email.endswith("@broadinstitute.org"):
                        google_group_slack_user_ids.append(user_id)
            google_group_slack_user_ids = sorted(set(google_group_slack_user_ids))

            # assemble group users into group members
            members = scim.prepare_group_members(google_group_slack_user_ids)

            if name not in groups:
                print(f"Creating group: {name}")
                print(scim.create_group(name=name, members=members))

            else:
                group = groups[name]
                group_member_ids = scim.get_group_member_ids(group)
                if group_member_ids != google_group_slack_user_ids:
                    print(f"Updating group from {len(group_member_ids)} to {len(google_group_slack_user_ids)} members: {name}")
                    group["members"] = members
                    scim.update_group(group["id"], group)

        # find groups to delete
        for name in groups:
            email = f"{name}@broadinstitute.org"
            group = groups[name]
            if email not in google_group_emails:
                print(f"Deleting group: {name}")
                scim.delete_group(group["id"])

    def idp_users(self):
        """Update IDP users in Slack."""
        scim = SCIM(self.slack.token)

        if self.verbose:
            print("Getting Slack Users from SCIM API...")
        self.scim_users = scim.get_users_dict(key="email")
        if self.verbose:
            print(f"Slack Users: {len(self.scim_users)}")

        if self.verbose:
            print("Getting People from Firestore...")
        self.people = self._get_people()
        if self.verbose:
            print(f"People: {len(self.people)}")

        for email in sorted(self.people):
            if self.people[email]["terminated"]:
                continue
            if email not in self.scim_users:
                print(f"Creating user: {email}...")
                person = self.people[email]
                idp_user = self._prepare_idp_user(person)
                idp_user["emails"] = [{"value": email, "primary": True}]
                try:
                    user = scim.client.create_user(idp_user)
                    print(f"  + Successfully created user: {user.id}")
                except Exception as error:
                    print(f"  ! Failed to create user: {error}")

        for email in self.scim_users:
            user = self.scim_users[email]

            # fix manager data
            if "urn:scim:schemas:extension:enterprise:1.0" in user:
                if "manager" in user["urn:scim:schemas:extension:enterprise:1.0"]:
                    if not user["urn:scim:schemas:extension:enterprise:1.0"]["manager"].get("managerId"):
                        del user["urn:scim:schemas:extension:enterprise:1.0"]["manager"]

            # skip non-people
            if email not in self.people:
                if email.endswith("@broadinstitute.org"):
                    if self.verbose:
                        print(f"Skipping unknown person: {email}")
                continue

            person = self.people[email]
            idp_user = self._prepare_idp_user(person)

            updates = []

            for key in sorted(idp_user):
                new = idp_user[key]
                old = user.get(key)
                if new != old:
                    updates.append(f"  {key}: {old} -> {new}")
                    user[key] = new
                    if key == 'phoneNumbers' and not user[key][1]["value"]:
                        user[key][1]["value"] = " "

            if updates:
                print(f"\nUpdating user: {email}...")
                print("\n".join(updates))
                try:
                    scim.update_user(user["id"], user)
                except Exception as e:
                    print(e)

    def profiles(self):
        """Update user profiles in Slack."""
        if not self.team_profile:
            self.team_profile = self.slack.get_team_profile().get("profile")
        self.github_profile_id = self._get_github_profile_field()
        print(f"Profile ID: {self.github_profile_id}")

        if not self.people:
            if self.verbose:
                print("Getting people...")
            self.people = self._get_people()
        if self.verbose:
            print(f"Found {len(self.people)} people.\n")

        if not self.slack_users:
            if self.verbose:
                print("Getting Slack users...")
            self.slack_users = self.slack.get_users_dict()
        if self.verbose:
            print(f"Found {len(self.slack_users)} Slack users.")

        for user_id in sorted(self.slack_users, key=lambda x: self.slack_users[x]["profile"].get("email", "")):
            user = self.slack_users[user_id]

            # skip deleted users
            if user["deleted"] or user["is_bot"] or user["id"] == "USLACKBOT":
                continue

            email = user["profile"].get("email")
            print(f"Email: {email}")

            # skip people with no email address
            if email not in self.people:
                print(f"Skipping user: {email}")
                continue

            # get person and their github login
            person = self.people[email]
            github_login = person.get("github_login")
            if github_login:
                print(f"  GitHub Login: {github_login}")

            # check github profile field
            if github_login and self.github_profile_id:

                # get the user profile with profile fields
                profile = self.slack.get_user_profile(user_id).get("profile")
                fields = profile.get("fields")
                if not fields:
                    fields = {}

                # create the profile value from the github_login
                github_url = f"https://github.com/{github_login}"
                body = {
                    "value": github_url,
                    "alt": github_login,
                }

                if self.github_profile_id not in fields:
                    fields[self.github_profile_id] = body
                elif fields[self.github_profile_id] != body:
                    fields[self.github_profile_id] = body

                if fields != profile.get("fields"):
                    print(f"Updating GitHub Profile for: {email}...")
                    profile["fields"] = fields
                    self.slack.set_user_profile(user_id, profile)
                else:
                    print(f"  No update required for: {email}")

    def usergroups(self):
        """Update usergroups in Slack."""
        self._get_slack_user_emails()

        if self.verbose:
            print("Getting syncs...")
        syncs = self._get_slack_usergroup_syncs()
        if self.verbose:
            print(f"Usergroup Sync Rules: {len(syncs)}")

        if self.verbose:
            print("Getting Usergroups...")
        usergroups = self.slack.get_usergroups_dict(include_disabled=True, include_users=True)
        if self.verbose:
            print(f"Usergroups: {len(usergroups)}")

        self.google_users = self._get_google_users()

        for sync in sorted(syncs, key=lambda x: x.get("google_group", "")):
            google_group = sync.get("google_group")
            usergroup_id = sync.get("slack_usergroup")
            usergroup_name = sync.get("slack_usergroup_name")

            if usergroup_id not in usergroups:
                print(f"ERROR: Usergroup not found: {usergroup_name} [{usergroup_id}] ({google_group})")
                continue

            usergroup = usergroups[usergroup_id]

            # skip deleted usergroups
            if usergroup.get("date_delete"):
                continue

            # get current slack usergroup users
            users = sorted(usergroup.get("users", []))

            # get google group members as slack users
            group_users = sorted(self._get_google_group_users(google_group))

            if users != group_users:
                print(f"\n{google_group} -> {usergroup_name} [{usergroup_id}]")
                add = list(set(group_users) - set(users))
                delete = list(set(users) - set(group_users))
                if add:
                    print(f"  Adding {len(add)} users:")
                    for user_id in sorted(add, key=lambda x: self.slack_users[x]["profile"]["email"].lower()):
                        user = self.slack_users[user_id]
                        email = user["profile"]["email"].lower()
                        print(f"   + {email}")
                if delete:
                    print(f"  Deleting {len(delete)} users:")
                    for user_id in sorted(delete, key=lambda x: self.slack_users[x]["profile"]["email"].lower() if x in self.slack_users else ""):
                        user = self.slack_users[user_id]
                        email = user["profile"]["email"].lower()
                        print(f"   - {email}")
                if add or delete:
                    try:
                        self.slack.update_usergroup_users(usergroup_id, group_users)
                    except Exception as e:
                        print(f"ERROR: Failed to update Usergroup: {usergroup_name} [{usergroup_id}]: {e}")

    def users(self):
        """Update users in Slack."""
        if not self.other_accounts:
            if self.verbose:
                print("Getting other accounts...")
            self.other_accounts = self._get_other_accounts()
        if self.verbose:
            print(f"Found {len(self.other_accounts)} other accounts.\n")

        if not self.people:
            if self.verbose:
                print("Getting people...")
            self.people = self._get_people()
        if self.verbose:
            print(f"Found {len(self.people)} people.\n")

        if not self.slack_users:
            if self.verbose:
                print("Getting Slack users...")
            self.slack_users = self.slack.get_users_dict()
        if self.verbose:
            print(f"Found {len(self.slack_users)} Slack users.")

        bots = []
        restricted = []
        ultra_restricted = []

        activate = []
        deactivate = []

        # check each user
        for user_id in sorted(self.slack_users, key=lambda x: self.slack_users[x]["profile"].get("email", "")):
            user = self.slack_users[user_id]

            # count and skip bot users
            if user["is_bot"] or user["id"] == "USLACKBOT":
                bots.append(user)
                continue

            # count single-channel and multi-channel guests
            if user.get("is_ultra_restricted"):
                ultra_restricted.append(user)
            elif user.get("is_restricted"):
                restricted.append(user)

            # check for users to activate or deactivate
            action = self._check_user(user)
            if action == "activate":
                activate.append(user)
            elif action == "deactivate":
                deactivate.append(user)

        # output activations/decativations
        if activate:
            print(f"\nUsers to activate: {len(activate)}")
            for user in activate:
                print(f"  + {user['profile']['email']}")
        if deactivate:
            print(f"\nUsers to deactivate: {len(deactivate)}")
            for user in deactivate:
                print(f"  - {user['profile']['email']}")

        # output stats about bots/guests
        if self.verbose:
            print(f"\nBot Users: {len(bots)}")
            print(f"Single-Channel Guests: {len(ultra_restricted)}")
            print(f"Multi-Channel Guests: {len(restricted)}")
