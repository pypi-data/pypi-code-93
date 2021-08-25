import os

import json

from AiDragonfly.aiqi_bluetooth_device_type import aiqi_bluetooth_dev_mes_class

Save_Json_path = os.path.expanduser('~')
Save_Json_path = os.path.join(Save_Json_path, 'aiqi_python_temp')
save_json_name = 'aiqi_save_devices_message.json'


def _write_local_json(json_data):
    json_path = os.path.join(Save_Json_path, save_json_name)
    json_result = None
    if not os.path.exists(Save_Json_path):
        os.mkdir(Save_Json_path)
    file = open(json_path, 'w')
    file.write(json_data)
    file.close()


def _read_local_json(name):
    json_path = os.path.join(Save_Json_path, name)

    if not os.path.isfile(json_path):
        print('file not exist,create new file')
        file = open(json_path, 'w')
        file.write('')
        file.close()
        return None
    file = open(json_path)
    json_class = None
    try:
        json_class = json.load(file)
        # print(json_class)
    except:
        print('json load except')
        file = open(json_path, 'w')
        file.write('')
    file.close()
    return json_class


def delete_local_save_device():
    _write_local_json('')




def Save_Local_Onebot_Device(dev_buff):
    save_buf = []
    for item in dev_buff:
        user_item = {'index':item.index, 'name': item.name, 'devid': item.devid, 'mesh_addr': item.mesh_addr, 'rssi': item.rssi,
                     'version': item.version}
        save_buf.append(user_item)
    json_data = json.dumps(save_buf, indent=4, separators=(',', ': '))
    _write_local_json(json_data)


def Read_Local_Onebot_Device():
    result = []
    read_buf = _read_local_json(save_json_name)
    # print('Read_Local_Onebot_Device:'+json.dumps(read_buf))
    for item in read_buf:
        dev = aiqi_bluetooth_dev_mes_class()
        dev.Set_Message(item['index'],item['name'], item['devid'], item['rssi'], item['mesh_addr'], item['version'])
        result.append(dev)
    return result


def print_Local_Onebot_Device():
    print('***********************local device list***********************')
    dev_item = Read_Local_Onebot_Device()
    for item in dev_item:
        print(item)

    print('*****************************************************************')
