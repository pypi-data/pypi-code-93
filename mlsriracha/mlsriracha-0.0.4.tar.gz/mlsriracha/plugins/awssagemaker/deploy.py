import os

from mlsriracha.interfaces.deploy import DeployInterface

class AwsSageMakerDeploy(DeployInterface):

    def __init__(self):
        print('Selected AWS SageMaker profile')

    def model_artifact(self, filename: str):
        """
        The path to model artifacts.

        Your algorithm should read all the model artifacts from this directory.
        Amazon SageMaker copies this data as a single object in a compressed tar
        format from the S3 location that you specified in the CreateModel config
        request. If multiple containers in a single training job write to this
        directory they should ensure no file/directory names clash. Amazon SageMaker
        mounts the S3 for the user.

        Arguments:
            filename (str): The name of the file which will be written back to S3

        Returns:
            path (str): The absolute path to the model output directory
        """
        return os.path.join(os.sep, 'opt', 'ml', 'model', filename)

    def endpoint_metadata(self):
        return {}