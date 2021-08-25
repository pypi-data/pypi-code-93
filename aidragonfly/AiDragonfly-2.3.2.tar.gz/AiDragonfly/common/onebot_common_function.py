import datetime


def onebot_xor_check(data):  # 异或校验函数 主要用于报文的校验
    value = 0x00
    for i in data:
        value = value ^ i
    return value

'''
十六进制字符串输出
'''
def Aiqi_Print_HEX(hexbuf,title=''):
    curr_time = datetime.datetime.now()
    time_str = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
    print(title+time_str+" "+" ".join([hex(c).replace('0x', '').rjust(2,'0') for c in hexbuf]))



def _int2hex(data, bitnum):  # 数据类型转换函数

    if data < 0:
        if bitnum == 8:
            bdata = bin(data & 0xff)
            cdata = bdata[2:10]
        elif bitnum == 16:
            bdata = bin(data & 0xFFFF)
            cdata = bdata[2:18]
        ldata = []
        for i in cdata:
            ldata.append(i)
        sdata = ''
        for i in ldata:
            sdata = sdata + str(i)
        fdata = int(sdata, 2)
        return fdata
    else:
        fdata = data
        return fdata


def _hex2int(hexnum, bitnum):
    if (bitnum == 8) and (0xFF >= hexnum >= 0x80):
        return ~(0xFF ^ hexnum)
    elif (bitnum == 16) and (0xFFFF >= hexnum >= 0x8000):
        return ~(0xFFFF ^ hexnum)
    elif (bitnum == 32) and (0xFFFFFFFF >= hexnum >= 0x80000000):
        return ~(0xFFFFFFFF ^ hexnum)
    else:
        return hexnum


