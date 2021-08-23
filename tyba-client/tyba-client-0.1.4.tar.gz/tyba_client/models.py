from dataclasses import dataclass, field
from enum import Enum
from dataclasses_json import config, dataclass_json
import typing as t

from tyba_client.utils import string_enum


def opt_field():
    return field(default=None, metadata=config(exclude=lambda x: x is None))

@dataclass_json
@dataclass
class FixedTilt(object):
    tilt: float


@dataclass_json
@dataclass
class SingleAxisTracking(object):
    rotation_limit: float = 45.0
    backtrack: bool = True

@dataclass_json
@dataclass
class PVModel(object):
    location: t.Tuple[float, float]
    inverter_name: str
    pv_module_name: str
    gcr: float
    ac_capacity: float
    poi_limit: float
    dc_capacity: float
    tracking: t.Union[FixedTilt, SingleAxisTracking]
    project_term: t.Optional[int] = opt_field()
    dc_degradation: t.Optional[float] = opt_field()


@dataclass_json
@dataclass
class SystemDesign(object):
    dc_capacity: float
    ac_capacity: float
    poi_limit: float
    gcr: float
    modules_per_string: int
    strings_in_parallel: int
    tracking: t.Union[FixedTilt, SingleAxisTracking]
    azimuth: t.Optional[float] = opt_field()

@dataclass_json
@dataclass
class Inverter(object):
    mppt_low: float
    mppt_high: float
    pso: float
    paco: float
    pdco: float
    vdco: float
    c0: float
    c1: float
    c2: float
    c3: float
    pnt: float
    vdcmax: float
    tdc: t.List[t.List[float]] = field(default_factory=lambda: [[1.0, 52.8, -0.021]])


@dataclass_json
@dataclass
class PVModule(object):
    bifacial: bool
    a_c: float
    n_s: float
    i_sc_ref: float
    v_oc_ref: float
    i_mp_ref: float
    v_mp_ref: float
    alpha_sc: float
    beta_oc: float
    t_noct: float
    a_ref: float
    i_l_ref: float
    i_o_ref: float
    r_s: float
    r_sh_ref: float
    adjust: float
    gamma_r: float
    bifacial_transmission_factor: float
    bifaciality: float
    bifacial_ground_clerance_height: float

@dataclass_json
@dataclass
class Losses(object):
    ac_wiring: t.Optional[float] = opt_field()
    dc_optimizer: t.Optional[float] = opt_field()
    enable_snow_model: t.Optional[bool] = opt_field()
    dc_wiring: t.Optional[float] = opt_field()
    diodes_connections: t.Optional[float] = opt_field()
    mismatch: t.Optional[float] = opt_field()
    nameplate: t.Optional[float] = opt_field()
    rear_irradiance: t.Optional[float] = opt_field()
    soiling: t.Optional[t.List[float]] = opt_field()
    tracking: t.Optional[float] = opt_field()
    transformer_load: t.Optional[float] = opt_field()
    transformer_no_load: t.Optional[float] = opt_field()
    transmission: t.Optional[float] = opt_field()

@dataclass_json
@dataclass
class Layout(object):
    orientation: t.Optional[str] = opt_field()
    vertical: t.Optional[int] = opt_field()
    horizontal: t.Optional[int] = opt_field()
    aspect_ratio: t.Optional[float] = opt_field()


@dataclass_json
@dataclass
class SolarResourceTimeSeries(object):
    year: t.List[int]
    month: t.List[int]
    day: t.List[int]
    hour: t.List[int]
    minute: t.List[int]
    tdew: t.List[float]
    df: t.List[float]
    dn: t.List[float]
    gh: t.List[float]
    pres: t.List[float]
    tdry: t.List[float]
    wdir: t.List[float]
    wspd: t.List[float]
    alb: t.Optional[t.List[float]] = opt_field()

@dataclass_json
@dataclass
class SolarResource(object):
    latitude: float
    longitude: float
    time_zone_offset: float
    elevation: float
    data: SolarResourceTimeSeries
    monthly_albedo: t.Optional[t.List[float]] = opt_field()


@dataclass_json
@dataclass
class DetailedPVModel(object):
    solar_resource: t.Union[t.Tuple[float, float], SolarResource]
    inverter: t.Union[str, Inverter]
    pv_module: t.Union[str, PVModule]
    system_design: SystemDesign
    losses: t.Optional[Losses] = opt_field()
    layout: t.Optional[Layout] = opt_field()
    project_term: t.Optional[int] = None
    dc_degradation: t.Optional[float] = None

@dataclass_json
@dataclass
class SingleStorageInputs(object):
    power_capacity: float
    energy_capacity: float
    charge_efficiency: float
    discharge_efficiency: float
    degradation_rate: float
    cycling_cost_adder: t.Optional[float] = 0

@dataclass_json
@dataclass
class Battery(object):
    power_capacity: float
    energy_capacity: float
    charge_efficiency: float
    discharge_efficiency: float
    degradation_rate: float
    term: int

@dataclass_json
@dataclass
class StorageInputs(object):
    batteries: t.List[Battery]
    cycling_cost_adder: t.Optional[float] = 0
    window: t.Optional[int] = opt_field()
    step: t.Optional[int] = opt_field()



@dataclass_json
@dataclass
class StorageModel(object):
    storage_inputs: StorageInputs
    energy_prices: t.List[float]

@dataclass_json
@dataclass
class AncillaryMarkets(object):
    rrs_capacity_factor: t.Optional[float]
    reg_up_capacity_factor: t.Optional[float]
    reg_down_capacity_factor: t.Optional[float]
    rrs_utilization: t.Optional[float]
    reg_up_utilization: t.Optional[float]
    reg_down_utilization: t.Optional[float]
    rrs_prices: t.Optional[t.List[float]]
    reg_up_prices: t.Optional[t.List[float]]
    reg_down_prices: t.Optional[t.List[float]]
    reserve_settlement_prices: t.List[float]

@dataclass_json
@dataclass
class StandaloneStorageModel(StorageModel):
    time_interval_mins: t.Optional[float] = opt_field()
    ancillary_markets: t.Optional[AncillaryMarkets] = opt_field()


@string_enum
class StorageCoupling(Enum):
    ac = 'ac'
    dc = 'dc'


PVModelTypes = t.Union[PVModel, DetailedPVModel]

@dataclass_json
@dataclass
class PVStorageModel(object):
    storage_coupling: StorageCoupling = field(metadata=StorageCoupling.__metadata__)
    pv_inputs: PVModelTypes
    storage_inputs: StorageInputs
    energy_prices: t.List[float]