import matplotlib.pyplot as plt
import typer

from pyplot_cli.io import DataSet


def str_to_list(string: str, dtype: type) -> list:
    """convert comma-separarted options to list.
    """
    if string == "":
        return []
    string = "".join(string.split())  # remove whitespaces
    options = list(map(dtype, string.split(",")))
    return options


def main(
    filename: str,
    x_idx: int = typer.Option(..., "-x"),
    y_idx: str = typer.Option(...,
                              "-y",
                              help="Comma-separated column indices ex)'1,2'"),
    colors: str = typer.Option("", help="Comma-separated colors ex)'k,r'"),
    styles: str = typer.Option("-", help="Comma-separated colors ex)'-,o-'"),
    xlabel: str = typer.Option("", help="xlabel. Default is column name."),
    ylabel: str = typer.Option("", help="ylabel. default is 'data'"),
    show_grid: bool = typer.Option(False, "--grid", help="Show grids or not"),
    show_minorticks: bool = typer.Option(False,
                                         "--minorticks",
                                         help="Show minorticks or not"),
    show_legend: bool = typer.Option(False,
                                     "--legend",
                                     help="Show legend or not"),
    show_figure: bool = typer.Option(True,
                                     "--show",
                                     help="Show interactive figure or not"),
    stylesheet: str = typer.Option(
        "", help="Custom stylesheet. If not given, uses default style."),
    save_file: str = typer.Option(
        "",
        "--output",
        help="Filename to save figure. If not given, does not save."),
):
    """Simple cli app to plot figure from data file with matplotlib."""
    y_idx_list = str_to_list(y_idx, int)
    colors_list = str_to_list(colors, str)
    styles_list = str_to_list(styles, str)

    if len(styles_list) == 1:
        styles_list = styles_list * len(y_idx_list)

    dataset = DataSet(filename)

    x_values = dataset.values[x_idx]
    selected_column_names = [dataset.column_names[i] for i in y_idx_list]
    y_values_list = [dataset.values[i] for i in y_idx_list]

    if stylesheet:
        plt.style.use(stylesheet)

    plt.figure()

    # plot
    if colors_list == []:
        for style, label, y_values in zip(styles_list, selected_column_names,
                                          y_values_list):
            plt.plot(x_values, y_values, style, label=label)
    else:
        for style, color, label, y_values in zip(styles_list, colors_list,
                                                 selected_column_names,
                                                 y_values_list):
            plt.plot(x_values, y_values, style, c=color, label=label)

    if xlabel:
        plt.xlabel(xlabel)
    else:
        plt.xlabel(dataset.column_names[0])

    if ylabel:
        plt.ylabel(ylabel)
    else:
        plt.ylabel("data")

    if show_grid:
        plt.grid()

    if show_minorticks:
        plt.minorticks_on()

    if show_legend:
        plt.legend(facecolor="none", edgecolor="none")

    if save_file:
        plt.savefig(save_file, dpi=600, facecolor="w")

    if show_figure:
        plt.show()


def run():
    typer.run(main)
