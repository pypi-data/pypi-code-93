import sys

Onebot_Dev_Name_Items = ['Onebot', 'Mibot', 'Mi_Builder_C1B', 'Onebot_Edu_01B', "OneBot_XL_M",
                         "OneBot_St_M", "OneBot_LED", "OneBot_BL_M"]
Onebot_Dev_MeshName_Items = ["OneBot_XL_M", "OneBot_St_M", "OneBot_LED", "OneBot_BL_M"]
Onebot_Dev_BleName_Items = ['Onebot', 'Mibot', 'Mi_Builder_C1B', 'Onebot_Edu_01B']

class aiqi_device_type_class:
    Aiqi_Null_Dev = 0
    Aiqi_Onebot_Dev = 1
    Aiqi_Mibot_Dev = 2
    Aiqi_Mi_Builder_C1B_Dev = 3
    Aiqi_Onebot_Edu_01B_Dev = 4
    Aiqi_Onebot_Mesh_Dev = 5

class aiqi_bluetooth_dev_mes_class:
    index = 0
    name = ''
    devid = ''
    mesh_addr = None
    rssi = 0
    version = None

    def __init__(self, index=0, name=None, id=None, rssi=None):
        self.index = index
        self.name = name
        self.devid = id
        self.rssi = rssi

    def Set_Message(self, index,name, id, rssi, addr, version):
        self.index = index
        self.name = name
        self.devid = id
        self.rssi = rssi
        self.mesh_addr = addr
        self.version = version

    def print_title(self):
        print("index  name  deviceid  rssi")

    def __str__(self):
        restr= ('[ ' +'index:' + str(self.index) + ' name: ' + str(self.name) + ' devid: ' + str(self.devid) + ' addr: ' + str
        (self.mesh_addr) + ' rssi: ' + str(self.rssi) + ']')

        return restr


class aiqi_bluetooth_scan_class:
    scantimeout = 0
    scannamelist = []
    scanmaclist = []
    scanrssi = 0

    def __init__(self, scantimeout=3, scannamelist=[], scanmaclist=[],rssi =-100):
        self.scantimeout = scantimeout
        self.scannamelist = scannamelist
        self.scanmaclist = scanmaclist
        self.scanrssi = rssi


def select_onebot_devices(devices, rssi=-100, scan_name=[], scan_mac=[]):
    result_buff = []
    index = 0
    for dev in devices:
        if dev.name in Onebot_Dev_Name_Items and dev.rssi > rssi:

            dev_item = aiqi_bluetooth_dev_mes_class()
            dev_item.index = index
            dev_item.name = dev.name
            dev_item.devid = dev.address
            dev_item.rssi = dev.rssi
            index += 1
            if len(scan_name) == 0 and len(scan_mac) == 0:  # 不筛选
                result_buff.append(dev_item)
                # print('find ' + dev.name + " " + dev.address + ' ' + str(dev.rssi))
            elif len(scan_name) > 0 and len(scan_mac) == 0:  # 只筛选名字
                for name in scan_name:
                    if name == dev_item.name:
                        result_buff.append(dev_item)
                        # print('find ' + dev.name + " " + dev.address + ' ' + str(dev.rssi))
            elif len(scan_name) > 0 and len(scan_mac) > 0:  # 筛选名字和mac的设备
                for name in scan_name:
                    if name == dev_item.name:
                        for mac in scan_mac:
                            if mac == dev_item.devid:
                                result_buff.append(dev_item)
                                # print('find ' + dev.name + " " + dev.address + ' ' + str(dev.rssi))

    return result_buff


'''
mesh 设备判断
禁止ble 与 mesh 设备混合使用
'''


def IsMesh_Devices(buff):
    stats = False
    dev_len = len(buff)
    search = 0
    for item in buff:
        if item.name in Onebot_Dev_MeshName_Items:
            stats = True
            search +=1
        else:
            stats = False
    if stats == True and  search <dev_len:
        sys.exit('禁止普通设备与mesh 设备混合使用')
    return stats


'''

'''


def Read_Onebot_Device_type(devs):
    dev_type = aiqi_device_type_class.Aiqi_Null_Dev
    if len(devs) == 0:
        return []
    if IsMesh_Devices(devs) :
        dev_type = aiqi_device_type_class.Aiqi_Onebot_Mesh_Dev
    else:# 不是mesh device,取第一个判断类型
        _name = devs[0].name
        if _name == 'Onebot':
            dev_type=aiqi_device_type_class.Aiqi_Onebot_Dev
        elif _name == 'Mibot':
            dev_type = aiqi_device_type_class.Aiqi_Mibot_Dev
        elif _name == 'Mi_Builder_C1B':
            dev_type = aiqi_device_type_class.Aiqi_Mi_Builder_C1B_Dev
        elif _name == 'Onebot_Edu_01B':
            dev_type = aiqi_device_type_class.Aiqi_Onebot_Edu_01B_Dev
        else:
            pass
            sys.exit('不支持的设备名称，程序即将退出')

    return dev_type

def Print_Scan_Onebot_Device(devbuf):
    print('***********************local device list***********************')
    for item in devbuf:
        print(item)
    print('***************************************************************')




