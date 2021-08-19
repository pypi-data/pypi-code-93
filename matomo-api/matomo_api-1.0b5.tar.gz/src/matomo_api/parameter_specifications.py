"""Classes and functions for specifying url query parameters."""

import urllib.parse


class QryDict(dict):
    """Specialized dictionary to handle api query parameters."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ParameterError(Exception):
    """Raised when the use of a query parameter is incorrect."""
    pass


class idSite:
    """Id's of the sites.

    -----

    Choose method or attribute:

    - `one_or_more(ids)`: to select one or more sites
    - `all`: for all sites, but be cautious in using it
    """
    all = QryDict(idSite='all')

    @staticmethod
    def one_or_more(*ids):
        """One or more sites.

        :param ids: one or more comma separated site id's
            (examples: 5 or 3,7,13)
        :type ids: int
        :return: dictionary to use in API query
        :rtype: QryDict
        """
        for i in ids:
            if type(i) != int:
                raise ParameterError('use integer site id')
        str_nums = [str(i) for i in ids]
        return QryDict(idSite=','.join(str_nums))


class date:
    """Reference date for the API request.

    -----

    Choose attribute or method:

    - `today`
    - `yesterday`
    - `lastWeek` [as of Matomo v4.1]
    - `lastMonth` [as of Matomo v4.1]
    - `lastYear` [as of Matomo v4.1]
    - `last(n)`: n periods, including today
    - `previous(n)`: n periods, excluding today
    - `YMD(date_str)`: specific date or date range
    """

    today = QryDict(date='today')
    yesterday = QryDict(date='yesterday')
    lastWeek = QryDict(date='lastWeek')
    lastMonth = QryDict(date='lastMonth')
    lastYear = QryDict(date='lastYear')

    @staticmethod
    def last(n):
        """Last number of periods.

        :param n: number of periods, including period containing today
        :type n: int
        :return: dictionary to use in API query
        :rtype: QryDict
        """
        return QryDict(date=f'last{n}')

    @staticmethod
    def previous(n):
        """Previous number of periods.

        :param n: number of periods, excluding period containing today
        :type n: int
        :return: dictionary to use in API query
        :rtype: QryDict
        """
        if type(n) != int or n < 0:
            raise ParameterError(
                'use a positive integer to specify number of periods')
        return QryDict(date=f'previous{n}')

    @staticmethod
    def YMD(date_str):
        """Reference date or date range.

        :param date_str: formatted as YYYY-MM-DD or YYYY-MM-DD,YYYY-MM-DD
        :type date_str: str
        :return: dictionary to use in API query
        :rtype: QryDict
        """
        # TODO: add possibility to use keywords, but mind dependence on version
        # TODO: check date or range
        return QryDict(date=date_str)


class period:
    """Date span that contains the specified date.

    -----

    Choose attribute:

    - `day`
    - `week`
    - `month`
    - `year`
    - `range`: sums data for the custom date span
    """
    day = QryDict(period='day')
    week = QryDict(period='week')
    month = QryDict(period='month')
    year = QryDict(period='year')
    range = QryDict(period='range')


class col:
    """Columns of the query result.

    -----

    Choose from the available attributes.
    """
    abandoned_carts = 'abandoned_carts'
    avg_bandwidth = 'avg_bandwidth'
    avg_event_value = 'avg_event_value'
    avg_page_load_time = 'avg_page_load_time'
    avg_price = 'avg_price'
    avg_quantity = 'avg_quantity'
    avg_time_generation = 'avg_time_generation'
    avg_time_on_page = 'avg_time_on_page'
    bounce_count = 'bounce_count'
    bounce_rate = 'bounce_rate'
    conversion_rate = 'conversion_rate'
    date = 'date'
    entry_bounce_count = 'entry_bounce_count'
    entry_nb_actions = 'entry_nb_actions'
    entry_nb_uniq_visitors = 'entry_nb_uniq_visitors'
    entry_nb_visits = 'entry_nb_visits'
    entry_sum_visit_length = 'entry_sum_visit_length'
    exit_bounce_count = 'exit_bounce_count'
    exit_nb_uniq_visitors = 'exit_nb_uniq_visitors'
    exit_nb_visits = 'exit_nb_visits'
    exit_rate = 'exit_rate'
    items = 'items'
    label = 'label'
    max_actions = 'max_actions'
    max_bandwidth = 'max_bandwidth'
    max_event_value = 'max_event_value'
    max_time_generation = 'max_time_generation'
    min_bandwidth = 'min_bandwidth'
    min_event_value = 'min_event_value'
    min_time_generation = 'min_time_generation'
    nb_actions = 'nb_actions'
    nb_conversions = 'nb_conversions'
    nb_downloads = 'nb_downloads'
    nb_events = 'nb_events'
    nb_events_with_value = 'nb_events_with_value'
    nb_hits = 'nb_hits'
    nb_hits_following_search = 'nb_hits_following_search'
    nb_hits_with_bandwidth = 'nb_hits_with_bandwidth'
    nb_hits_with_time_generation = 'nb_hits_with_time_generation'
    nb_keywords = 'nb_keywords'
    nb_outlinks = 'nb_outlinks'
    nb_pages_per_search = 'nb_pages_per_search'
    nb_pageviews = 'nb_pageviews'
    nb_searches = 'nb_searches'
    nb_uniq_downloads = 'nb_uniq_downloads'
    nb_uniq_outlinks = 'nb_uniq_outlinks'
    nb_uniq_pageviews = 'nb_uniq_pageviews'
    nb_uniq_visitors = 'nb_uniq_visitors'
    nb_users = 'nb_users'
    nb_visits = 'nb_visits'
    nb_visits_converted = 'nb_visits_converted'
    orders = 'orders'
    quantity = 'quantity'
    revenue = 'revenue'
    revenue_discount = 'revenue_discount'
    revenue_shipping = 'revenue_shipping'
    revenue_subtotal = 'revenue_subtotal'
    revenue_tax = 'revenue_tax'
    sum_bandwidth = 'sum_bandwidth'
    sum_daily_entry_nb_uniq_visitors = 'sum_daily_entry_nb_uniq_visitors'
    sum_daily_exit_nb_uniq_visitors = 'sum_daily_exit_nb_uniq_visitors'
    sum_daily_nb_uniq_visitors = 'sum_daily_nb_uniq_visitors'
    sum_event_value = 'sum_event_value'
    sum_time_spent = 'sum_time_spent'
    sum_visit_length = 'sum_visit_length'
    url = 'url'


class format:
    """Format of the output.

    -----

    Choose from attributes:

    - `xml`: extensible markup language
    - `json`: javascript object notation
    - `csv`: comma separated values
    - `tsv`: tab separated values
    - `html`: hypertext markup language
    - `rss`: really simple syndication (when date is a range for example
      date=last10)
    """
    xml = QryDict(format='xml')
    json = QryDict(format='json')
    csv = QryDict(format='csv')
    tsv = QryDict(format='tsv')
    html = QryDict(format='html')
    rss = QryDict(format='rss')


class language:
    """Language specification.

    -----

    Choose from the available attributes.
    """
    am = QryDict(language='am')
    ar = QryDict(language='ar')
    be = QryDict(language='be')
    bg = QryDict(language='bg')
    bn = QryDict(language='bn')
    bs = QryDict(language='bs')
    ca = QryDict(language='ca')
    cs = QryDict(language='cs')
    cy = QryDict(language='cy')
    da = QryDict(language='da')
    de = QryDict(language='de')
    el = QryDict(language='el')
    en = QryDict(language='en')
    eo = QryDict(language='eo')
    es_ar = QryDict(language='es-ar')
    es = QryDict(language='es')
    et = QryDict(language='et')
    eu = QryDict(language='eu')
    fa = QryDict(language='fa')
    fi = QryDict(language='fi')
    fr = QryDict(language='fr')
    gl = QryDict(language='gl')
    he = QryDict(language='he')
    hi = QryDict(language='hi')
    hr = QryDict(language='hr')
    hu = QryDict(language='hu')
    id = QryDict(language='id')
    is_ = QryDict(language='is')
    it = QryDict(language='it')
    ja = QryDict(language='ja')
    ka = QryDict(language='ka')
    ko = QryDict(language='ko')
    lt = QryDict(language='lt')
    lv = QryDict(language='lv')
    nb = QryDict(language='nb')
    nl = QryDict(language='nl')
    nn = QryDict(language='nn')
    pl = QryDict(language='pl')
    pt_br = QryDict(language='pt-br')
    pt = QryDict(language='pt')
    ro = QryDict(language='ro')
    ru = QryDict(language='ru')
    sk = QryDict(language='sk')
    sl = QryDict(language='sl')
    sq = QryDict(language='sq')
    sr = QryDict(language='sr')
    sv = QryDict(language='sv')
    ta = QryDict(language='ta')
    te = QryDict(language='te')
    th = QryDict(language='th')
    tl = QryDict(language='tl')
    tr = QryDict(language='tr')
    uk = QryDict(language='uk')
    vi = QryDict(language='vi')
    zh_cn = QryDict(language='zh-cn')
    zh_tw = QryDict(language='zh-tw')


class languageCode:
    """Language specification for the LanguagesManager API Module.

    -----

    Choose from the available attributes.
    """
    am = QryDict(languageCode='am')
    ar = QryDict(languageCode='ar')
    be = QryDict(languageCode='be')
    bg = QryDict(languageCode='bg')
    bn = QryDict(languageCode='bn')
    bs = QryDict(languageCode='bs')
    ca = QryDict(languageCode='ca')
    cs = QryDict(languageCode='cs')
    cy = QryDict(languageCode='cy')
    da = QryDict(languageCode='da')
    de = QryDict(languageCode='de')
    el = QryDict(languageCode='el')
    en = QryDict(languageCode='en')
    eo = QryDict(languageCode='eo')
    es_ar = QryDict(languageCode='es-ar')
    es = QryDict(languageCode='es')
    et = QryDict(languageCode='et')
    eu = QryDict(languageCode='eu')
    fa = QryDict(languageCode='fa')
    fi = QryDict(languageCode='fi')
    fr = QryDict(languageCode='fr')
    gl = QryDict(languageCode='gl')
    he = QryDict(languageCode='he')
    hi = QryDict(languageCode='hi')
    hr = QryDict(languageCode='hr')
    hu = QryDict(languageCode='hu')
    id = QryDict(languageCode='id')
    is_ = QryDict(languageCode='is')
    it = QryDict(languageCode='it')
    ja = QryDict(languageCode='ja')
    ka = QryDict(languageCode='ka')
    ko = QryDict(languageCode='ko')
    lt = QryDict(languageCode='lt')
    lv = QryDict(languageCode='lv')
    nb = QryDict(languageCode='nb')
    nl = QryDict(languageCode='nl')
    nn = QryDict(languageCode='nn')
    pl = QryDict(languageCode='pl')
    pt_br = QryDict(languageCode='pt-br')
    pt = QryDict(languageCode='pt')
    ro = QryDict(languageCode='ro')
    ru = QryDict(languageCode='ru')
    sk = QryDict(languageCode='sk')
    sl = QryDict(languageCode='sl')
    sq = QryDict(languageCode='sq')
    sr = QryDict(languageCode='sr')
    sv = QryDict(languageCode='sv')
    ta = QryDict(languageCode='ta')
    te = QryDict(languageCode='te')
    th = QryDict(languageCode='th')
    tl = QryDict(languageCode='tl')
    tr = QryDict(languageCode='tr')
    uk = QryDict(languageCode='uk')
    vi = QryDict(languageCode='vi')
    zh_cn = QryDict(languageCode='zh-cn')
    zh_tw = QryDict(languageCode='zh-tw')


def segment(spec_str=''):
    """Segment specification.

    -----

    This function handles the necessary url-encoding of the specification
    string, but does not check the validity of it.

    The actual specification should conform to the relevant `segmentation
    documentation <https://developer.matomo.org/api-reference/reporting-api
    -segmentation>`_.

    :param spec_str: segment specification string
    :type spec_str: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(spec_str) != str:
        raise ParameterError('specify the segment using a string')
    return QryDict(segment=urllib.parse.quote(spec_str))


