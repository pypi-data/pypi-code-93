import io
import json
import pandas as pd
from mitosheet.mito_analytics import log
from mitosheet.sheet_functions.types.utils import get_mito_type, NUMBER_SERIES
import plotly.express as px
import plotly.graph_objects as go
import sys # In order to print in this file use sys.stdout.flush() once after the print statements.

# We have a variety of heuristics to make sure that we never send too much data
# to the frontend to display to the user. See comments below in the file for 
# which heuristics we use. They use the following constants 

# Graph types should be kept consistent with the GraphType in GraphSidebar.tsx
SCATTER = 'scatter'
BAR = 'bar'
HISTOGRAM = 'histogram'
BOX = 'box'
SUMMARY_STAT = 'summary_stat'

# Max number of unique non-number items to display in a graph
# NOTE: make sure to change both in unison so they make sense
MAX_UNIQUE_NON_NUMBER_VALUES = 10_000
MAX_UNIQUE_NON_NUMBER_VALUES_COMMENT = '(Top 10k)'

SCATTER_PLOT_LESS_THAN_4_SERIES_MAX_NUMBER_OF_ROWS = 10_000
SCATTER_PLOT_4_SERIES_MAX_NUMBER_OF_ROWS = 5_000
BAR_CHART_MAX_NUMBER_OF_ROWS = 5_000
BOX_PLOT_3_SERIES_MAX_NUMBER_OF_ROWS = 500_000
BOX_PLOT_4_SERIES_MAX_NUMBER_OF_ROWS = 250_000

# On the key axis, the difference between the minimum value and the maximum
# value initially displayed on the graph can be no larger than STARTING_RANGE_RANGE
# for qualifying graphs. Only scatter plots and bar charts with a key series that is 
# a number have the default starting range updated. 
STARTING_RANGE_MAX_RANGE = 500

# Labels used to show that the graph is filtered. 
# Used both in the graph_title and the title.
# Note: Because box plot filtering is more complicated, we don't 
# have a graph_filter_label for it
GRAPH_FILTER_LABELS = {
    SCATTER: '(first 10k)',
    BAR: '(first 5k)',
    HISTOGRAM: '(all data)'
}

# Label for each type of graph used in the graph title
GRAPH_TITLE_LABELS = {
    SCATTER: 'scatter plot',
    BAR: 'bar chart',
    BOX: 'box plot',
    HISTOGRAM: 'histogram'
}

# Some, uh, constants that are nice
X = 'x'
Y = 'y'

def is_all_number_series(df, column_headers):
    """
    Returns True if the mito type of each series with the header column_header
    in column_headers is a NUMBER_SERIES. Returns False otherwise. 
    """
    for column_header in column_headers:
        mito_type = get_mito_type(df[column_header])
        if mito_type != NUMBER_SERIES:
            return False
    return True

def get_graph_title (x_axis_column_headers, y_axis_column_headers, filtered, graph_type, special_title=None):
    """
    Helper function for determing the title of the graph for the scatter plot and bar chart
    """
    # Get the label to let the user know that their graph had a filter applied.

    # Handle the special case for the box plot.
    if graph_type == BOX and filtered:
        graph_filter_label = '(top 500k)' if len(x_axis_column_headers + y_axis_column_headers) == 3 else '(top 250k)'
    # Handle the special case for the scatter plot.
    elif graph_type == SCATTER and filtered:
        graph_filter_label = '(first 10k)' if len(x_axis_column_headers + y_axis_column_headers) < 4 else '(first 5k)'
    else:
        graph_filter_label = GRAPH_FILTER_LABELS[graph_type] if filtered else None

    # Compile all of the column headers into one comma separated string
    all_column_headers = (', ').join(x_axis_column_headers + y_axis_column_headers)
    # Get the title of the graph based on the type of graph
    graph_title_label = GRAPH_TITLE_LABELS[graph_type] if special_title is None else special_title
    # Combine all of the non empty graph title components into one list
    graph_title_components = [all_column_headers, graph_filter_label, graph_title_label] if graph_filter_label is not None else [all_column_headers, graph_title_label]
    
    # Return a string with all of the graph_title_components separated by a space  
    return (' ').join(graph_title_components)


