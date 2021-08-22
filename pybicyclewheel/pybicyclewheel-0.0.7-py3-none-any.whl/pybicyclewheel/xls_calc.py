from pybicyclewheel.dataloader import RimDataLoader, HubDataLoader

from pybicyclewheel.rim import Rim
from pybicyclewheel.hub import Hub
from pybicyclewheel.wheel import Wheel

# calc


def wheel_calc(
    rim_idx,
    hub_idx,
    rim_path="./rims.xls",
    hub_path="./hubs.xls",
    cross_l=3,
    cross_r=3,
    spoke=2.0,
):

    xls_off = -2

    rdl = RimDataLoader(rim_path).load_xls()

    rim_dims = rdl.get_dims(rim_idx + xls_off)
    rim_info = rdl.get_row(rim_idx + xls_off)

    hdl = HubDataLoader(hub_path).load_xls()

    hub_dims = hdl.get_dims(hub_idx + xls_off)
    hub_info = hdl.get_row(hub_idx + xls_off)

    if rim_dims.holes != hub_dims.holes:
        raise Exception("number of holes different")

    rim = Rim(rim_dims.erd)

    hub = Hub(
        hub_dims.holes,
        diameter_l=hub_dims.flange_diameter_left,
        diameter_r=hub_dims.flange_diameter_right,
        distance_l=-hub_dims.flange_distance_left,
        distance_r=hub_dims.flange_distance_right,
        spoke_hole=hub_dims.spoke_hole,
    )

    wheel = Wheel(hub=hub, rim=rim, cross_l=cross_l, cross_r=cross_r, spoke=spoke)
    spoke_lr = wheel.spoke_lr()

    return spoke_lr, wheel, rim_dims, rim_info, hub_dims, hub_info
