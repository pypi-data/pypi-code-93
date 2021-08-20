from datetime import datetime
import sys

import ccalogging
from ccautils.errors import errorRaise

from ccaaws.botosession import BotoSession

log = ccalogging.log


class AccessKeyError(Exception):
    pass


class IamClient(BotoSession):
    def __init__(self, username, **kwargs):
        super().__init__(**kwargs)
        self.newClient("iam")
        self.username = username
        self.currentkey = None
        self.user = None

    def testProfile(self):
        user = self.getKeys()
        if type(user) is dict:
            if "keys" in user:
                log.debug("User: {}".format(user["Arn"]))
                return True
        return False

    def listUsers(self):
        try:
            users = []
            kwargs = {}
            while True:
                xusers = self.client.list_users(**kwargs)
                for user in xusers["Users"]:
                    if "PasswordLastUsed" in user:
                        user["pwlastused"] = int(
                            datetime.timestamp(user["PasswordLastUsed"])
                        )
                    kuser = self.getKeys(user)
                    users.append(kuser)

                if "IsTruncated" in xusers and xusers["IsTruncated"]:
                    kwargs["Marker"] = xusers["Marker"]
                else:
                    break
            return users
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def _getUser(self):
        """returns a user dict

        This is intended to not be called standalone, but to be called by the
        getKeys() method, so that the user information is as complete as
        possible
        """
        try:
            user = self.client.get_user(UserName=self.username)
            user["passwordage"] = self._getPasswordAge()
        except Exception as e:
            msg = f"""IamClient: Failed to retrieve username,
                are you actually connected
                {e}
                """
            log.error(msg)
            return False
        return user["User"]

    def _getPasswordAge(self):
        """ returns the date the console password was last set

        is intended not to be called standalone, but as an addition to the
        _getUser() method above
        """
        try:
            passwordage = None
            lp = self.client.get_login_profile(UserName=self.username)
            if lp is not None:
                if "LoginProfile" in lp:
                    passwordage = lp["LoginProfile"]["CreateDate"]
        except ClientError as e:
            # if user doesn't have a console pasword
            # boto raises a ClientError Exception
            pass
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)
        finally:
            return passwordage

    def getKeys(self, user):
        """returns a user dict complete with registered access keys"""
        # user = self._getUser()
        log.debug("user: {}".format(user))
        if user is not False:
            self.user = user
            self.username = self.user["UserName"]
            self.user["passwordage"] = self._getPasswordAge()
            try:
                keys = self.client.list_access_keys(UserName=self.user["UserName"])
                log.debug("keys: {}".format(keys))
                self.user["keys"] = []
                for key in keys["AccessKeyMetadata"]:
                    kid = key["AccessKeyId"]
                    klu = self.client.get_access_key_last_used(AccessKeyId=kid)
                    if "LastUsedDate" in klu["AccessKeyLastUsed"]:
                        key["LastUsedDate"] = klu["AccessKeyLastUsed"]["LastUsedDate"]
                        key["lastused"] = int(
                            datetime.timestamp(klu["AccessKeyLastUsed"]["LastUsedDate"])
                        )
                    self.user["keys"].append(key)
                # self.user["keys"] = keys["AccessKeyMetadata"]
            except Exception as e:
                log.error(
                    "Failed to obtain access key infomation for user: {}".format(
                        self.user["UserName"]
                    )
                )
                log.error("Exception was {}: {}".format(type(e).__name__, e))
                raise
        return self.user

    # I'm not writing tests for the methods below as they
    # all fiddle with credentials. They all fail safe, so
    # your credentials are safe unless they do what they say they
    # are going to do.  Just use the rotateKeys method and
    # forget about whinging.  The dictionary it returns will
    # have your current, active key and secret information.
    def __delete_inactive_keys(self):
        """If the user has an inactive key, this will delete it

        sets the self.currentkey to the currently active key id
        so this must be run before generating a new key so that the
        old key can be deactivated easily.  Also, AWS only allows
        a user to have 2 keys at any one time (whether active or not).
        """
        res = True
        self.user = self.getKeys()
        for key in self.user["keys"]:
            if key["Status"] == "Active":
                self.currentkey = key["AccessKeyId"]
            elif key["Status"] == "Inactive":
                try:
                    self.client.delete_access_key(
                        AccessKeyId=key["AccessKeyId"], UserName=self.user["UserName"]
                    )
                except Exception as e:
                    msg = "An error occurred deleting the inactive access key: {}".format(
                        key["AccessKeyId"]
                    )
                    msg += " for user {}, the exception was: {}".format(
                        self.user["UserName"], e
                    )
                    log.error(msg)
                    res = False
        return res

    def __deactivate_current_key(self):
        """This will deactivate the users currently active key

        This must be called after generating a new key, so that the
        user only has one active key at any one time
        """
        res = True
        if self.currentkey is not None:
            try:
                self.client.update_access_key(
                    AccessKeyId=self.currentkey,
                    UserName=self.user["UserName"],
                    Status="Inactive",
                )
            except Exception as e:
                msg = "Failed to de-activate the current key {} for user{}.".format(
                    self.currentkey, self.user["UserName"]
                )
                msg += " Error was{}".format(e)
                log.error(msg)
                res = False
        return res

    def __generate_new_key(self):
        key = False
        try:
            key = self.client.create_access_key(UserName=self.user["UserName"])
            # rebuild the user dictionary
            # I know, but it saves dicking around deleting keys from
            # the user dictionary and deactivating the current one later on
            # this does it all in one line, te he he.
            self.getKeys()
        except Exception as e:
            log.error(
                "Exception generating a new key for user {}, {}".format(
                    self.user["UserName"], e
                )
            )
        return key

    def rotateKeys(self):
        """This will leave the user with a new, active key

        It first deletes any inactive key,
        then generates a new active key,
        the de-activates the original key.
        returns a dictionary:
        {
        "UserName": the users name
        "Arn": the arn of the user
        "Keys": hash of key dicts.
            [{
            "AccessKeyId": access key id
            "SecretAccessKey": secret access key id
            "Status": Active | Inactive
            },
            {...}]
        """
        key = None
        try:
            if self.__delete_inactive_keys() is False:
                raise AccessKeyError("Failure to delete inactive key")
            key = self.__generate_new_key()
            if key is False:
                raise AccessKeyError("Failure to generate a new key")
            if self.__deactivate_current_key() is False:
                raise AccessKeyError("Failure to de-activate the users current key")
        except Exception as e:
            log.error("An error occurred while attempting key rotation, see logs.")
            log.error("Exception was {}".format(e))
        return key
