import os
from urllib.parse import unquote_plus
import boto3
import s3fs

fs = s3fs.S3FileSystem()


def move_object(destination_bucket: str, source_bucket: str, source_key: str):
    """The function will copy the object in S3 to the "destination_bucket" bucket,
    while adding a timestamp to the filename. It will then
    delete the original object from "source_bucket".
    Parameters
    ----------
    destination_bucket : str
        The bucket where the S3 object will be copied to.
    source_bucket : str
        The bucket where the S3 object is.
    source_key : str
        The object S3 key.
    """
    client = boto3.client("s3")

    client.copy_object(
        Bucket=destination_bucket,
        CopySource={"Bucket": source_bucket, "Key": source_key},
        Key=source_key,
        ServerSideEncryption="AES256",
        ACL="bucket-owner-full-control",
    )
    client.delete_object(Bucket=source_bucket, Key=source_key)


class EmptyFileError(Exception):
    """Raised when the file opened has no contents"""

    pass


class FileValidator:
    """
    A class to validate data in the Land-to-History pipeline. Currently
    merely checks that the file can be opened, and contains a non-zero
    amount of bytestream content. If both conditions are met, it moves
    to the pass bucket, otherwise moves the object to the fail bucket.
    Attributes
    ----------
    key : str
        The AWS S3 key of the file being validated.
    pass_bucket : str
        The name of the bucket for files that pass validation.
    fail_bucket : str
        The name of the bucket for files that fail validation.
    source_bucket : str
        The name of the bucket that contains the file being validated.
    """

    def __init__(
        self,
        key: str,
        pass_bucket: str,
        fail_bucket: str,
        source_bucket: str,
    ):
        """
        Parameters
        ----------
        key : str
            The AWS S3 key of the file being validated.
        pass_bucket : str
            The name of the bucket for files that pass validation.
        fail_bucket : str
            The name of the bucket for files that fail validation.
        source_bucket : str
            The name of the bucket that contains the file being validated.
        """
        self.key = key
        self.fail_bucket = fail_bucket
        self.pass_bucket = pass_bucket
        self.source_bucket = source_bucket
        self.errors = []

    def _add_error(self, error: str):
        """Collects and aggregates error messges into a list.
        Parameters
        ----------
        error : str
            An error message
        """
        if error not in self.errors:
            self.errors.append(error)

    def _validate_file(self, path, fs=fs):
        """
        Parameters
        ----------
        path : [type]
            The file path to the file to be validated.
        """
        open_function = fs.open if fs is not None else open
        with open_function(path, mode="rb") as source:
            try:
                self.file = source
                if len(self.file.read()) < 1:
                    raise EmptyFileError("File has no content")
            except Exception as e:
                self._add_error(error=str(e))
                return

    def execute(self):
        self._validate_file(path=f"{self.source_bucket}/{self.key}")
        if len(self.errors) > 0:
            move_object(
                destination_bucket=self.fail_bucket,
                source_bucket=self.source_bucket,
                source_key=self.key,
            )
            return {"validation_outcome": "Fail"}
        else:
            move_object(
                destination_bucket=self.pass_bucket,
                source_bucket=self.source_bucket,
                source_key=self.key,
            )
            return {"validation_outcome": "Pass"}


def handler(event, context):
    for record in event["Records"]:
        source_bucket = record["s3"]["bucket"]["name"]
        pass_bucket = os.environ["PASS_BUCKET"]
        fail_bucket = os.environ["FAIL_BUCKET"]
        key = unquote_plus(record["s3"]["object"]["key"])

        fileValidator = FileValidator(
            key=key,
            pass_bucket=pass_bucket,
            fail_bucket=fail_bucket,
            source_bucket=source_bucket,
        )

        fileValidator.execute()
