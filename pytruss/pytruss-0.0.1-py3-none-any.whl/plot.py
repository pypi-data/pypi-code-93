import matplotlib.pyplot as plt
import numpy as np


def plot(model) -> None:
    x, y = [], []
    xd, yd = [], []

    d = model.deformations
    for element in model.elements:
        x.append(element.node1.x)
        x.append(element.node2.x)
        x.append(np.nan)
        y.append(element.node1.y)
        y.append(element.node2.y)
        y.append(np.nan)
        if d is not None:
            xd.append(element.node1.x + d[element.node1.dofs[0]])
            xd.append(element.node2.x + d[element.node2.dofs[0]])
            xd.append(np.nan)
            yd.append(element.node1.y + d[element.node1.dofs[1]])
            yd.append(element.node2.y + d[element.node2.dofs[1]])
            yd.append(np.nan)

        plt.plot(
            [element.node1.x, element.node2.x],
            [element.node1.y, element.node2.y],
            "o-",
            color="k",
            linewidth=4,
        )
    plt.plot(xd, yd, "ok--")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.show()