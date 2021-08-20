""" ccaaws cloudformation class
"""
import sys
import time

from botocore.exceptions import ClientError
import ccalogging
from ccautils.errors import errorRaise
import ccautils.fileutils as FT
import ccautils.utils as UT

from ccaaws import __version__
from ccaaws.botosession import BotoSession

log = ccalogging.log


class CFNClient(BotoSession):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.newClient("cloudformation")

    def stackDetails(self, stackname):
        try:
            resp = self.client.describe_stacks(StackName=stackname)
            if "Stacks" in resp:
                stack = resp["Stacks"][0]
                return stack
        except ClientError:
            log.debug(f"stack: {stackname} does not exist")
            return None
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def stackStatus(self, stackname):
        try:
            stack = self.stackDetails(stackname)
            return stack["StackStatus"] if stack is not None else None
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def createStack(self, **kwargs):
        try:
            resp = self.client.create_stack(**kwargs)
            if "StackId" in resp:
                return resp["StackId"]
            return None
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def updateStack(self, **kwargs):
        try:
            resp = self.client.update_stack(**kwargs)
            if "StackId" in resp:
                return resp["StackId"]
            return None
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def deleteStack(self, stackname):
        try:
            self.client.delete_stack(StackName=stackname)
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def waitForStack(self, stackn, timeout=10, sleeptime=30):
        """ wait for a stack to become "..._COMPLETE"

        waits for timeout * sleeptime seconds

        returns the stack status
        """
        try:
            status = None
            cn = 0
            sleeptime = sleeptime
            while True:
                cn += 1
                if cn > timeout:
                    log.error(
                        f"Timeout expired waiting for stack {stackn} to become ready"
                    )
                    break
                status = self.stackStatus(stackn)
                if status is not None and "COMPLETE" in status:
                    log.info(f"Stack {stackn} is {status}")
                    break
                elif status is None:
                    log.warning(f"stack {stackn} does not exist (anymore)")
                    break
                time.sleep(sleeptime)
            return status
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def checkStack(self, stack):
        ok = False
        log.debug(f"checking stack: {stack}")
        if "StackStatus" in stack:
            log.debug("status is in stack")
            if stack["StackStatus"] in ["UPDATE_COMPLETE", "CREATE_COMPLETE"]:
                log.debug("is one of the updates")
                if "Tags" in stack:
                    log.debug("stack has tags")
                    for tag in stack["Tags"]:
                        if tag["Key"] == "version":
                            log.debug(
                                f"""version tag: {tag["Value"]}, version: {__version__}"""
                            )
                            if tag["Value"] == __version__:
                                log.debug("version tag is correct")
                                ok = True
        return ok

    def expandDictToList(self, xdict, keyname="Key", valuename="Value"):
        """ expands a dictionary into a list of dictionaries, one per key

            {"somekey": "someval", "otherkey": "otherval"}

        returns a list of dictionaries

            [
                {"Key": "somekey", "Value": "someval"},
                {"Key": "otherkey", "Value": "otherval"},
            ]
        """
        try:
            op = []
            for key in xdict:
                tmp = {keyname: key, valuename: xdict[key]}
                op.append(tmp)
            return op
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def buildStackTags(self, tagdict):
        """ converts a set of tags into the form used by CFN Stacks

                tagdict = {
                    "owner": "sre",
                    "environment": "prod",
                    "product": "ccaaws",
                }

        returns a list of dictionaries
            [
                {"Key": "owner", "Value": "sre"},
                {"Key": "environment", "Value": "prod"},
                {"Key": "product", "Value": "ccaaws"},
            ]
        """
        try:
            tagdict["version"] = __version__
            tagdict["builder"] = "ccaaws"
            return self.expandDictToList(tagdict)
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def buildStackParams(self, paramdict):
        """ builds a set of parameters from a paramstring
        """
        try:
            lpd = self.expandDictToList(
                paramdict, keyname="ParameterKey", valuename="ParameterValue"
            )
            return lpd
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def testParam(
        self,
        param,
        options,
        testlist=False,
        teststr=False,
        testint=False,
        testdict=False,
    ):
        if param in options and options[param] is not None:
            if testlist:
                return True if type(options[param]) is list else False
            elif teststr:
                return True if type(options[param]) is str else False
            elif testint:
                return True if type(options[param]) is int else False
            elif testdict:
                return True if type(options[param]) is dict else False
            else:
                return True
        return False

    def buildStackDict(self, options):
        """ sets up the stack 'dictionary' for the create/update stack functions

        param: options
               a dictionary of required options for the stack
                "templatefn": fqfn of the yaml or json template for the stack
                "stackname": the name of the stack
                "params"(optional): the parameters of the stack in string form
                          'param1=val1,param2=val2'
                    or dict form:
                          {"param1": "val1", "param2": "val2"}
                "tags"(optional): the stack tags in dict form
                "capabilities"(optional): ["CAPABILITY_IAM"] or ["CAPABILITY_NAMED_IAM"]

        returns a dictionary ready for the stack create/update functions
        """
        try:
            template = FT.readFile(options["templatefn"])
            if template is None:
                raise Exception(f"""Failed to read {options["templatefn"]}""")
            xd = {"StackName": options["stackname"], "TemplateBody": template}
            if self.testParam("params", options, teststr=True):
                pd = UT.makeDictFromString(options["params"])
                xd["Parameters"] = self.buildStackParams(pd)
            elif self.testParam("params", options, testdict=True):
                xd["Parameters"] = self.buildStackParams(options["params"])
            if self.testParam("tags", options, testdict=True):
                xd["Tags"] = self.buildStackTags(options["tags"])
            else:
                xd["Tags"] = self.buildStackTags({})
            if self.testParam("capabilities", options, testlist=True):
                if len(options["capabilities"]) > 0:
                    xd["Capabilities"] = options["capabilities"]
            return xd
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def installOrUpdateStack(self, options):
        """ installs a stack if it doesn't exist or updates it

        param options: as for the buildStackDict function above

        returns stack status or None
        """
        try:
            status = self.waitForStack(options["stackname"])
            xd = self.buildStackDict(options)
            if status is not None and "COMPLETE" in status:
                if not self.checkStack(self.stackDetails(options["stackname"])):
                    # stack exists, so update it
                    log.warning(f"""updating stack {options["stackname"]}""")
                    self.updateStack(**xd)
                    time.sleep(10)
                    status = self.waitForStack(options["stackname"])
                else:
                    log.info(f"""Stack {options["stackname"]} is up to date""")
            elif status is None:
                log.info(f"""creating stack {options["stackname"]}""")
                self.createStack(**xd)
                time.sleep(10)
                status = self.waitForStack(options["stackname"])
            else:
                msg = f"""stack {options["stackname"]} is status: {status}"""
                log.warning(msg)
                raise Exception(msg)
        except ClientError as ce:
            log.warning("Client Error: stack probably already up to date")
            log.warning(f"{ce}")
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)
