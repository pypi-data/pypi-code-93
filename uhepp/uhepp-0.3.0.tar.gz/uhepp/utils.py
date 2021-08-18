
import uhepp

def add_envelope(histo, variation, stack_index=0):
    """Returns a copy of the histogram with envelope stacks for the variation"""
    plot = histo.clone()

    stack = plot.stacks[stack_index]
    processes = [
        process
        for item in stack.content
        for process in item.yield_names
    ]

    # Up
    plot.stacks.append(uhepp.Stack([
            uhepp.StackItem(
                [f"{process}/{variation}/up" for process in processes],
                label="Up", color="#ff0000"
            )
        ], bartype="step")
    )
    plot.ratio.append(uhepp.RatioItem(
        [f"{process}/{variation}/up" for process in processes],
        processes, color="#ff0000"
    ))

    # Down
    plot.stacks.append(uhepp.Stack([
            uhepp.StackItem(
                [f"{process}/{variation}/down" for process in processes],
                label="Down", color="#0000ff"
            )
        ], bartype="step")
    )
    plot.ratio.append(uhepp.RatioItem(
        [f"{process}/{variation}/down" for process in processes],
        processes, color="#0000ff"
    ))

    return plot

def merge(first, *plots):
    """Combine multiple plots into a single plot"""
    result = first.clone()
    
    result.yields = {}
    result.stacks = []
    result.ratio = []
    for i, plot in enumerate([first, *plots]):
        plot = plot.clone()
        if plot.bin_edges != result.bin_edges:
            raise ValueError("Cannot merge incompatible bin edges")
                
        for yield_name, yield_obj in plot.yields.items():
            result.yields[f"h{i}_{yield_name}"] = yield_obj
        for stack in plot.stacks:
            for item in stack.content:
                item.yield_names = [f"h{i}_{name}"
                                    for name in item.yield_names]
            result.stacks.append(stack)
        for ratio in plot.ratio:
            ratio.numerator = [f"h{i}_{name}"
                               for name in ratio.numerator]
            ratio.denominator = [f"h{i}_{name}"
                                 for name in ratio.denominator]
            result.ratio.append(ratio)
    return result