def hideColumns(*cols):
    """Suppress columns from the output.

    -----

    Selected columns will not be included in the query result. Can be used to
    reduce the amount of data transferred.

    :param cols: column names; select from the attributes of the col class
    :type cols: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    columns = []
    for c in cols:
        if type(c) != str or not hasattr(col, c):
            raise ParameterError(
                'use attributes of col class to specify column')
        columns.append(c)
    return QryDict(hideColumns=','.join(columns))


def showColumns(*cols):
    """Set columns of the output.

    -----

    Removes columns that are not selected. Can be used to reduce the amount
    of data transferred.

    :param cols: column names; select from the attributes of the col class
    :type cols: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    columns = []
    for c in cols:
        if type(c) != str or not hasattr(col, c):
            raise ParameterError(
                'use attributes of col class to specify column')
        columns.append(c)
    return QryDict(showColumns=','.join(columns))


def filter_limit(n=10):
    """Filter limit.

    -----

    Defines the number of rows to be returned. If this parameter is omitted
    in the query, the API defaults to the top 100 rows.

    :param n: number of rows (-1 or 'all' for all rows)
    :type n: int|str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(n) == str:
        if n == 'all':
            n = -1
        else:
            raise ParameterError(
                "only 'all' is a valid string for setting the filter_limit")
    elif type(n) != int:
        raise ParameterError(
            "use a positive integer or -1 or 'all' for all rows")
    return QryDict(filter_limit=n)


def idSubtable(idsubdatatable):
    """Set the id of the requested subtable of a given data row.

    -----

    Some data rows are linked to a sub-table. For example, each row in the
    Referrers.getSearchEngines response have an idsubdatatable field. This
    integer idsubdatatable is the idSubtable of the table that contains all
    keywords for this search engine. You can then request the keywords for
    this search engine by calling Referrers.getKeywordsFromSearchEngineId
    with the parameter idSubtable=X (replace X with the idsubdatatable value
    found in the Referrers.getSearchEngines response, for the search engine
    you are interested in).

    :param idsubdatatable: the id of the subtable
    :type idsubdatatable: int
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(idsubdatatable) != int:
        raise ParameterError('specify the id of the subtable using an integer')
    return QryDict(idSubtable=idsubdatatable)


