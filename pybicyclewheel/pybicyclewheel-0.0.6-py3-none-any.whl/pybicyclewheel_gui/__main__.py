from pybicyclewheel.xls_calc import *
from pybicyclewheel_gui import *

from pybicyclewheel_gui.tile import *

from tkinter import messagebox

import webbrowser

"""

simple gui for pybicyclewheel

"""


ftypes = [("xls files", "*.xls"), ("all files", "*.*")]
t_rim_file = TileFileSelect(
    caption="Rim file",
    commandtext="...",
    path="~/repo/pybicyclewheel/rims.xls",
    filetypes=ftypes,
)
t_hub_file = TileFileSelect(
    caption="Hub file", path="~/repo/pybicyclewheel/hubs.xls", filetypes=ftypes
)

t_cross = TileEntryCombo(caption="Crosses", values=[3, 2, 4, 1], sel_idx=0)


rdl = None
rim_dims = None


def rim_data():
    r = rim_list.get_val()[1]
    print(r)
    t_rim_erd.set_val(r.erd)
    t_rim_hole.set_val(r.holes)


rim_list = TileEntryListbox(
    caption="select one",
    values=[],
    map_value=lambda x: f"{x.manufacturer} {x.model} {x.year} {x.holes} {x.ean}",
    on_select=rim_data,
)


def reload_rim():
    print("reload_rim")

    global rdl, rim_dims

    rdl = RimDataLoader(t_rim_file.get_val()).load_xls()

    print(rdl.data)

    rims = []
    for i in range(0, len(rdl.data)):
        r = rdl.get_dims(i)
        print("rim:", r)
        rims.append(r)

    rim_list.set_values(rims)
    rim_list.layout()


hdl = None
hub_dims = None


def reload_hub():
    global hdl, hub_dims

    hdl = HubDataLoader(t_hub_file.get_val()).load_xls()

    # print(hdl.data)

    hubs = []
    for i in range(0, len(hdl.data)):
        h = hdl.get_dims(i)
        # print("hub:",h)
        hubs.append(h)

    hub_list.set_values(hubs)
    hub_list.layout()


t_reload_rim = TileLabelButton(caption="reload rim data file", command=reload_rim)
t_reload_hub = TileLabelButton(caption="reload hub data file", command=reload_hub)


def hub_data():
    h = hub_list.get_val()[1]
    print(h)
    t_hub_dia_l.set_val(h.flange_diameter_left)
    t_hub_dia_r.set_val(h.flange_diameter_right)
    t_hub_dist_l.set_val(h.flange_distance_left)
    t_hub_dist_r.set_val(h.flange_distance_right)
    t_hub_hole.set_val(h.holes)


hub_list = TileEntryListbox(
    caption="select one",
    values=[],
    map_value=lambda x: f"{x.manufacturer} {x.model} {x.year} {x.holes} {x.ean}",
    on_select=hub_data,
)


def reload_all():
    reload_rim()
    reload_hub()


t_reload = TileLabelButton(caption="reload all data files", command=reload_all)


t_hub_dia_l = TileEntry(caption="hub diameter left")
t_hub_dia_r = TileEntry(caption="hub diameter right")
t_hub_dist_l = TileEntry(caption="hub dist left")
t_hub_dist_r = TileEntry(caption="hub dist right")
t_hub_hole = TileEntry(caption="hub hole#")

t_rim_erd = TileEntry(caption="rim erd")
t_rim_hole = TileEntry(caption="rim hole#")


def calc():
    print("calc")

    t_result_spoke_l.set_val()
    t_result_spoke_r.set_val()

    try:

        hub_hole = int(t_hub_hole.get_val())

        hub = Hub(
            hub_hole,
            diameter_l=float(t_hub_dia_l.get_val()),
            diameter_r=float(t_hub_dia_r.get_val()),
            distance_l=-float(t_hub_dist_l.get_val()),
            distance_r=float(t_hub_dist_r.get_val()),
            spoke_hole=None,
        )

        rim_hole = int(t_rim_hole.get_val())

        rim = Rim(float(t_rim_erd.get_val()))

        if rim_hole != hub_hole:
            messagebox.showerror(title="error", message="number of holes do not match")
            return

        cross = int(t_cross.get_val())
        spoke = rim_hole

        wheel = Wheel(hub=hub, rim=rim, cross_l=cross, cross_r=cross, spoke=None)
        spoke_lr = wheel.spoke_lr()

        print(wheel)

        spoke_lr = wheel.spoke_lr()

        print(spoke_lr)

        t_result_spoke_l.set_val(spoke_lr[0])
        t_result_spoke_r.set_val(spoke_lr[1])

    except Exception as ex:
        messagebox.showerror(title="error", message="check input data, and log")


t_result_spoke_l = TileEntry(
    caption="spoke length left",
)
t_result_spoke_r = TileEntry(caption="spoke length right")
t_calc = TileButton(caption="", commandtext="calc spoke", command=calc)

t_tab = TileTab(
    source=[
        (
            "hub",
            TileRows(
                source=[
                    t_hub_file,
                    t_reload_hub,
                    hub_list,
                    t_hub_dia_l,
                    t_hub_dia_r,
                    t_hub_dist_l,
                    t_hub_dist_r,
                    t_hub_hole,
                ]
            ),
        ),
        (
            "rim",
            TileRows(
                source=[
                    t_rim_file,
                    t_reload_rim,
                    rim_list,
                    t_rim_erd,
                    t_rim_hole,
                ]
            ),
        ),
        (
            "calculation",
            TileRows(
                source=[
                    t_cross,
                    t_result_spoke_l,
                    t_result_spoke_r,
                    t_calc,
                ]
            ),
        ),
    ]
)


mainframe = Tile(Tile.tk)
# mainframe.title("pyBicycleWheel")

t_close = TileLabelButton(caption="close app", command=mainframe.quit)


def openweb():
    webbrowser.open("https://github.com/kr-g/pybicyclewheel")


main = TileRows(
    source=[
        t_close,
        t_reload,
        t_tab,
        TileLabelClick(
            caption="homepage: https://github.com/kr-g/pybicyclewheel", on_click=openweb
        ),
    ]
)

mainframe.add(main)
mainframe.layout()

# mainframe.geometry("+100+100")
mainframe.resize_grip()

mainframe.mainloop()