def get_graph_labels(x_axis_column_headers, y_axis_column_headers):
    """
    Helper function for determining the x and y axis titles, 
    for the scatter plot and bar chart. 
    """
    if x_axis_column_headers == [] and y_axis_column_headers == []:
        # If no data is provided, don't label the axises
        x_axis_title = ''
        y_axis_title = ''

    elif x_axis_column_headers == [] and y_axis_column_headers != []:
        # Following from the graph generation, if the user only selects a y axis, 
        # then the y axis is the index column and the columns selected are put on the x axis
        x_axis_title = y_axis_column_headers[0] if len(y_axis_column_headers) == 1 else ''
        y_axis_title = 'index'

    elif x_axis_column_headers != [] and y_axis_column_headers == []:
        # Following from the graph generation, if the user only selects a x axis, 
        # then the y axis is the index column
        x_axis_title = 'index'
        y_axis_title = x_axis_column_headers[0] if len(x_axis_column_headers) == 1 else ''

    else: 
        # Only label the axis if there is one column header on the axis. Otherwise, plotly 
        # legend will label the columns
        x_axis_title = x_axis_column_headers[0] if len(x_axis_column_headers) == 1 else ''
        y_axis_title = y_axis_column_headers[0] if len(y_axis_column_headers) == 1 else ''

    return x_axis_title, y_axis_title

def get_starting_ranges(graph_type, df, x_axis_column_headers, y_axis_column_headers):
    """
    Helper function for determing range that the axis should default to on 
    inital render. It finds the smallest value in the key series and sets the range of it
    [smallest value in series, smallest value in series + STARTING_RANGE_RANGE]

    It returns the object {
        X: [start of range, end of range] or [None, None]
        Y: [start of range, end of range] or [None, None]
    }

    At least one of the axises will be [None, None]
    
    In the following conditions, this function will return a range of [None, None] so 
    as to not overwrite the plotly default:
    1. the graph type is not a scatter plot or a bar chart.
    2. the key series is not a NUMBER_SERIES.
    3. the range of the key series is already less than STARTING_RANGE_RANGE.

    This approach is used to avoid graphs rendering where the data is nearly invisible due to the 
    range of the key axis being so large
    """
    if (graph_type != SCATTER and graph_type != BAR) or (x_axis_column_headers == [] and y_axis_column_headers == []):
        # We only need to overwrite the default range in scatter plots and bar charts. 
        # We also don't care about the case where the graph has no data.
        return {
            X: [None, None],
            Y: [None, None]
        } 

    elif len(x_axis_column_headers) == 0 and len(y_axis_column_headers) > 0:
        key_axis = Y
        # Since the user has no way of zooming in/out the y axis, we regretably 
        # don't start the graph zoomed in because they will be stuck there!
        return {
            X: [None, None],
            Y: [None, None]
        } 

    elif len(x_axis_column_headers) > 0 and len(y_axis_column_headers) == 0:
        # In this case the x axis is the key axis and it is the index series. 
        # Because the index series is always a number, we don't have to do the 
        # mito_type_check and we just make sure that there are more than 
        # DEFAULT_RANGE rows. 
        key_axis = X
        return {
            X: [0, STARTING_RANGE_MAX_RANGE] if len(df) > STARTING_RANGE_MAX_RANGE else [None, None],
            Y: [None, None]
        }

    else: 
        key_axis = X if len(x_axis_column_headers) == 1 else Y
        key_series = df[x_axis_column_headers[0]] if key_axis == X else df[y_axis_column_headers[0]]

        # If the series is not a number series, we give up on creating
        # a heuristic for setting the x axis 
        # TODO: Figure out if we can set the range as a list of the first 500 unique values
        # Think about whether the order of the unique values in the chart matters. 
        if get_mito_type(key_series) != NUMBER_SERIES:
            return {
                X: [None, None],
                Y: [None, None]
            } 

        # Learn about the range of the key series to make decision
        # about how we should set the default range of the graph
        min_value_in_series = key_series.min()
        max_value_in_series = key_series.max()

        if max_value_in_series - min_value_in_series > STARTING_RANGE_MAX_RANGE:
            # If the range of the series is greater than STARTING_RANGE_RANGE, then 
            # set the starting range from the min_value_in_series to min_value_in_series + STARTING_RANGE_RANGE
            return {
                X: [min_value_in_series, min_value_in_series + STARTING_RANGE_MAX_RANGE] if key_axis == X else [None, None],
                Y: [None, None] # the Y axis is never set zoomed in because the user has no way of zooming out
            }
        else:
            # If the range of the series is less than STARTING_RANGE_RANGE, 
            # don't overwrite plotly's default range
            return {
                X: [None, None],
                Y: [None, None]
            } 