def expanded(true_or_false=True):
    """Expand the query results.

    -----

    In case an API method accepts the `expanded` parameter, it can be used to
    get only the first level results or the related hierarchical data as well.

    :param true_or_false: True to get expanded results
    :type true_or_false: bool
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(true_or_false) != bool:
        raise ParameterError('set this parameter using a boolean')
    return QryDict(expanded=1 if true_or_false else 0)


def flat(true_or_false=True):
    """Get flattened view for expanded query results.

    -----

    In case an API method returns hierarchical results by using the `expanded`
    parameter, the `flat` parameter can be used to keep related data together
    instead of ordering it by hierarchical level. This is useful for example
    to see all Custom Variable names and values at once or to see the full
    URLs not broken down by directory or structure.

    :param true_or_false: True to get flattened results
    :type true_or_false: bool
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(true_or_false) != bool:
        raise ParameterError('set this parameter using a boolean')
    return QryDict(flat=1 if true_or_false else 0)


def format_metrics(true_or_false=True):
    """Get the result set with formatted metrics.

    -----

    Only valid for csv, tsv, rss and html reports.

    :param true_or_false: True to get formatted metrics
    :type true_or_false: bool
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(true_or_false) != bool:
        raise ParameterError('set this parameter using a boolean')
    return QryDict(format_metrics=1 if true_or_false else 0)


def convertToUnicode(utf_16=True):
    """Set the character encoding for the csv and tsv output format.

    -----

    By omitting this parameter in the query, the API defaults to UTF-16LE
    encoding. UTF-8 will be used when specifying a false argument.

    Both encodings support all necessary characters, but UTF-8 is more memory
    efficient.

    :param utf_16: value to use for setting character encoding
    :type utf_16: bool
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(utf_16) != bool:
        raise ParameterError('set this parameter using a boolean')
    return QryDict(convertToUnicode=1 if utf_16 else 0)


