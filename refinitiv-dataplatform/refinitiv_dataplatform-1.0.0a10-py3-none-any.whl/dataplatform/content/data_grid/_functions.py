# coding: utf8


__all__ = ["get_data"]

from ._fundamental_class import Fundamental


def get_data(
    universe,
    fields,
    parameters=None,
    field_name=None,
):
    """
    Returns a pandas.DataFrame with fields in columns and instruments as row index

    Parameters
    ----------
    universe: string or list
        Single instrument or list of instruments to request.

    fields: string, dictionary or list of strings and/or dictionaries.
        List of fields to request.

        Examples:

        - 'TR.PriceClose'
        - {'TR.GrossProfit': { 'params':{ 'Scale': 6, 'Curn': 'EUR' }}
        - {'TR.GrossProfit': { 'params':{ 'Scale': 6, 'Curn': 'EUR' },sort_dir:'desc'}
        - ['TR.PriceClose','TR.PriceOpen']
        - [{'TR.PriceClose':  {'sort_dir':asc,sort_priority:1}},{'TR.PriceOpen':  {'sort_dir':asc,sort_priority:0}}

        You can use the legacy TR_Field to build the fields:

        >>> fields = [ek.TR_Field('tr.revenue'),ek.TR_Field('tr.open','asc',1),ek.TR_Field('TR.GrossProfit',{'Scale': 6, 'Curn': 'EUR'},'asc',0)]
        >>> data, err = ek.get_data(["IBM","MSFT.O"],fields)

        Tips:
        You can launch the Data Item Browser to discover fields and parameters,
        or copy field names and parameters from TR Eikon - MS Office formulas

    parameters: string or dictionary, optional
        Single global parameter key=value or dictionary of global parameters to request.

        Default: None

    field_name: boolean, optional
        Define if column headers are filled with field name or display names.

        If True value, field names will ube used as column headers. Otherwise, the full display name will be used.

        Default: False

    Returns
    -------
    pandas.DataFrame
        Returns pandas.DataFrame with fields in columns and instruments as row index

        errors
            Returns a list of errors

    Raises
    ----------
        Exception
            If http request fails or if server returns an error.

        ValueError
            If a parameter type or value is wrong.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> data = rdp.get_data(["IBM", "GOOG.O", "MSFT.O"], ["TR.PriceClose", "TR.Volume", "TR.PriceLow"])
    >>> data = rdp.get_data("IBM", ['TR.Employees', {'TR.GrossProfit':{'params':{'Scale': 6, 'Curn': 'EUR'},'sort_dir':'asc'}}])
    >>> fields = [rdp.TR_Field('tr.revenue'),rdp.TR_Field('tr.open',None,'asc',1),rdp.TR_Field('TR.GrossProfit',{'Scale': 6, 'Curn': 'EUR'},'asc',0)]
    >>> data = rdp.get_data(["IBM","MSFT.O"], fields)
    """

    result = Fundamental.get_data(
        universe=universe,
        fields=fields,
        parameters=parameters,
        field_name=field_name,
    )
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = result.status
        retval = None

    ContentFactory._last_result = result

    return retval
