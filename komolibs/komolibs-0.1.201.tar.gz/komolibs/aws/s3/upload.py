import json

from komolibs.aws.s3.s3_base import S3Base, S3Result


class Upload(S3Base):
    def __init__(self):
        super().__init__()

    def upload(self, data: dict, file_name: str, bucket: str) -> S3Result:
        try:
            s3_object = self.resource.Object(bucket, file_name)
            text = json.dumps(data)
            result = s3_object.put(Body=text)
            response = result.get('ResponseMetadata')
            if response.get('HTTPStatusCode') in [200, 201]:
                self.logger().info('File Uploaded Successfully. ')
                return S3Result.SUCCESS
            else:
                self.logger().error(f'File Not Uploaded. {response.get("HTTPStatusCode")}')
                return S3Result.FAILURE
        except Exception as e:
            raise e