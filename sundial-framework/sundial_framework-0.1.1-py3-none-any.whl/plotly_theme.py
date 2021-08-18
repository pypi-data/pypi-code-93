import plotly.graph_objects as go
import plotly.io as pio

# ______________________________________
# Define template object
# ______________________________________

# set up a custom dark plotly template
pio.templates["predictor"] = pio.templates["plotly_dark"]
predictor_template = pio.templates["predictor"]
pio.templates.default = "predictor"


# ______________________________________
# General parameter definitions
# ______________________________________

plot_pallette_dark = [
    "#008fd1",
    "#ff707a",
    "#ab82e0",
    "#ffa600",
    "#688ce1",
    "#ff6aa8",
    "#e374cc",
    "#ff8749",
]

colour_dark = dict(
    app_background="#222",
    text="#fafafa",
    box_background="#303030",
    axis="#fafafa",
    axis_line="#fafafa",
    grid_line="#777777",
    spikes="#97aec2",
    pallette=plot_pallette_dark,
    rangeslider_border="#b1c3d4",
    rangeslider_bg="#444",
    now_line="#777777",
    button_bg="#444",
    button_bg_focus="#28415b",
    endpoint_colour=plot_pallette_dark[1],
    table_odd_row="#555",
    table_even_row="#555",
    table_firstcol_odd="#555",
    table_firstcol_even="#555",
    table_header="#444",
    table_border="#303030",
)

plot_margins_default = dict(l=50, r=50, b=50, t=50, pad=4)

table_default = dict(
    width_firstcol=3, width_col=1, cell_height=30, line_width=2, outer_margins=dict(l=20, r=20, b=50, t=50, pad=4),
)
# print(base_colour_pallette.copy().reverse())
colour_theme = colour_dark.copy()

# ______________________________________
# General layout formatting
# ______________________________________

# plot background
predictor_template["layout"]["paper_bgcolor"] = colour_theme["box_background"]
predictor_template["layout"]["plot_bgcolor"] = colour_theme["box_background"]

# axes. Here use the color property to set everything at once. Maybe control finer later.
predictor_template["layout"]["xaxis"]["color"] = colour_theme["axis"]
predictor_template["layout"]["yaxis"]["color"] = colour_theme["axis"]
predictor_template["layout"]["xaxis"]["linecolor"] = colour_theme["axis"]
predictor_template["layout"]["yaxis"]["linecolor"] = colour_theme["axis"]
predictor_template["layout"]["xaxis"]["linewidth"] = 1
predictor_template["layout"]["yaxis"]["linewidth"] = 1
predictor_template["layout"]["xaxis"]["showline"] = True
predictor_template["layout"]["yaxis"]["showline"] = True
predictor_template.layout.xaxis.type = "-"

# xaxis rangeslider formatting
predictor_template.layout.xaxis.rangeslider.visible = False
predictor_template.layout.xaxis.rangeslider.borderwidth = 0
predictor_template.layout.xaxis.rangeslider.bordercolor = colour_theme["rangeslider_border"]
predictor_template.layout.xaxis.rangeslider.thickness = 0.20
predictor_template.layout.xaxis.rangeslider.bgcolor = colour_theme["rangeslider_bg"]

# xaxis rangeselector formatting
predictor_template.layout.xaxis.rangeselector.visible = False
predictor_template.layout.xaxis.rangeselector.font.color = colour_theme["text"]
predictor_template.layout.xaxis.rangeselector.bgcolor = colour_theme["button_bg"]
predictor_template.layout.xaxis.rangeselector.activecolor = colour_theme["button_bg"]
predictor_template.layout.xaxis.rangeselector.borderwidth = 0


# axis spikes
predictor_template["layout"]["yaxis"]["showspikes"] = False
predictor_template["layout"]["xaxis"]["showspikes"] = True
predictor_template["layout"]["xaxis"]["spikethickness"] = 1
predictor_template["layout"]["xaxis"]["spikedash"] = "dot"
predictor_template.layout.xaxis.spikesnap = "data"
predictor_template["layout"]["xaxis"]["spikecolor"] = colour_theme["spikes"]
predictor_template.layout.spikedistance = 5000

# grid
predictor_template["layout"]["yaxis"]["gridcolor"] = colour_theme["grid_line"]
predictor_template["layout"]["yaxis"]["showgrid"] = True
predictor_template["layout"]["xaxis"]["showgrid"] = False

# margin
# predictor_template.layout.margin = plot_margins_default

# hover
predictor_template.layout.hovermode = "x"
predictor_template.layout.xaxis.hoverformat = ".2f"
predictor_template.layout.hoverdistance = 100

# graph series colours
predictor_template.layout.colorway = colour_theme["pallette"]

# ______________________________________
# Plot-type specific formatting
# ______________________________________

# scatter plots
predictor_template.data.scatter = [
    go.Scatter(hovertemplate="%{y:.2f}", line=dict(shape="linear", dash="solid", width=1))
]

# bar plots
# predictor_template.layout.barmode='stack'
predictor_template.layout.bargap = 0.1
predictor_template.data.bar = [
    go.Bar(hovertemplate="%{y:.2f}<extra></extra>", marker=dict(opacity=0.8, line={"width": 1}),)
]

# tables
predictor_template.data.table = [go.Table(hoverinfo="x+y")]

# ______________________________________
# Formatting options
# ______________________________________
#
# Formatting options are to be used by the graph code to make standardised adustments
# or to select amoung standardised alternatives for things like graph size etc

# graph general formatting
graph_format_std = go.Layout(
    height=350,
    title=dict(font={"size": 14}),
    xaxis=dict(tickfont={"size": 10}, titlefont={"size": 12}),
    yaxis=dict(tickfont={"size": 10}, titlefont={"size": 12}),
)

graph_format_lrg = go.Layout(
    height=350,
    xaxis=dict(tickfont={"size": 10}, titlefont={"size": 12}),
    yaxis=dict(tickfont={"size": 10}, titlefont={"size": 12}),
)

# graph legend
legend_right_vertical = go.Layout(
    legend=dict(orientation="v", yanchor="top", xanchor="left", x=1.02, y=1, font=dict(size=10))
)

legend_top_right_horizontal = go.Layout(
    legend=dict(orientation="h", yanchor="bottom", xanchor="right", x=1.02, y=1, font=dict(size=10),)
)

legend_bottom_centre_horizontal = go.Layout(
    legend=dict(orientation="h", yanchor="top", xanchor="center", x=0.5, y=-0.1, font=dict(size=10),)
)
