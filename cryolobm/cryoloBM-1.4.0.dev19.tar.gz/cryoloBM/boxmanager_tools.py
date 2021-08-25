#
# This fiel contains command line cryoloBM_tools for box management
#
import sys
import argparse
from typing import List
from cryoloBM.bmtool import BMTool


def get_tool_list() -> List[BMTool]:
    tools = []

    from cryoloBM_tools.filamentresampling import FilamentResampleTool
    fil_resample_tool = FilamentResampleTool()
    tools.append(fil_resample_tool)

    from cryoloBM_tools.coords2warp import Coords2WarpTool
    c2w_tool = Coords2WarpTool()
    tools.append(c2w_tool)

    from cryoloBM_tools.priors2star import Priors2StarTool
    p2s_tool = Priors2StarTool()
    tools.append(p2s_tool)

    from cryoloBM_tools.scale import ScaleTool
    scale_tool = ScaleTool()
    tools.append(scale_tool)


    return tools

def _main_():

    parser = argparse.ArgumentParser(
        description="Boxmanager Tools",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(help="sub-command help")


    tools = get_tool_list()

    tools = sorted(tools, key=lambda x: x.get_command_name())

    for tool in tools:
        tool.create_parser(subparsers)

    args = parser.parse_args()

    for tool in tools:
        if tool.get_command_name() in sys.argv[1]:
            tool.run(args)




if __name__ == "__main__":
    _main_()