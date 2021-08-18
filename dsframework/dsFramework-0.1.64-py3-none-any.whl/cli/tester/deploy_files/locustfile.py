from locust import HttpUser, task
import pandas as pd
import numpy as np

from server.token_generator import tokenGenerator

j = tokenGenerator()
jwtToken = j.generateToken('DEFAULT_Conf')
global_headers = {
    'x-token': 'fake-super-secret-token',
    'Authorization': 'Bearer ' + jwtToken
}

class payloadUser(HttpUser):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.df = pd.read_csv("sample.csv", sep='\t')
		self.df.replace(np.nan, '', regex=True)

	def get_random_row(self):
		s = self.df.sample().to_dict('list')
		d = dict((k.lower(), v[0]) for k, v in s.items())
		return d

	@task
	def get_diagnosis_with_valid_payload(self):
		headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
		payload = self.get_random_row()
		self.client.post("/predict", json=payload, headers=headers)


# how to run
# --host - Host to load test in the following format: http://example.com
# --users - Number of concurrent Locust users
# --spawn-rate - The rate per second in which users are spawned
# locust -f locustfile.py --host={your-host} --users={number-of-users} --spawn-rate={your-spawn-rate}