def translateColumnNames(true_or_false=True):
    """Get translated column names for the result set.

    -----

    The names will be translated to the language specified by the language
    parameter. Only valid for csv, tsv, rss and html formats.

    :param true_or_false: True to get translated columns
    :type true_or_false: bool
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(true_or_false) != bool:
        raise ParameterError('set this parameter using a boolean')
    return QryDict(translateColumnNames=1 if true_or_false else 0)


def label(label_spec):
    """Set the label to specify the row to be returned.

    -----

    When specified, the report data will be filtered and return only the rows
    of which the label matches the specified parameter. For example, you can
    set 'Nice Keyword' to keep only the row with that label.

    There are also generic filters you can use. Look for parameters starting
    with 'filter_'

    This function handles the necessary url-encoding of the specification
    string, but does not check the validity of it.

    :param label_spec: label specification to select a specific row
    :type label_spec: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(label_spec) != str:
        raise ParameterError('use a string to specify the label')
    return QryDict(label=urllib.parse.quote(label_spec))


def pivotBy(dimension):
    """Set the pivotBy query parameter.

    -----

    This parameter can be used to create a pivot table of a report using a
    specified dimension. Pivoting a report will intersect a report with
    another report and display a single metric for values along two
    dimensions. To pivot a report, this query parameter must be set to the ID
    of the dimension to pivot by. For example, Referrers.Keyword would pivot
    against the Keyword dimension.

    :param dimension: ID of the dimension to pivot by
    :type dimension: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(dimension) != str:
        raise ParameterError('specify dimension using a string')
    return QryDict(pivotBy=dimension)


def pivotByColumn(column):
    """Set the column to display in a pivoted result set.

    -----

    See also the use of the pivotBy parameter.

    :param column: column name; select from the attributes of the col class
    :type column: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(column) != str or not hasattr(col, column):
        raise ParameterError(
            'use attributes of col class to specify column')
    return QryDict(filter_column=column)


