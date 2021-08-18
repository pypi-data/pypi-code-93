# 巡检记录sql，参数：sn、month
OA_INSPECT_RECORD_SQL = """
SELECT
crm_customer.sn AS sn,
crm_source.sn AS source_sn,
crm_source.meter_sn,
crm_source.voltage_level,
crm_source.override,
crm_transformer.capacity, 
crm_transformer.real_capacity, 
crm_transformer.no AS transformer_no,
io_inspect.*,
io_inspect_in.*,
io_inspect_out.*
FROM io_inspect_out 
LEFT JOIN io_inspect_in on io_inspect_in.inspect_id = io_inspect_out.inspect_id AND io_inspect_in.source_id = io_inspect_out.source_id
LEFT JOIN io_inspect on io_inspect_out.inspect_id = io_inspect.id
LEFT JOIN io_customer on io_customer.id = io_inspect.customer_id
LEFT JOIN crm_customer on crm_customer.id = io_customer.customer_id
LEFT JOIN crm_source on crm_source.id = io_inspect_in.source_id
LEFT JOIN crm_transformer on crm_transformer.id = io_inspect_out.transformer_id
WHERE crm_customer.sn = "{sn}" and io_inspect.year_month= "{month}"
"""

# 监控信息sql，参数：sn
OA_MONITOR_INFO_SQL = """
SELECT
crm_customer.sn,
crm_customer.`name`,
crm_source.sn AS source_sn,
crm_source.meter_sn,
crm_source.price_type,
crm_source.voltage_level,
crm_source.power_factor,
crm_transformer.`no` AS transformer_sn,
crm_transformer.capacity,
crm_transformer.real_capacity,
im_device.sn AS device_sn,
im_device.`name` AS device_point,
im_device.`no` AS line,
im_device.online_time,
im_alert_value.sendto
FROM im_device
INNER JOIN im_customer on im_customer.id=im_device.im_customer_id 
INNER JOIN crm_customer on crm_customer.id=im_customer.customer_id 
LEFT JOIN crm_source on crm_source.id=im_device.source_id
LEFT JOIN crm_transformer on crm_transformer.source_id = im_device.source_id AND im_device.transformer_id = crm_transformer.id 
LEFT JOIN im_alert_value ON im_alert_value.device_id = im_device.id
WHERE crm_customer.sn = "{sn}" 
"""

# 监控告警sql，参数：sn、month
OA_MONITOR_ALERT_SQL = """
SELECT 
im_device.sn AS device_sn,
im_device.`name` AS device_point,
im_device.no as line,
im_alert_list.*
FROM im_alert_list
LEFT JOIN im_device on im_device.id = im_alert_list.device_id
INNER JOIN im_customer on im_customer.id=im_device.im_customer_id 
INNER JOIN crm_customer on crm_customer.id=im_customer.customer_id 
WHERE crm_customer.sn = "{sn}" and left(im_alert_list.start_time,7) = "{month}"
"""

# 工程数据sql，参数：sn、month
OA_MAINTENANCE_SQL = """
SELECT
crm_customer.sn,
crm_customer.`name`,
pm_project.application_time,
pm_project.content,
pm_project.type,
pm_project.`status`,
pm_project.dispatch_time,
pm_project.implement_start_time,
pm_project.implement_end_time,
pm_project.accept_time,
pm_implement.start_time,
pm_implement.end_time
FROM pm_project
LEFT JOIN pm_implement ON pm_implement.pm_project_id = pm_project.id
LEFT JOIN crm_customer ON pm_project.crm_customer_id = crm_customer.id
WHERE crm_customer.sn = '{sn}' and left(pm_implement.start_time,7) = '{month}'
"""

# 缺陷记录sql，参数：sn、month
OA_DEFECT_RECORD_SQL = """
SELECT io_defect.*
FROM io_defect
LEFT JOIN io_customer on io_customer.id = io_defect.io_customer_id
LEFT JOIN crm_customer on crm_customer.id = io_customer.customer_id
WHERE crm_customer.sn = "{sn}" and left(io_defect.input_date,7)="{sn}"
"""

# 客户基本信息sql，参数：sn
OA_USER_INFO_SQL = """
SELECT 
    crm_customer.sn, 
    crm_customer.name,
    crm_customer.province,
    crm_customer.address, 
    crm_customer.p_capacity,
    crm_customer.p_real_capacity,
    crm_customer.prize_type,
    crm_customer.p_vol_level,
    crm_contact.name AS contact_name,
    crm_contact.mobile,
    oa_user.nick AS inspector_name,
    sales_name.nick AS sales_name,
    oa_org.`name` AS oa_org
FROM io_customer 
LEFT JOIN crm_customer on io_customer.customer_id=crm_customer.id
LEFT JOIN crm_contact on crm_contact.id=io_customer.contact_id
LEFT JOIN oa_user on oa_user.id=io_customer.inspector_id
LEFT JOIN oa_user as sales_name on sales_name.id=crm_customer.sales_id 
LEFT JOIN oa_org on oa_org.id = crm_customer.org_id
WHERE crm_customer.sn = "{sn}"
"""

# 客户电气信息sql，参数：sn
OA_USER_ELECTRICITY_SQL = """
SELECT
    crm_customer.sn,
    crm_customer.`name`,
    crm_source.sn AS source_sn,
    crm_source.meter_sn,
    crm_source.price_type,
    crm_source.voltage_level,
    crm_source.power_factor,
    crm_transformer.`no` AS transformer_sn,
    crm_transformer.capacity,
    crm_transformer.real_capacity
FROM crm_customer
LEFT JOIN crm_source on crm_source.customer_id = crm_customer.id
LEFT JOIN crm_transformer on crm_source.id = crm_transformer.source_id 
WHERE crm_customer.sn = "{sn}" 
"""

