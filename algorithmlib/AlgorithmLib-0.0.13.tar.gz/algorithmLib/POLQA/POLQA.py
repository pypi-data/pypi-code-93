from ctypes import *
import time
from algorithmLib.Function import project_root_path

# import VQTdll

# print(GetLastError())
VQTdll = cdll.LoadLibrary(project_root_path() + 'algorithmLib/POLQA/VQTDll.dll')



connect_flag = False
stop_flag = False
stop_flag1 = False
expectStr = 'Connected'
finalResul = {'mos':0.0,'Speech Level Gain':0.0,'Noise Level Gain':0.0}




class LogMsg(Structure):
    _fields_ = [("index", c_int),
                ("msg", c_char_p)
                ]

# callback output
def VQTLogfunc(msg):
    #print('VQTLogfunc start ')
    # c_s = string_at(msg)
    c_s = msg.decode()
    # cs = str(c_s,'utf-8')
    cs = str(c_s)
    #print('VQTLogfunc : ' + cs)
    global connect_flag
    global stop_flag1
    if 'Connected' in cs or 'Message sent' in cs:
        connect_flag = True
        stop_flag1 = True
    #print('VQTLogfunc end')


def VQTMSGfunc(msg):
    #print('VQTMSGfunc start')
    c_s = string_at(msg)
    cs = str(c_s, 'utf-8')
    print("VQTMSGfunc : " + cs)
    global stop_flag
    if 'Measurement Denied' in cs or 'Noise Level Gain' in cs:
        stop_flag = True
    #print('VQTMSGfunc end')
    if 'POLQA:' in cs:
        finalResul['mos'] = cs.split('POLQA:')[1].strip()
    if 'Speech Level Gain:' in cs:
        finalResul['Speech Level Gain'] = cs.split('Speech Level Gain:')[1].strip()
    if 'Noise Level Gain:' in cs:
        finalResul['Noise Level Gain'] = cs.split('Noise Level Gain:')[1].strip()


# callback hook
callback_type = CFUNCTYPE(None, c_char_p)
callback_login = callback_type(VQTLogfunc)
VQTdll.SetVQTLogMessage(callback_login)
# wd.SetVQTLogMessage(callback_login)

callback_type1 = CFUNCTYPE(None, c_wchar_p)
callback = callback_type1(VQTMSGfunc)
# VQTdll.SetVQTScores(callback)
# VQTdll.SetVQTSendInfoMessage(callback)
VQTdll.SetVQTRecvDBResponse(callback)
# VQTdll.SetVQTErrorAlert(callback)



def cal_polqa(refFile,degFile,samplerate):
    params = [1, 48000, 16, 99, 1, 48000, 16, 99, 1, 1, 0.2, 1, 0, 1, 0, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
              -1,
              -1, -1]  # for WB 16K sample rate
    params = [1, 48000, 16, 99, 1, 48000, 16, 99, 1, 1, 0.2, 1, 0, 1, 0, -1, -1, -1, -1, -1, -1, 0, 2, 0, 3, 0, 0, 0, 0,
              0]  # for WB 16K sample rate
    params[1], params[5] = samplerate, samplerate
    parameter_array = (c_float * len(params))(*params)
    vqtip = '192.168.2.22'
    VQTdll.ConnectPort(c_char_p(vqtip.encode('utf_8')), 6666)
    # VQTdll.ConnectPort(c_char_p("127.0.0.1"), 6666)
    #print('After VQT ConnectPort')
    while connect_flag == False:
        #print('inside while')
        time.sleep(5)
        pass
        # print('inside While ' + str(connect_flag))

    VQTdll.RunVQTPAMSPSQM(0, 0, c_char_p(refFile.encode('utf_8')), c_char_p(degFile.encode('utf_8')), 1, parameter_array)

    time.sleep(5)

    # StartVQTAuto (char *degraded_dir, char *ref_file, long del_deg, char *inventory_dir, char *user_id)


    # VQTdll.Disconnect()
    VQTdll.Disconnect()
    return finalResul

if __name__ == '__main__':

    ref = r"E:\AlgorithmLib\algorithmLib\POLQA\femalePOLQASWB.pcm"
    src = r'E:\files\cle_malePolqaWB.pcm'
    # deg = "C:\\VQT_Degraded\\nrtc\\female\\fem1POLQASWB_20190321133156_O_ManualTest_My Phone2_20190321133156_p.pcm"
    deg = r"E:\AlgorithmLib\algorithmLib\POLQA\femalePOLQASWB.pcm"
    cal_polqa(src,src,192000)
    print(finalResul)