def pivotByColumnLimit(cols):
    """Set the maximum number of columns in a pivoted result set.

    -----

    All other columns are aggregated into an 'Others' column.

    :param cols: number of columns
    :type cols: int
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(cols) != int:
        raise ParameterError('specify the number of columns using an integer')
    return QryDict(pivotByColumnLimit=cols)


def filter_offset(n):
    """Set the offset for the first result row to be returned.

    -----

    :param n: number of rows
    :type n: int
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(n) != int:
        raise ParameterError('use an integer to specify offset')
    return QryDict(filter_offset=n)


def filter_truncate(n=10):
    """Truncate the resulting row set.

    -----

    Truncate the result after n rows. The last row will be
    named 'Others' (localized in the requested language) and the columns will
    be an aggregate of statistics of all truncated rows.

    :param n: number of rows
    :type n: int
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(n) != int:
        raise ParameterError('use an integer to specify the number of rows')
    return QryDict(filter_truncate=n)


def filter_pattern(regex):
    """Set the regular expression to filter the results with.

    -----

    Only rows of which the regex matches the filter_column are returned.

    :param regex: regular expression string
    :type regex: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(regex) != str:
        raise ParameterError('use a string to specify the regular expression')
    return QryDict(filter_pattern=regex)


def filter_column(column=col.label):
    """Set the column related to the filter_pattern parameter.

    -----

    Defines the column to be used when filter_pattern is used to filter the
    output rows. If this parameter is omitted in the query, the API defaults
    to 'label'.

    :param column: column name; select from the attributes of the col class
    :type column: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(column) != str or not hasattr(col, column):
        raise ParameterError(
            'use attributes of col class to specify column')
    return QryDict(filter_column=column)


def filter_sort_order(order_asc=True):
    """Set the sorting order for the result set.

    -----

    defines the order with which the resulting rows will be sorted. See also
    the filter_sort_column parameter

    :param order_asc: ascending when true, descending otherwise
    :type order_asc: bool
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(order_asc) != bool:
        raise ParameterError('set this parameter using a boolean')
    return QryDict(filter_sort_order='asc' if order_asc else 'desc')


def filter_sort_column(column):
    """Set the column to sort the results with.

    -----

    Defines the column to be used to sort the output rows.

    :param column: column name; select from the attributes of the col class
    :type column: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(column) != str or not hasattr(col, column):
        raise ParameterError(
            'use attributes of col class to specify column')
    return QryDict(filter_sort_column=column)


def filter_excludelowpop(column):
    """Set the column to use for a threshold.

    -----

    Defines the column to be used when a threshold is set to limit the
    resulting rows (see the filter_excludelowpop_value parameter). Only the
    columns with a value greater than that threshold will be returned.

    :param column: column name; select from the attributes of the col class
    :type column: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(column) != str or not hasattr(col, column):
        raise ParameterError(
            'use attributes of col class to specify column')
    return QryDict(filter_excludelowpop=column)