def filter_df_to_top_unique_values_in_series(
        df: pd.DataFrame,
        main_series: pd.Series,
        num_unique_values: int,
    ) -> pd.Series: 
    """
    Helper function for filtering the dataframe down to the top most common
    num_unique_values in the main_series. Will not change the series if there are less
    values than that.

    The function filters the entire dataframe to make sure that the columns stay 
    the same length (which is necessary if you want to graph them).

    It returns the filtered dataframe
    """
    if len(main_series) < num_unique_values or main_series.nunique() < num_unique_values:
        return df

    value_counts_series = main_series.value_counts()
    most_frequent_values_list = value_counts_series.head(n=num_unique_values).index.tolist()

    return df[main_series.isin(most_frequent_values_list)]

def get_html_and_script_from_figure(fig, height, width):
    """
    Given a plotly figure, generates HTML from it, and returns
    a dictonary with the div and script for the frontend.

    The plotly HTML generated by the write_html function call is a div with two children:
    1. a div that contains the id for the graph itself
    2. a script that actually builds the graph
    
    Because we have to dynamically execute the script, we split these into two 
    strings, to make them easier to do what we need on the frontend
    """
    # Send the graph back to the frontend
    buffer = io.StringIO()
    fig.write_html(
        buffer,
        full_html=False,
        include_plotlyjs=False,
        default_height=height,
        default_width=width,
    )
    
    original_html = buffer.getvalue()
    # First, we remove the main div, and the resulting whitespace, to just have the children
    original_html = original_html[5:]
    original_html = original_html[:-6]
    original_html = original_html.strip()

    # Then, we split the children into the div, and the script 
    # making sure to remove the script tag (so we can execute it)
    script_start = '<script type=\"text/javascript\">'
    script_end = '</script>'
    split_html = original_html.split(script_start)
    div = split_html[0]
    script = split_html[1][:-len(script_end)]

    return {
        'html': div,
        'script': script
    }

