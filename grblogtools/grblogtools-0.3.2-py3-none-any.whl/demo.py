# %%

import grblogtools as glt
import plotly.io as pio
pio.renderers.default = "notebook"

summary, timelines, rootlp = glt.get_dataframe(
    ["c:/users/miltenberger/code/grblogtools/data/*.log"],
    timelines=True,
    merged_logs=False,
)
summary[
    [
        "ModelName",
        "Settings",
        "Seed",
        "ModelFilePath",
    ]
].head()

timelines.tail()
# %%
glt.plot(timelines, type="line")

# %%

import plotly.graph_objects as go
fig = go.Figure(
    data=[go.Bar(y=[2, 1, 3])],
    layout_title_text="A Figure Displayed with fig.show()"
)
fig.show()