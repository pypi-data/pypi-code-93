import io
import json
from typing import Any

from komolibs.aws.s3.s3_base import S3Base


class Download(S3Base):
    def __init__(self, access_key: str, access_secret: str, region: str):
        super().__init__(access_key, access_secret, region)

    def download(self, bucket: str, file_name: str) -> Any:
        try:
            s3_object = self.resource.Object(bucket, file_name)
            data = io.BytesIO()
            s3_object.download_fileobj(data)

            # object is now a bytes string, Converting it to a dict:
            return json.loads(data.getvalue().decode("utf-8"))

        except Exception as e:
            raise e
