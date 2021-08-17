from gateways.apis.api_base_class import ApiBase


class ApiIntegration(ApiBase):
    def get_insided_token(self):
        return self.build_route("integrations/insided/token")
