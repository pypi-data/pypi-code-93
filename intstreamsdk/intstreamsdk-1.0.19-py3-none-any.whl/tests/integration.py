import unittest
import logging
import time
import os
from intstreamsdk.client import SyncClient, AsyncClient
from intstreamsdk import resource

class Indicator(unittest.TestCase):
    def setUp(self):
        username = os.environ.get("TESTUSER", "")
        password = os.environ.get("TESTPASSWORD", "")
        server = os.environ.get("TESTSERVER", "http://127.0.0.1:8000")
        self.client = SyncClient(username=username,
                            password=password,
                            server_url=server)

    def test_indicator_jobs(self):
        """
        need to start the celery workers to fully test this
        :return:
        """

        # upload indicatorjob
        base_dir = os.environ.get("BASE_DIR", "/tmp")
        job_file = os.path.join(base_dir, "fixtures/indicatorjob.tar.gz") # adds a traffic column
        text_job_file = os.path.join(base_dir, "fixtures/indicatorjobtext.tar.gz") # adds a traffic column

        ind_types = resource.IndicatorType(self.client, method=resource.Resource.GET)
        ind_types.filter({"name":"IPV4"})
        r = ind_types.full_request()
        ip_id = r["data"]["results"][0]["id"]

        #########################
        # see if text job exists
        #########################
        r_ind_job_check = resource.IndicatorJob(self.client)
        name = "ip_category"
        r_ind_job_check.filter({"name":name})
        r_exists = r_ind_job_check.full_request()
        text_job_id = None
        if len(r_exists["data"]["results"]) == 0:
            resource_ind_job = resource.IndicatorJob(self.client, method=resource.Resource.POST)
            resource_ind_job.job_post(name=name,
                                      indicator_type_ids=[ip_id],
                                      python_version="3.6",
                                      user=os.environ.get("TESTUSER",""),
                                      timeout=600
                                      )
            r_job = resource_ind_job.full_request()

            text_job_id = r_job["data"]["id"]
        else:
            text_job_id = r_exists["data"]["results"][0]["id"]

        # see if version exists already
        version = "1.0.0"
        r_job_version_get = resource.IndicatorJobVersion(self.client,)
        r_job_version_get.filter({"job": text_job_id,
                                  "version": version
                                  })
        res = r_job_version_get.full_request()
        text_job_version_id = None
        if len(res["data"]["results"]) == 0:
            resource_job_version = resource.IndicatorJobVersion(self.client, method=resource.Resource.POST)
            resource_job_version.job_version_post(text_job_id, version, text_job_file)
            r = resource_job_version.full_request()
            text_job_version_id = r["data"]["id"]
        else:
            text_job_version_id = res["data"]["results"][0]["id"]

        #########################
        # see if traffic job exists already
        #########################
        r_ind_job_check = resource.IndicatorJob(self.client)
        name = "ip_traffic"
        r_ind_job_check.filter({"name":name})
        r_exists = r_ind_job_check.full_request()
        job_id = None
        if len(r_exists["data"]["results"]) == 0:
            resource_ind_job = resource.IndicatorJob(self.client, method=resource.Resource.POST)
            resource_ind_job.job_post(name=name,
                                      indicator_type_ids=[ip_id],
                                      python_version="3.6",
                                      user=os.environ.get("TESTUSER",""),
                                      timeout=600
                                      )
            r_job = resource_ind_job.full_request()

            job_id = r_job["data"]["id"]
        else:
            job_id = r_exists["data"]["results"][0]["id"]

        # see if version exists already
        version = "1.0.0"
        r_job_version_get = resource.IndicatorJobVersion(self.client,)
        r_job_version_get.filter({"job": job_id,
                                  "version": version
                                  })
        res = r_job_version_get.full_request()
        job_version_id = None
        if len(res["data"]["results"]) == 0:
            resource_job_version = resource.IndicatorJobVersion(self.client, method=resource.Resource.POST)
            resource_job_version.job_version_post(job_id, version, job_file)
            r = resource_job_version.full_request()
            job_version_id = r["data"]["id"]
        else:
            job_version_id = res["data"]["results"][0]["id"]

        #insert indicator
        indicator = "1.1.1.1"
        uploader = resource.IndicatorAction(self.client)
        r = uploader.check_upload([indicator], resource.IPV4)
        ind_id = r[0]["id"]
        # wait for job to finish in celery
        time.sleep(55)
        # verify custom job field exists
        r_traffic = resource.IndicatorNumericField(self.client)
        r_traffic.filter({"indicator": ind_id, "name": "traffic"})
        res_traffic = r_traffic.full_request()

        # verify text custom job field exists
        r_cat = resource.IndicatorTextField(self.client)
        r_cat.filter({"indicator": ind_id, "name": "category"})
        res_cat = r_cat.full_request()

        # delete indicator
        r_del = uploader.check_delete([indicator], resource.IPV4)

        # delete job and versions
        res_del_job = resource.IndicatorJob(self.client, method=resource.Resource.DELETE)
        res_del_job.id(job_id)
        r_d0 = res_del_job.full_request()

        # delete text job and versions
        res_del_job = resource.IndicatorJob(self.client, method=resource.Resource.DELETE)
        res_del_job.id(text_job_id)
        r_d1 = res_del_job.full_request()

        self.assertEqual(len(res_traffic["data"]["results"]), 1)
        self.assertEqual(len(res_cat["data"]["results"]), 1)


