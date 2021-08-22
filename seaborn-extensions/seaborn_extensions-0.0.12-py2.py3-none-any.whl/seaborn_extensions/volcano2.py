import numpy as np
import matplotlib.pyplot as plt

from seaborn_extensions.types import DataFrame, Figure
from seaborn_extensions.utils import get_grid_dims, log_pvalues


def volcano_plot(stats: DataFrame, x="A", y="B", features=None) -> Figure:
    if features is None:
        stats["features"] = stats.index
    else:
        stats["features"] = stats[features]
    ### volcano plot
    combs = stats[["A", "B"]].drop_duplicates().reset_index(drop=True)
    stats["hedges"] *= -1
    stats["logp-unc"] = log_pvalues(stats["p-unc"].fillna(1))
    stats["logp-cor"] = log_pvalues(stats["p-cor"].fillna(1))
    stats["p-cor-plot"] = (stats["logp-cor"] / stats["logp-cor"].max()) * 5
    n, m = get_grid_dims(combs.shape[0])
    fig, axes = plt.subplots(n, m, figsize=(4 * m, 4 * n), squeeze=False)
    for idx, (a, b) in combs.iterrows():
        ax = axes.flatten()[idx]
        p = stats.query(f"{x} == '{a}' & {y} == '{b}'")
        v = p["hedges"].abs().max()
        ax.axvline(0, linestyle="--", color="grey")
        ax.scatter(
            p["hedges"],
            p["logp-unc"],
            c=p["hedges"],
            s=5 + (2 ** p["p-cor-plot"]),
            cmap="coolwarm",
            vmin=-v,
            vmax=v,
        )
        ax.set(title=f"{b} / {a}", ylabel=None, xlabel=None)
        for t in p.query(f"`p-cor` < 0.05").index:
            ax.text(
                p.loc[t, "hedges"],
                p.loc[t, "logp-unc"],
                s=p.loc[t, "features"],
                ha="right" if p.loc[t, "hedges"] > 0 else "left",
            )
    for ax in axes.flatten()[idx + 1 :]:
        ax.axis("off")

    for ax in axes[:, 0]:
        ax.set(ylabel="-log10(p-val)")
    for ax in axes[-1, :]:
        ax.set(xlabel="Hedges' g")
    return fig
