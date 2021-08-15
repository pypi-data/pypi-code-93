#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

class EnricherError(Exception):
    pass


class Enricher(object):
    version = "0.0.1"

    def __init__(self,
                 scene_engine_client):

        self.scene_engine_client = scene_engine_client

    def enrich(self, metadata: dict) -> dict:
        pass
