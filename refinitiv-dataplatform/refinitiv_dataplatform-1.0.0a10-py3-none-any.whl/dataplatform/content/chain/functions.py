# coding: utf-8

__all__ = ["get_chain", "get_chain_async"]

###############################################################
#
#   STANDARD IMPORTS
#


###############################################################
#
#   REFINITIV IMPORTS
#

from .chain import Chain


###############################################################
#
#   LOCAL IMPORTS
#

###############################################################
#
#   FUNCTIONS
#


def get_chain(universe):
    """
    Call synchronous a decode chain with given universe parameter

    Parameters
    ----------
    universe: str
        The chain record name to decode ie. 0#.DJI or .AV.O

    Returns
    -------
    DataFrame
        The response object from given chain name parameters
    None

    """
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    response = Chain.decode(universe=universe)

    ContentFactory._last_result = response
    if response.is_success and response.data and response.data.df is not None:
        return response.data.df
    else:
        ContentFactory._last_error_status = response.status
        return None


async def get_chain_async(universe, on_response=None, session=None):
    """
    Call synchronous a decode chain with given universe parameter

    Parameters
    ----------
    universe: str
        The chain record name to decode ie. 0#.DJI or .AV.O
    on_response: object, optional
        A callback legacy when response from decoding chain requested, default: None
    session: object, optional
        The session for calling a decoding chain, default: default session

    Returns
    -------
    DataFrame
        The response object from given chain parameters
    None

    """
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    response = await Chain.decode_async(
        universe=universe, session=session, on_response=on_response
    )

    ContentFactory._last_result = response
    if response.is_success and response.data and response.data.df is not None:
        return response.data.df
    else:
        ContentFactory._last_error_status = response.status
        return None
