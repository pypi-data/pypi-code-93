class DeployLog:
    """
        Deploy log parameter object.
    """

    def __init__(self):
        self._start_time = None
        self._end_time = None
        self._req_method = None
        self._req_url = None
        self._req_body = None
        self._status_code = None
        self._response_data = None

    def __eq__(self, other):
        if type(other) is type(self):
            # TODO deep equality here?
            return self.__dict__ == other.__dict__
        return False

    @property
    def start_time(self):
        """Start time of the deploy api requested."""
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        self._start_time = start_time

    @property
    def end_time(self):
        """Time of the deploy api responsed for a request."""
        return self._end_time

    @end_time.setter
    def end_time(self, end_time):
        self._end_time = end_time

    @property
    def req_method(self):
        """Http method of the request"""
        return self._req_method

    @req_method.setter
    def req_method(self, req_method):
        self._req_method = req_method

    @property
    def req_url(self):
        """Requested URL"""
        return self._req_url

    @req_url.setter
    def req_url(self, req_url):
        self._req_url = req_url

    @property
    def req_body(self):
        """Requested Data"""
        return self._req_body

    @req_body.setter
    def req_body(self, req_body):
        self._req_body = req_body

    @property
    def status_code(self):
        """Http status code of the deploy api response."""
        return self._status_code

    @status_code.setter
    def status_code(self, status_code):
        self._status_code = status_code

    @property
    def response_data(self):
        """String the deploy api response."""
        return self._response_data

    @response_data.setter
    def response_data(self, response_data):
        self._response_data = response_data

    @classmethod
    def from_proto(cls, proto):
        pass

    def get_logging_param(self):
        """Create and return backend API parameter"""
        import time, json

        if self.start_time is None:
            raise Exception("start_time cannot be None")

        if self.end_time is None:
            raise Exception("end_time cannot be None")

        if self.req_url is None:
            raise Exception("req_url cannot be None")

        if self.req_method is None:
            raise Exception("req_method cannot be None")

        if self.status_code is None:
            raise Exception("status_code cannot be None")

        if self.response_data is None:
            raise Exception("response_data cannot be None")

        data = dict()

        data['createdAt'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(self.start_time)))
        data['endAt'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(self.end_time)))
        data['duration'] = round(self.end_time - self.start_time, 3)
        data['url'] = self.req_url
        data['requestMethod'] = self.req_method
        data['requestBody'] = self.req_body
        data['statusCode'] = self.status_code
        data['response'] = self.response_data

        return json.dumps(data, indent=2)
