

from typing import List
import pandas as pd
import plotly.graph_objects as go

from mitosheet.mito_analytics import log
from mitosheet.api.graph.graph_utils import CREATE_FIG_CODE, HISTOGRAM, SHOW_FIG_CODE, X, get_graph_title


def get_histogram(axis, df, column_headers):
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
        if axis == X:
            fig.update_layout(
                xaxis_title=column_headers[0]
            )
        else:
            fig.update_layout(
                yaxis_title=column_headers[0]
            )

    graph_title = get_graph_title(column_headers, [], False, HISTOGRAM, 'frequencies')
    fig.update_layout(
        title=graph_title,
        barmode='group'
    )

    log(f'generate_graph', {
        'params_graph_type': HISTOGRAM,
        'params_axis': axis,
        'params_column_headers': column_headers,
    })

    return fig, False

def get_histogram_code(
        axis: str, 
        df: pd.DataFrame, 
        column_headers: List[str], 
        df_name: str
    ):
    """
    Generates code for a histogram, as above.
    """

    graph_title = get_graph_title(column_headers, [], False, HISTOGRAM, 'frequencies')

    # Note: we conditionally include this code
    update_layout_code = ''
    if len(column_headers) == 1:
        if axis == X:
            update_layout_code = "\n\txaxis_title='{column_header}',".format(column_header=column_headers[0])
        else:
            update_layout_code = "\n\tyaxis_title='{column_header}',".format(column_header=column_headers[0])

    return """{CREATE_FIG_CODE}

# Add the histogram traces to the figure
for column_header in {column_headers}:
    fig.add_trace(go.Histogram({axis}={df_name}[column_header], name=column_header))

# Update the layout
# See Plotly documentation for customizations: https://plotly.com/python/reference/histogram/
fig.update_layout({update_layout_code}
    title='{graph_title}',
    barmode='group'
)
{SHOW_FIG_CODE}""".format(
    CREATE_FIG_CODE=CREATE_FIG_CODE,
    column_headers=column_headers,
    df_name=df_name,
    axis=axis,
    graph_title=graph_title,
    update_layout_code=update_layout_code,
    SHOW_FIG_CODE=SHOW_FIG_CODE
)