def get_bar_chart(df, x_axis_column_headers, y_axis_column_headers):
    """
    Returns a bar chart using the following heuristic:
    - Graphs the first BAR_CHART_MAX_NUMBER_OF_ROWS rows. 

    If only one axis has data, then we create a histogram instead. 

    If at leastat least the x_axis_column_headers or y_axis_column_headers 
    has at least one series, then it returns a bar chart. Otherwise, it returns 
    a blank graph.
    """
    original_length_of_df = len(df)

    x_axis = True if x_axis_column_headers != [] else False
    y_axis = True if y_axis_column_headers != [] else False
    
    # If no data is passed, return a blank graph
    if not x_axis and not y_axis:
        # This should never happen because this check already occurs in the get_graph
        # function. But we leave it here for robustness of the function
        return go.Figure(), False

    # If only one axis is supplied, then we create a histogram instead of a bar chart 
    # because it is more informative to show the counts of each value instead of graphing 
    # the values by index. 
    if x_axis and not y_axis:
        return get_histogram(X, df, x_axis_column_headers)
    elif y_axis and not x_axis:
        return get_histogram(Y, df, y_axis_column_headers)

    # If both axises are supplied, then we go on to create the bar chart. 
    # Start by sorting the key column in decreasing frequency so we can filter 
    # dataframe according to the bar chart filtering strategy. 
    if len(y_axis_column_headers) == 1:
        df['Frequency'] = df.groupby(y_axis_column_headers[0])[y_axis_column_headers[0]].transform('count')
    else:
        df['Frequency'] = df.groupby(x_axis_column_headers[0])[x_axis_column_headers[0]].transform('count')

    df = df.sort_values('Frequency', inplace=False, ascending=False)

    # Take the top BAR_CHART_MAX_NUMBER_OF_ROWS rows of the sorted dataframe
    df = df.head(BAR_CHART_MAX_NUMBER_OF_ROWS)

    # Determine if the dataframe was sorted
    filter_label = GRAPH_FILTER_LABELS[BAR] if len(df) < original_length_of_df else ''
    filtered = len(df) < original_length_of_df

    # Construct the traces for the graph. Note: For some reason that I do not understand, 
    # for bar plots, the traces need to be added when initially creating the bar chart, 
    # unlike the other types of graphs where we can use the add_trace function.
    traces = []

    # If the y_axis has __exactly__ one series and the x_axis has __at least__ one series (covered by above checks)
    if len(y_axis_column_headers) == 1:
        for column_header in x_axis_column_headers:
            traces.append(
                go.Bar( 
                    x = df[column_header],
                    y = df[y_axis_column_headers[0]],
                    name=(' ').join([column_header, filter_label])
                )
            )
    # If the y_axis has > one series and the x_axis has __at least__ one series (covered by above checks)
    else: 
        for column_header in y_axis_column_headers:
            traces.append(
                go.Bar( 
                    x = df[x_axis_column_headers[0]],
                    y = df[column_header],
                    name=(' ').join([column_header, filter_label])
                )
            )
    
    fig = go.Figure(data=traces)

    # Update the layout of the graph
    x_axis_title, y_axis_title = get_graph_labels(x_axis_column_headers, y_axis_column_headers)
    graph_title = get_graph_title(x_axis_column_headers, y_axis_column_headers, filtered, BAR)
    fig.update_layout(
        xaxis_title = x_axis_title,
        yaxis_title = y_axis_title,
        title = graph_title,
        barmode='group',
    )

    # Update the starting range of the graph
    ranges = get_starting_ranges(BAR, df, x_axis_column_headers, y_axis_column_headers)
    fig.update_layout(
        xaxis=dict(
            range=ranges[X]
        ), 
        yaxis=dict(
            range=ranges[Y]
        )
    )
    # Determine if the graph was zoomed in
    is_zoomed = ranges[X][0] is not None or ranges[X][1] or ranges[Y][0] is not None or ranges[Y][1] is not None

    log(f'generate_graph', {
        'params_graph_type': BAR,
        'params_x_axis_column_headers': x_axis_column_headers,
        'params_x_axis_column_types': [get_mito_type(df[column_header]) for column_header in x_axis_column_headers] if x_axis_column_headers is not None else [],
        'params_y_axis_column_headers': y_axis_column_headers,
        'params_y_axis_column_types': [get_mito_type(df[column_header]) for column_header in y_axis_column_headers] if y_axis_column_headers is not None else [],
        'params_filtered': filtered,
        'params_is_zoomed': is_zoomed
    })

    return fig, is_zoomed

def get_box_plot(axis, df, column_headers): 
    """
    Returns a box plot using the following heuristic:

    - If there are 2 or less series, no filtering is required.
    - If there are 3 series, filter to the first BOX_PLOT_3_SERIES_MAX_NUMBER_OF_ROWS rows.
    - If there are 4 series, filter to the first BOX_PLOT_4_SERIES_MAX_NUMBER_OF_ROWS rows.
    """
    fig = go.Figure()
    original_length_of_df = len(df)

    # Make sure all of the series are NUMBER_SERIES
    if not is_all_number_series(df, column_headers):
        # If not all of the series are numbers, then 
        # return a blank graph
        log(f'failed_generate_graph', {
            'params_graph_type': BOX,
            'params_axis': axis,
            'params_column_headers': column_headers,
            'params_failed_reason': 'non-number-series'
        })
        return go.Figure(), False
      
    filtered = False

    # If <= 2 series, no filter required
    if len(column_headers) <= 2:
        for column_header in column_headers:
            if axis == X:
                fig.add_trace(go.Box(x=df[column_header], name=column_header))
            else:
                fig.add_trace(go.Box(y=df[column_header], name=column_header))  
    # If 3 series, filter to 500k rows
    elif len(column_headers) == 3:
        for column_header in column_headers:
            filtered = original_length_of_df > BOX_PLOT_3_SERIES_MAX_NUMBER_OF_ROWS
            filter_label = ('top 500k') if filtered else ''
            if axis == X:
                fig.add_trace(go.Box(x=df[column_header].head(BOX_PLOT_3_SERIES_MAX_NUMBER_OF_ROWS), name=(' ').join([column_header, filter_label])))
            else:
                fig.add_trace(go.Box(y=df[column_header].head(BOX_PLOT_3_SERIES_MAX_NUMBER_OF_ROWS), name=(' ').join([column_header, filter_label]))) 
    # If > 3 series, filter to 250k rows
    else:
        for column_header in column_headers:
            filtered = original_length_of_df > BOX_PLOT_4_SERIES_MAX_NUMBER_OF_ROWS
            filter_label = ('top 250k') if filtered else ''
            if axis == X:
                fig.add_trace(go.Box(x=df[column_header].head(BOX_PLOT_4_SERIES_MAX_NUMBER_OF_ROWS), name=(' ').join([column_header, filter_label])))
            else:
                fig.add_trace(go.Box(y=df[column_header].head(BOX_PLOT_4_SERIES_MAX_NUMBER_OF_ROWS), name=(' ').join([column_header, filter_label]))) 
    
    graph_title = get_graph_title(column_headers, [], filtered, BOX)

    fig.update_layout(
        title = graph_title,
        barmode='stack'
    )

    log(f'generate_graph', {
        'params_graph_type': BOX,
        'params_axis': axis,
        'params_column_headers': column_headers,
        'params_filtered': filtered
    })
    
    return fig, False