def filter_excludelowpop_value(threshold):
    """Set threshold value to limit the set of returned rows.

    -----

    The column to be used for this threshold is set by using the
    filter_excludelowpop parameter. Only the columns with a value greater
    than the threshold value will be returned.

    :param threshold: minimum value to be included in result set
    :type threshold: int
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(threshold) != int:
        raise ParameterError('threshold should be set using an integer')
    return QryDict(filter_excludelowpop_value=threshold)


def filter_column_recursive(column=col.label):
    """Set the column related to the filter_pattern_recursive parameter.

    -----

    Defines the column to be used when filter_pattern_recursive is used to
    filter the output rows.

    :param column: column name; select from the attributes of the col class
    :type column: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(column) != str or not hasattr(col, column):
        raise ParameterError(
            'use attributes of col class to specify column')
    return QryDict(filter_column_recursive=column)


def filter_pattern_recursive(regex):
    """Set the regular expression to recursively filter the results with.

    -----

    Only matching row are returned.

    This filter is applied to recursive tables (actions, downloads and
    outlinks tables) including any subtables.

    :param regex: regular expression string
    :type regex: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(regex) != str:
        raise ParameterError('use a string to specify the regular expression')
    return QryDict(filter_pattern_recursive=regex)


def disable_generic_filters(true_or_false=True):
    """Disable all generic filters.

    -----

    Even the filters that are not explicitly set and thus fall back to their
    respective defaults.

    Primarily used for internal purposes and when developing plugins.

    :param true_or_false: true to disable
    :type true_or_false: bool
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(true_or_false) != bool:
        raise ParameterError('set this parameter using a boolean')
    return QryDict(disable_generic_filters=1 if true_or_false else 0)


def disable_queued_filters(true_or_false=True):
    """Disable all queued filters.

    -----

    All filters that are mostly presentation filters (replace a column
    name, apply callbacks on the column to add new information such as the
    browser icon URL, etc.) will not be applied.

    Primarily used for internal purposes and when developing plugins.

    :param true_or_false: true to disable
    :type true_or_false: bool
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(true_or_false) != bool:
        raise ParameterError('set this parameter using a boolean')
    return QryDict(disable_queued_filters=1 if true_or_false else 0)


def pageUrl(url):
    """Sets the full page url for a query.

    :param url: complete and valid url
    :type url: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(url) != str:
        raise ParameterError('set this parameter using a string')
    return QryDict(pageUrl=url)


def idCustomReport(crid):
    """Specifies a custom report in the Methods of the CustomReport API Module.

    :param crid: the id of the custom report
    :type crid: int
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(crid) != int:
        raise ParameterError('set this parameter using an integer')
    return QryDict(idCustomReport=crid)


def idDashboard(dbid):
    """Specifies a user dashboard in the Methods of the Dashboard API Module.

    :param dbid: the id of the dashboard
    :type dbid: int
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(dbid) != int:
        raise ParameterError('set this parameter using an integer')
    return QryDict(idDashboard=dbid)


def login(uid):
    """Sets the user id for a query.

    :param uid: user id
    :type uid: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(uid) != str:
        raise ParameterError('set this parameter using a string')
    return QryDict(login=uid)


def userLogin(uid):
    """Sets the user login id for a query.

    :param uid: user id
    :type uid: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(uid) != str:
        raise ParameterError('set this parameter using a string')
    return QryDict(userLogin=uid)


def copyToUser(uid):
    """Sets the user id to receive a copy of a dashboard.

    :param uid: user id
    :type uid: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(uid) != str:
        raise ParameterError('set this parameter using a string')
    return QryDict(copyToUser=uid)


def dashboardName(db_name):
    """Sets the name for a dashboard to copy or create.

    :param db_name: name for the dashboard
    :type db_name: str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(db_name) != str:
        raise ParameterError('set this parameter using a string')
    return QryDict(dashboardName=db_name)


def par_val(name, value):
    """Set a parameter to a value.

    -----

    Use this function to specify a parameter for which there is no specific
    class or function.

    :param name: name of the query parameter
    :type name: str
    :param value: value for the parameter
    :type value: int | str
    :return: dictionary to use in API query
    :rtype: QryDict
    """
    if type(name) != str:
        raise ParameterError('use a string to specify the parameter name')
    if type(value) not in (str, int):
        raise ParameterError('parameter value should be string or integer')
    return QryDict([(name, value)])
