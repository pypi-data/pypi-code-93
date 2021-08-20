# 账单sql，参数：sn、month
FARADAY_BILL_SQL = """
SELECT
A.number AS sn,
B.power_number AS source_sn,
C.*,
C.tip_volume + C.tip_volume2 + C.peak_volume + C.peak_volume2 + 
C.usual_volume + C.usual_volume2 + C.valley_volume + C.valley_volume2 + 
C.other_volume AS total_volume
FROM `console`.electricity_bill C
INNER JOIN `console`.electrical_info B on C.electrical_id=B.id
LEFT JOIN `console`.electricity_user A on A.id=B.electricity_user_id 
WHERE A.number = "{sn}" and C.year_month = "{month}"
"""

# 电价表sql，无参数
FARADAY_TARIFF_SQL = """
SELECT *
FROM `faladi`.code_tariff
"""

# 分时段表sql，无参数
FARADAY_TIME_OF_USE_SQL = """
SELECT *
FROM `faladi`.code_tou
"""

# 巡检记录sql，参数：sn、month
FARADAY_INSPECT_RECORD_SQL = """
SELECT
electricity_user.number AS sn,
E.power_number AS source_sn,
E.meter_number AS meter_sn,
E.id as source_id,
E.voltage_level,
E.magnification as override,
E.transformer_capacity as capacity,
E.real_capacity,
DATE_FORMAT(B.end_time,"%Y-%m-%d %H:%i:%s") AS date,
C.inspector,
BC.nickname as team_headman_name,
C.temperature AS temp,
C.humidity AS humi,
ifnull(C.weather,"晴") AS weather,
AA.cable_conduit_status AS house1,
AA.cable_holes_status AS house2,
AA.frame_status AS house3,
AA.ground_status AS house4,
AA.window_status AS house5,
AA.house_status AS house6,
AAA.electroprobe_status AS facility1,
AAA.ground_wire AS facility2,
AAA.insulating_mat AS facility3,
AAA.insulating_gloves AS facility4,
AAA.insulating_shoes AS facility5,
AAA.extinguisher AS facility6,
D.multiplying_power,
D.power_factor,
D.total_active_power AS active_volume,
D.peak AS peak_volume,
D.flat_1 AS usual1_volume,
D.flat_2 AS usual2_volume,
D.valley AS valley_volume,
D.peak_md,
D.flat_1_md AS usual1_md,
D.flat_2_md AS usual2_md,
D.valley_md,
D.max_md,
D.declare_md,
D.real_power_factor AS power_factor_real,
D.reactive_power_1 AS idle1_volume,
D.reactive_power_2 AS idle2_volume,
F.v_ab,
F.v_bc,
F.v_ca,
F.i_a,
F.i_b,
F.i_c,
F.monitor_a as pd_a,
F.monitor_b as pd_b,
F.monitor_c as pd_c,
G.outline as transformer_id,
G.o_ia,
G.o_ib,
G.o_ic,
G.cos,
G.power,
G.monitor_a as o_pda,
G.monitor_b as o_pdb,
G.monitor_c as o_pdc,
G.voice as t_voice,
G.fan as t_fan,
# G.temperature as o_temperature,
G.oil_leak as t_oil,
G.dry as t_dry,
concat(CAST(G.temperature_a as char)," ", CAST(G.temperature_b as char)," ", CAST(G.temperature_c as char)) as t_temp,
G.abnormal as t_exception,
G.switch_v_ab as s_vab,
G.switch_v_bc as s_vbc,
G.switch_v_ca as s_vca,
G.switch_ia as s_ia,
G.switch_ib as s_ib,
G.switch_ic as s_ic,
G.GGJ as ec_status
FROM
(select id,station_id 
from inspection_plan
where station_id in 
        (select B.id 
        from electricity_user A
        left join power_station B on A.id=B.electricity_user_id
        )
) A
left join station_building AA on AA.station_id=A.station_id
left join safety_equipment AAA on AAA.station_id=A.station_id
left join inspection_task B ON B.plan_id=A.id
left join team BB on BB.id=B.team_id
left join users BC ON BB.team_headman_id=BC.id
left join inspection_data C ON C.inspection_task_id=B.id
left join power_inspection_data D on D.inspection_task_id=B.id
LEFT JOIN electrical_info E on D.power_number=E.id
LEFT JOIN electricity_user on electricity_user.id = E.electricity_user_id
LEFT JOIN inspection_in F on F.power_number=E.id and F.inspect_task_id=B.id
left join inspection_out G on G.power_number=E.id and G.inspect_task_id=B.id
WHERE B.status="completed" and left(B.work_date,7)="{month}" and electricity_user.number = "{sn}"
"""

# 缺陷记录sql，参数：sn、month
FARADAY_DEFECT_RECORD_SQL = """
SELECT
defect.created_time AS input_date,
defect.`name`,
defect.content AS `desc`,
defect.proposal AS advise,
defect.`level`,
defect.possible_result AS result,
defect.follow_up,
defect.`status`,
defect.remark,
defect.type AS position,
defect.customer_id,
defect.station_id,
electricity_user.number AS sn
FROM defect
INNER JOIN electricity_user ON defect.customer_id = electricity_user.customer_id
WHERE electricity_user.number="{sn}" and left(defect.created_time,7)="{month}"
"""