def get_histogram(axis, df, column_headers, frequency_title=None):
    """
    Returns a histogram using the following heuristic:

    If any of the series are not NUMBER_SERIES, return a blank graph.

    Numeric histograms don't require any filtering.  
    """
    fig = go.Figure()

    for column_header in column_headers:
        if axis == X:
            fig.add_trace(go.Histogram(x=df[column_header], name=column_header))
        else:
            fig.add_trace(go.Histogram(y=df[column_header], name=column_header))

    if len(column_headers) == 1:
        if (axis == X):
            fig.update_layout (
                xaxis_title = column_headers[0]
            )
        else:
            fig.update_layout (
                yaxis_title = column_headers[0]
            )

    graph_title = get_graph_title(column_headers, [], False, HISTOGRAM, 'frequencies')
    fig.update_layout(
        title = graph_title,
        barmode='group'
    )

    log(f'generate_graph', {
        'params_graph_type': HISTOGRAM,
        'params_axis': axis,
        'params_column_headers': column_headers,
    })

    return fig, False

def get_scatter_plot(df, x_axis_column_headers, y_axis_column_headers):
    """
    Returns a scatter plot using the following heuristic:

    - If a non-number series exists, filter the df to contain the most common MAX_UNIQUE_NON_NUMBER_VALUES
    - Graph the first SCATTER_PLOT_MAX_NUMBER_OF_ROWS rows regardless of the type of the series. 
    """
    fig = go.Figure()
    original_length_of_df = len(df)

    x_axis = True if x_axis_column_headers != [] else None
    y_axis = True if y_axis_column_headers != [] else None

    # If no data is passed, return a blank graph
    if not x_axis and not y_axis:
        # This should never happen because this check already occurs in the get_graph
        # function. But we leave it here for robustness of the function
        return go.Figure(), False

    # Check the type of each series to appropriately filter 
    all_column_headers = x_axis_column_headers + y_axis_column_headers
    for column_header in all_column_headers:
        if get_mito_type(df[column_header]) != NUMBER_SERIES:
            # For each non-number series, filter it to only contain the most common values
            df = filter_df_to_top_unique_values_in_series(
                df, 
                df[column_header],
                MAX_UNIQUE_NON_NUMBER_VALUES,
            )

    # Then, take the first 10k rows
    total_allowed_rows = SCATTER_PLOT_LESS_THAN_4_SERIES_MAX_NUMBER_OF_ROWS if len(all_column_headers) < 4 else SCATTER_PLOT_4_SERIES_MAX_NUMBER_OF_ROWS
    filtered = original_length_of_df > total_allowed_rows
    df = df.head(total_allowed_rows)

    # Determine if the dataframe was sorted
    filter_label = ''
    if len(df) < original_length_of_df: 
        filter_label = '(first 10k)' if len(all_column_headers) < 4 else '(first 5k)'
    
    # If only one axis is defined, plotly defaults to using
    # the index column as the other axis. This is also what Google Sheets
    # does, so we do it too.    
    if x_axis and not y_axis:
        # Only an x_axis was provided
        for column_header in x_axis_column_headers:
            fig.add_trace(go.Scatter(
                y=df[column_header], 
                mode='markers',
                name=(' ').join([column_header, filter_label])
            ))
    elif not x_axis and y_axis:
        # Only a y axis was provided
        for column_header in y_axis_column_headers:
            fig.add_trace(go.Scatter(
                x=df[column_header],
                mode='markers',
                name=(' ').join([column_header, filter_label])
            ))
    elif len(y_axis_column_headers) == 1:
        # If the y axis only has one column header, then we use tat as the key
        for column_header in x_axis_column_headers:
            fig.add_trace(go.Scatter(
                x=df[column_header], 
                y=df[y_axis_column_headers[0]],
                mode='markers',
                name=(' ').join([column_header, filter_label])
            ))
    else:
        # It should not be possible for both the x axis and y axis 
        # to have more than 1 column. But if it does happen, we default 
        # to using the first column of the x axis as the key
        for column_header in y_axis_column_headers:
            fig.add_trace(go.Scatter(
                x=df[x_axis_column_headers[0]], 
                y=df[column_header],
                mode='markers',
                name=(' ').join([column_header, filter_label])
            ))

    # Update the layout of the graph
    x_axis_title, y_axis_title = get_graph_labels(x_axis_column_headers, y_axis_column_headers)
    graph_title = get_graph_title(x_axis_column_headers, y_axis_column_headers, filtered, SCATTER)
    fig.update_layout(
        xaxis_title = x_axis_title,
        yaxis_title = y_axis_title,
        title = graph_title,
    )

    # Update the starting range of the graph
    ranges = get_starting_ranges(BAR, df, x_axis_column_headers, y_axis_column_headers)
    fig.update_layout(
        xaxis=dict(
            range=ranges[X]
        ), 
        yaxis=dict(
            range=ranges[Y]
        )
    )
    # Determine if the graph was zoomed in
    is_zoomed = ranges[X][0] is not None or ranges[X][1] or ranges[Y][0] is not None or ranges[Y][1] is not None

    log(f'generate_graph', {
        'params_graph_type': SCATTER,
        'params_x_axis_column_headers': x_axis_column_headers,
        'params_x_axis_column_types': [get_mito_type(df[column_header]) for column_header in x_axis_column_headers] if x_axis_column_headers is not None else [],
        'params_y_axis_column_headers': y_axis_column_headers,
        'params_y_axis_column_types': [get_mito_type(df[column_header]) for column_header in y_axis_column_headers] if y_axis_column_headers is not None else [],
        'params_filtered': filtered,
        'params_is_zoomed': is_zoomed
    })

    return fig, is_zoomed


