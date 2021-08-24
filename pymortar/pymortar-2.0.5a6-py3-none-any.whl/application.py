import toml
from functools import cached_property

class Application:
    def __init__(self, filename, client):
        self.spec = toml.load(open(filename))
        self.queries = self.spec["queries"]
        self.name = self.spec["name"]
        self.client = client

    @cached_property
    def valid_sites(self):
        self.refresh_valid_sites()

    def refresh_valid_sites(self):
        df = self.client.qualify(self.queries).df
        sites = list(df[df.all(axis=1)].index)
        return sites
