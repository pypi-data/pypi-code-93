from huaweicloudsdkcore.auth.credentials import BasicCredentials, GlobalCredentials


class HuaweiClient(object):

    def __init__(self, access_key_id, access_key_secret, region):
        self.ak = access_key_id
        self.sk = access_key_secret
        self.region = region

    @property
    def credentials(self):
        return BasicCredentials(self.ak, self.sk)

    def generate_client(self, client_name, region_name):
        return client_name.new_builder(). \
            with_credentials(self.credentials). \
            with_region(region_name.value_of(self.region)). \
            build()

    @property
    def global_credentials(self):
        return GlobalCredentials(self.ak, self.sk)

    def generate_global_client(self, client_name, region_name):
        return client_name.new_builder(). \
            with_credentials(self.global_credentials). \
            with_region(region_name.value_of(self.region)). \
            build()