def get_column_summary_graph(axis, df, axis_data_array):
    """
    One Axis Graphs heuristics:
    1. Number Column - we do not filtering. These graphs are pretty efficient up to 1M rows
    2. Non-number column. We filter to the top 10k values, as the graphs get pretty laggy 
       beyond that
    """
    column_header: str = axis_data_array[0]
    series: pd.Series = df[column_header]
    mito_type = get_mito_type(series)

    graph_title = f'{column_header} Frequencies'

    filtered = False
    if mito_type != NUMBER_SERIES:
        if series.nunique() > MAX_UNIQUE_NON_NUMBER_VALUES:
            title = f'{graph_title} {MAX_UNIQUE_NON_NUMBER_VALUES_COMMENT}'
            df = filter_df_to_top_unique_values_in_series(
                df, 
                series, 
                MAX_UNIQUE_NON_NUMBER_VALUES
            )
            # Set series as the newly filtered series
            series = df[column_header]

            filtered = True

            
    labels = {axis: ''}

    kwargs = {
        axis: series,
        'labels': labels,
        'title': graph_title,
    }

    fig = px.histogram(
        **kwargs        
    )

    log(f'generate_column_summary_stat_graph', {
        f'param_is_number_series_{axis}': mito_type == NUMBER_SERIES,
        'param_filtered': filtered
    })

    # Because the Column Summary Stat Graph is never zoomed in 
    # we always return False as the second parameter
    return fig, False

