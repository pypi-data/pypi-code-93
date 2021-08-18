from intstreamsdk import job, resource

MITIGATED = "mitigated"

RESOURCE_IPV4 = "IPV4"
RESOURCE_IPV6 = "IPV6"
RESOURCE_MD5 = "MD5"
RESOURCE_SHA1 = "SHA1"
RESOURCE_SHA256 = "SHA256"
RESOURCE_NETLOC = "NetLoc"
RESOURCE_EMAIL = "Email"


class UnMitigateJob(job.IndicatorJob):
    def __init__(self, client_class, model):
        """

        :param client_class:
        :param model: str
        """
        super(UnMitigateJob, self).__init__(client_class)
        self.model = model

    def do_unmitigate(self, indicator):
        """
        api code to mitigate here.
        If mitigated return true
        :param indicator:
        :return: Boolean
        """
        raise NotImplemented

    def custom(self, parsed_args):

        # get indicator data
        ip_resource = getattr(resource, self.model)(self.client)
        ip_resource.filter({"value": parsed_args.indicator})
        res = ip_resource.full_request()
        indicators = res["data"]["results"]
        # if indicator found
        if len(indicators) > 0:
            indicator_id = indicators[0]["id"]
            put_resource = getattr(resource, self.model)(self.client, resource.Resource.PUT)
            put_resource.id(indicator_id)
            indicator_data = indicators[0]
            if indicator_data[MITIGATED]:
                unmitigated = self.do_unmitigate(parsed_args.indicator)
                if unmitigated:
                    indicator_data[MITIGATED] = False
                    put_resource.indicators_put(indicator_data)
                    put_resource.full_request()


class MitigateJob(job.IndicatorJob):
    def __init__(self, client_class, model):
        """
        :param client_class:
        :param model: str
        """
        super(MitigateJob, self).__init__(client_class)
        self.model = model

    def do_mitigate(self, indicator):
        """
        api code to mitigate here.
        If mitigated return true
        :param indicator:
        :return: Boolean
        """
        raise NotImplemented

    def custom(self, parsed_args):
        """
        DO NOT EDIT
        :param parsed_args:
        :return:
        """
        # get indicator data
        ip_resource = getattr(resource, self.model)(self.client)
        ip_resource.filter({"value": parsed_args.indicator})
        res = ip_resource.full_request()
        indicators = res["data"]["results"]
        # if indicator found
        if len(indicators) > 0:
            indicator = indicators[0]
            indicator_id = indicator["id"]
            if not indicator[MITIGATED]:
                do_mitigate = False
                if indicator["allowed"]:
                    do_mitigate = False
                else:
                    do_mitigate = self.do_mitigate(indicator)
                if do_mitigate:
                    put_resource = getattr(resource, self.model)(self.client, resource.Resource.PUT)
                    put_resource.id(indicator_id)
                    indicator[MITIGATED] = True
                    put_resource.indicators_put(indicator)
                    put_resource.full_request()
