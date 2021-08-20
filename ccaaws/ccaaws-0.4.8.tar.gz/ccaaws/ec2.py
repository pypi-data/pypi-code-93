""" ccaaws ec2 class
"""
import sys

from botocore.exceptions import ClientError
import ccalogging
from ccautils.errors import errorRaise

from ccaaws.botosession import BotoSession

log = ccalogging.log


class EC2(BotoSession):
    def __init__(self, **kwargs):
        """ connect to aws

        to switch region supply the `region` keyword
        """
        super().__init__(**kwargs)
        self.newClient("ec2")

    def findInstances(self, instlist):
        """ find instances in instlist

        instlist is a list of instance-id strings
        """
        try:
            instances = []
            kwargs = {"InstanceIds": instlist} if type(instlist) is list else {}
            while True:
                try:
                    # will raise client error if instances don't exist
                    resp = self.client.describe_instances(**kwargs)
                    try:
                        rinsts = [
                            i["Instances"]
                            for i in [
                                r for r in resp["Reservations"] if "Instances" in r
                            ]
                        ]
                        instances += [i for subi in rinsts for i in subi]
                        kwargs["NextToken"] = resp["NextToken"]
                    except KeyError:
                        break
                except ClientError as ce:
                    log.debug(f"ClientError: Instances probably don't exist: {ce}")
                    break
            return instances
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def getMatchingInstances(self, instlst=None):
        """ find the instances named in the `instlst` list
        or all instances if `instlst` is None

        NOTE: this does not appear to work with filters, use
        the 'findInstances' function above
        """
        try:
            instances = []
            kwargs = {}
            if type(instlst) is list:
                kwargs["Filters"] = [{"Name": "instance-id", "Values": instlst}]
            while True:
                resp = self.client.describe_instances(**kwargs)
                try:
                    rinsts = [
                        i["Instances"]
                        for i in [r for r in resp["Reservations"] if "Instances" in r]
                    ]
                    instances += [i for subi in rinsts for i in subi]
                    kwargs["NextToken"] = resp["NextToken"]
                except KeyError:
                    break
            return instances
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def getRegions(self):
        """
        returns a list of all available regions
        """
        try:
            resp = self.client.describe_regions()
            regions = [
                region["RegionName"] for region in resp["Regions"] if "Regions" in resp
            ]
            log.debug("Regions: {}".format(regions))
            return regions
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)