def get_graph(event, steps_manager):
    """
    Creates a graph of the passed parameters, and sends it back as a PNG
    string to the frontend for display.

    Params:
    - graph_type
    - sheet_index
    - x_axis_column_header_array (optional)
    - y_axis_column_header_array (optional)
    - height (optional) - int representing the div width
    - width (optional) - int representing the div width

    If only an x axis is given, and if the series is a numeric series,
    will return a histogram. Otherwise, as long as there are less than 
    20 distinct items in the series, will return a bar chart of the 
    value count. Otherwise, will return nothing.
    """
    keys = event.keys()

    # Get graph type 
    graph_type = event['graph_type'] if 'graph_type' in keys else None

    # Get the x axis params, if they were provided
    x_axis_column_headers = event['x_axis_column_headers'] if event['x_axis_column_headers'] is not None else []
    x_axis = len(x_axis_column_headers) > 0

    # Get the y axis params, if they were provided
    y_axis_column_headers = event['y_axis_column_headers'] if event['y_axis_column_headers'] is not None else []
    y_axis = len(y_axis_column_headers) > 0
    
    # Find the height and the width, defaulting to fill whatever container its in
    height = event["height"] if 'height' in keys else '100%'
    width = event["width"] if 'width' in keys else '100%'

    sheet_index = event["sheet_index"] if "sheet_index" in keys else None

    try:
        # First, handle edge cases
        if not x_axis and not y_axis:
            # If no axes provided, return
            log(f'failed_generate_graph', {
                'params_graph_type': graph_type,
                'params_failed_reason': 'no axis data'
            })

            return ''
        if sheet_index is None or graph_type is None:
            # If no sheet_index or graph type is provided, return
            failed_reason = 'no selected_sheet_index' if sheet_index is None else 'no graph_type'
            log(f'failed_generate_graph', {
                'params_graph_type': graph_type,
                'params_failed_reason': failed_reason
            })
            return ''
        if x_axis and len(x_axis_column_headers) > 1 and y_axis and len(y_axis_column_headers) > 1:
            # If both axises have more than 1 series, return
            log(f'failed_generate_graph', {
                'params_graph_type': graph_type,
                'params_failed_reason': 'both axises have multiple columns'
            })
            return ''

        # Create a copy of the dataframe, just for safety.
        df: pd.DataFrame = steps_manager.dfs[sheet_index].copy()

        # Handle the graphs in alphabetical order
        if graph_type == BAR:
            fig, is_zoomed = get_bar_chart(df, x_axis_column_headers, y_axis_column_headers)
        elif graph_type == BOX:
            # Box plots are only defined on one axis. The UI should enforce that 
            # it is never the case that a box plot is selected with series for both 
            # the x and y axis. However, if it does happen, we default to taking the x axis. 
            if x_axis:
                fig, is_zoomed = get_box_plot(
                    X, df, x_axis_column_headers
                )
            else:
                fig, is_zoomed = get_box_plot(
                    Y, df, y_axis_column_headers
                )
        elif graph_type == HISTOGRAM:
            # Histograms are only defined on one axis. The UI should enforce that 
            # it is never the case that a histogram is selected with series for both 
            # the x and y axis. However, if it does happen, we default to taking the x axis. 
            if x_axis:
                fig, is_zoomed = get_histogram(X, df, x_axis_column_headers)
            else:
                fig, is_zoomed = get_histogram(Y, df, y_axis_column_headers)
        elif graph_type == SCATTER:
            fig, is_zoomed = get_scatter_plot(df, x_axis_column_headers, y_axis_column_headers)
        elif graph_type == SUMMARY_STAT:
            # We handle summary stats separately from the histogram, for now, because 
            # we only let the user use a histogram with all numeric data, whereas the column
            # summary stats may not be all numeric data. 
            fig, is_zoomed = get_column_summary_graph(
                X, df, x_axis_column_headers
            )
            
        # 1) Get rid of some of the default white space
        # 2) Add a range slider
        # 3) Set the colors of the graphs so they stand out more
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                t=30, 
                b=30,
            ),
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                ),
            ),
            colorway =["#FF0202", "#03AA00", "#FFA800", "#0085FF"],
        )

        # Make the rangeslider take up 5% of the height of the plot space
        fig.update_xaxes(
            rangeslider_thickness = 0.05
        )

        return_object = get_html_and_script_from_figure(
            fig, height, width
        )

        # Tell the frontend if the graph is zoomed in
        return_object['is_zoomed'] = is_zoomed

        return json.dumps(return_object),

    except Exception as e:
        # As not being able to make a graph is a non-critical error that doesn't
        # result from user interaction, we don't want to throw an error if something
        # weird happens, so we just return nothing in this case
        return ''