class IntegrationAsync(unittest.TestCase):
    def setUp(self):
        username = os.environ.get("TESTUSER", "")
        password = os.environ.get("TESTPASSWORD", "")
        server = os.environ.get("TESTSERVER", "http://127.0.0.1:8000")
        self.client = AsyncClient(username=username,
                            password=password,
                            server_url=server)

    def test_md5_resource(self):
        # get ind
        ind = "0800fc577294c34e0b28ad2839435945"
        res = resource.MD5(client=self.client, method=resource.Resource.GET)
        res.indicators_post([ind])
        result = res.full_request(raise_exc=True)
        length = len(result.get("data", {}).get("results",[]))
        # if exists delete
        if result["status"] == "SUCCESS"and length == 1:
            id = result.get("data", {}).get("results",[])[0]["id"]
            res = resource.MD5(client=self.client, method=resource.Resource.DELETE)
            res.id(id)
            # could do multiple full requests here in a for loop and they will async
            pre_r = res.request()
            # collect multiple responses
            result = res.getdata(pre_r, raise_exc=True)
            self.assertEqual(result["status"], "SUCCESS")
        # create
        res = resource.MD5(client=self.client, method=resource.Resource.POST)
        res.indicators_post([ind])
        result = res.full_request(raise_exc=True)
        self.assertEqual(result["status"], "SUCCESS")


class IntegrationSync(unittest.TestCase):

    def setUp(self):
        username = os.environ.get("TESTUSER", "")
        password = os.environ.get("TESTPASSWORD", "")
        server = os.environ.get("TESTSERVER", "http://127.0.0.1:8000")
        self.client = SyncClient(username=username,
                            password=password,
                            server_url=server)

    def test_email(self):
        ind = "test@testing.com"
        self._delete_update(resource.Email, ind)
        uploader = resource.Uploader(self.client)
        r_del = uploader.check_delete([ind], resource.Email)


    def _delete_update(self, resource_class, ind):
        """

        :param resource_class:
        :param ind: str
        :return:
        """
        res = resource_class(client=self.client, method=resource.Resource.GET)
        res.filter({"value_in":",".join([ind])})
        result = res.full_request(raise_exc=True)
        length = len(result.get("data", {}).get("results",[]))
        # if exists delete
        if result["status"] == "SUCCESS"and length == 1:
            id = result.get("data", {}).get("results",[])[0]["id"]
            res = resource_class(client=self.client, method=resource.Resource.DELETE)
            res.id(id)
            result = res.full_request(raise_exc=True)
            self.assertEqual(result["status"], "SUCCESS")
        # create indicator
        res = resource_class(client=self.client, method=resource.Resource.POST)
        res.indicators_post([ind])
        result = res.full_request(raise_exc=True)
        self.assertEqual(result["status"], "SUCCESS")

    def test_ipv4(self):
        ind = "1.1.1.1"
        self._delete_update(resource.IPV4, ind)
        uploader = resource.Uploader(self.client)
        r_del = uploader.check_delete([ind], resource.IPV4)

    def test_ipv6(self):
        ind = "2607:f0d0:1002:0051:0000:0000:0000:0004"
        self._delete_update(resource.IPV6, ind)
        uploader = resource.Uploader(self.client)
        r_del = uploader.check_delete([ind], resource.IPV6)

    def test_md5_resource(self):
        # get indicator
        ind = "0800fc577294c34e0b28ad2839435945"
        self._delete_update(resource.MD5, ind)
        uploader = resource.Uploader(self.client)
        r_del = uploader.check_delete([ind], resource.MD5)


    def test_sha256_resource(self):
        # get indicator
        ind = "b1bb0b49069db3871451654efb038e9674ca2595d665c9fc6b5c65e54c5f76cb"
        self._delete_update(resource.SHA256, ind)
        uploader = resource.Uploader(self.client)
        r_del = uploader.check_delete([ind], resource.SHA256)

    def test_sha1_resource(self):
        # get indicator
        ind = "2346ad27d7568ba9896f1b7da6b5991251debdf2"
        self._delete_update(resource.SHA1, ind)
        uploader = resource.Uploader(self.client)
        r_del = uploader.check_delete([ind], resource.SHA1)

    def test_domain(self):
        dom1 = "test.com"
        dom2 = "testing.com"
        ind = [dom1, dom2]
        # upload urls
        uploader = resource.DomainLoader(ind, self.client)
        r = uploader.upload()
        
        # verify dom1 in database
        extractor = resource.DomainExtractor(dom1, self.client)
        resource_net_loc = resource.NetLoc(client=self.client, method=resource.Resource.GET)
        filter = {
            "suffix": extractor.net_loc.suffix_id,
            "domain": extractor.net_loc.domain,
            "subdomain": extractor.net_loc.subdomain
        }
        resource_net_loc.filter(filter=filter)
        r = resource_net_loc.full_request()
        self.assertEqual(r["data"]["count"], 1)

        # delete
        uploader.delete()
        r = resource_net_loc.full_request()
        self.assertEqual(r["status"], resource.Resource.SUCCESS)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    unittest.main()





