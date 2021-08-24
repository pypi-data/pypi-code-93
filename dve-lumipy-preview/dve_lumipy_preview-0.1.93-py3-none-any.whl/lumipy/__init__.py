from lumipy.navigation.atlas import Atlas
from lumipy.client import Client
from lumipy.drive.drive import Drive
from typing import Optional
from functools import reduce

from lumipy.query.expression.table_op.row_set_op import RowSetOp
from lumipy.query.expression.variable.scalar_variable import DateScalar
from lumipy.query.expression.variable.scalar_variable import DateTimeScalar


def get_client(secrets: Optional[str] = None, token: Optional[str] = None) -> Client:
    """Get luminesce web API client instance.

    Args:
        secrets (Optional[str]): path to secrets file. If not supplied authentication information will be retrieved
        from the environment.
        token (Optional[str]): authentication token.

    Returns:
        Client: the web API client instance.
    """
    return Client(secrets, token)


def get_atlas(secrets: Optional[str] = None, token: Optional[str] = None) -> Atlas:
    """Get luminesce data provider atlas instance.

    Args:
        secrets (Optional[str]): path to secrets file. If not supplied authentication information will be retrieved
        from the environment.
        token (Optional[str]): authentication token.

    Returns:
        Atlas: the atlas instance.
    """
    return Client(secrets, token).get_atlas()


def get_drive(secrets: Optional[str] = None, token: Optional[str] = None) -> Drive:
    """Get drive instance.

    Args:
        secrets (Optional[str]): path to lumipy secrets file. If not supplied authentication information will be
        retrieved from the environment.
        token (Optional[str]): authentication token.

    Returns:
        Drive: the drive instance.
    """
    atlas = get_atlas(secrets, token)
    return Drive(atlas)


def datetime_now(delta_days: Optional[int] = 0) -> DateTimeScalar:
    """Get a scalar variable representing the current date with an optional offset.

    Args:
        delta_days (Optional[int]): time delta in days. Defaults to 0.

    Returns:
        DateTimeScalar: Datetime scalar variable expression.
    """
    return DateTimeScalar('now', delta_days)


def date_now(delta_days: Optional[int] = 0) -> DateScalar:
    """Get a scalar variable representing the current datetime with an optional offset.

    Args:
        delta_days (Optional[int]): time delta in days. Defaults to 0.

    Returns:
        DateScalar: Date scalar variable expression.
    """
    return DateScalar('now', delta_days)


def concat(sub_qrys, filter_duplicates=True) -> RowSetOp:
    """Vertical concatenation of subqueries. This is the lumipy equivalent of pandas.concat()

    Args:
        sub_qrys:
        filter_duplicates:

    Returns:
        RowSetOp: object representing the union of all the subqueries.
    """
    if filter_duplicates:
        return reduce(lambda x, y: x.union(y), sub_qrys)
    else:
        return reduce(lambda x, y: x.union_all(y), sub_qrys)
