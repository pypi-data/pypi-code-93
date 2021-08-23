from .client.Session import TrojSession
from .client.Client import TrojClient
from .data.Loaders import TrojClassificationDataset


def start(id_token=None, refresh_token=None, api_key=None):
    """
    This is the troj package's main function
    Initializes all the classes and saves them under the session superclass for use later

    """
    # Instantiate session super class
    user_session = TrojSession()
    # instantiate client to make and receive requests
    client = TrojClient()
    # instantiate dataset to create a dataframe in the future
    ds = TrojClassificationDataset()
    # use client function to set all credentials
    client.set_credentials(
        id_token=id_token, refresh_token=refresh_token, api_key=api_key
    )
    # associate the subclasses with the session superclass
    user_session.dataset = ds
    user_session.client = client
    # return session superclass
    return user_session
