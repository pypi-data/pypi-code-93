import asyncio
import platform
import sys
import time


from bleak import discover, BleakClient
from AiDragonfly.aiqi_model.bluetooth import aiqi_bluetooth


devs_buff = []
connect_index = None
connect_dev_done_callback = None

aiqi_adapter = aiqi_bluetooth.Aiqi_Bluetooth_Class()

def Blue_Rev_CallBack(datalen, data):
    # print(data)
    if(len(data)==20 and data[1]== 0x62):
        addr = data[18]<<8 |data[19]
        # print('mesh '+ devs_buff[connect_index].devid+ ' addr:'+str(addr))
        devs_buff[connect_index].mesh_addr=addr


async def _Darwin_GetMessage_Process():
    global connect_index
    for i in range(0,len(devs_buff)):
        try:
            await aiqi_adapter.connect(devs_buff[i].devid,timeout=8)
            await asyncio.sleep(1)
            time.sleep(0.3)
            connect_index = i
            aiqi_adapter.set_receive_callback_register(Blue_Rev_CallBack)
            dev_con = bytearray([0, 0x61])
            await aiqi_adapter.senddata(dev_con)
            time.sleep(0.1)
            await aiqi_adapter.disconnect()
            time.sleep(0.3)
        except:
            i -= 1
            print('connect err')
            print('连接失败，未获取到设备信息，即将退出')
            sys.exit('程序退出')
    if connect_dev_done_callback is not None:
        connect_dev_done_callback(devs_buff)

def _mesh_mac_to_netaddr(dev_mac_addr):  # mesh设备 mac地址转换网络地址
    global onebot_local_save_list
    netadd = None

    tmp0 = int(dev_mac_addr[0], 16)
    tmp1 = int(dev_mac_addr[1], 16)
    tmp3 = int(dev_mac_addr[3], 16)
    tmp4 = int(dev_mac_addr[4], 16)
    tmp6 = int(dev_mac_addr[6], 16)
    tmp7 = int(dev_mac_addr[7], 16)
    one = tmp0 * 16 + tmp1
    two = tmp3 * 16 + tmp4
    three = tmp6 * 16 + tmp7
    netadd = (three % 20) * 1000 + two * 10 + one

    return netadd


def _windowns_getmeshmessage_process():
    global devs_buff
    for i in range(0,len(devs_buff)):
        devs_buff[i].mesh_addr = _mesh_mac_to_netaddr(devs_buff[i].devid)
    if connect_dev_done_callback is not None:
        connect_dev_done_callback(devs_buff)




async def Get_Onebot_Device_Message_Init(dev_buf,done_callback):
    global devs_buff,connect_dev_done_callback
    connect_dev_done_callback = done_callback
    devs_buff = []
    devs_buff = dev_buf[:]
    run_system = platform.system()
    # run_system = "Darwin"
    if run_system == "Darwin":
        await _Darwin_GetMessage_Process()
    elif run_system == "Windows":
        _windowns_getmeshmessage_process()
    else:
        sys.exit('系统不支持')

