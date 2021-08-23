import matplotlib.pyplot as plt


def draw_scatter(title: str,
                 x_label: str,
                 y_label: str,
                 y_list: list,
                 x_list: list,
                 dot_size: int,
                 color: str
                 ):
    x_min = min(x_list)
    x_max = max(x_list)
    y_min = min(y_list)
    y_max = max(y_list)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.axis([x_min, x_max, y_min, y_max])
    plt.scatter(x_list, y_list, s=dot_size, edgecolors='None', c=color)
    plt.show()
