import multiprocessing,os,mediapipe
import Discord_framework

__ext_DCF__ = False
class using:
    def create_process(target,args):
        p = multiprocessing.Process(target=target,args=args)
        return p
    def start_process(Process):
        global _mp_tkt_process
        Process.start()
        _mp_tkt_process=Process
    def pull_values(V:str):
        t,hex=V.split('{"value":"',1)
        hex,t=hex.split('","clean":"',1)
        t,rgb=V.split('"value":"rgb',1)
        rgb,t=rgb.split('"},"hsl":{"',1)
        t,hsl=V.split('"value":"hsl',1)
        hsl,t=hsl.split('"},"hsv":{"fraction"',1)
        t,hsv=V.split(',"value":"hsv',1)
        hsv,t=hsv.split('","h":',1)
        return (hex,rgb,hsl,hsv,V)
    def del_files(dat: str,log:bool):
        for I in os.listdir(dat):
            E = (dat + "/" + I)
            if log == True:print(f'Deleting : {E}')
            if os.path.isfile(E):
                os.remove(E)
            elif os.path.isdir(E):
                using.del_files(E,log)

    def del_folders(dat: str,log:bool):
        for I in os.listdir(dat):
            E = (dat + "/" + I)
            if log == True:print(f'Deleting : {E}')
            if os.path.isdir(E):
                try:
                    os.rmdir(E)
                except OSError:
                    using.del_folders(E,log)
                    os.rmdir(E)
        os.rmdir(dat)
class Q:
    build_main = 'https://www.thecolorapi.com/'
    build_hex = 'id?hex='
    build_rgb = 'id?rgb=rgb'
    urlSafeChars=".","\\","(",")","{","[","|","]","}","^",">","<"
class ScannedText:
    def __init__(self,res1,res2,img_dat1,img_dat2):
        self.ext_text = res2
        self.raw_boxes = res1
        self.height = img_dat2
        self.width = img_dat1
        I = []
        for b in self.raw_boxes.splitlines():
            b = b.split(' ')
            i = int(b[1]),int(b[2]),int(b[3]),int(b[4]),str(b[0])
            I.append(i)
        self.boxes = I
class Hand:
    def __init__(self,n_hand:int,lm:list,handLms):
        self.hand_n             = n_hand
        self.sol                = mediapipe.solutions
        self.lm_list            = lm
        self.hand_lms           = handLms
        self.mpHands            = self.sol.hands
        self.WRIST              = self.lm_list[0]
        self.THUMB_CMC          = self.lm_list[1]
        self.THUMB_MCP          = self.lm_list[2]
        self.THUMB_IP           = self.lm_list[3]
        self.THUMB_TIP          = self.lm_list[4]
        self.INDEX_FINGER_MCP   = self.lm_list[5]
        self.INDEX_FINGER_PIP   = self.lm_list[6]
        self.INDEX_FINGER_DIP   = self.lm_list[7]
        self.INDEX_FINGER_TIP   = self.lm_list[8]
        self.MIDDLE_FINGER_MCP  = self.lm_list[9]
        self.MIDDLE_FINGER_PIP  = self.lm_list[10]
        self.MIDDLE_FINGER_DIP  = self.lm_list[11]
        self.MIDDLE_FINGER_TIP  = self.lm_list[12]
        self.RING_FINGER_MCP    = self.lm_list[13]
        self.RING_FINGER_PIP    = self.lm_list[14]
        self.RING_FINGER_DIP    = self.lm_list[15]
        self.RING_FINGER_TIP    = self.lm_list[16]
        self.PINKY_MCP          = self.lm_list[17]
        self.PINKY_PIP          = self.lm_list[18]
        self.PINKY_DIP          = self.lm_list[19]
        self.PINKY_TIP          = self.lm_list[20]
        self.THUMB              = [self.THUMB_CMC,self.THUMB_MCP,self.THUMB_IP,self.THUMB_TIP]
        self.INDEX              = [self.INDEX_FINGER_MCP,self.INDEX_FINGER_PIP,self.INDEX_FINGER_DIP,self.INDEX_FINGER_TIP]
        self.MIDDLE             = [self.MIDDLE_FINGER_MCP,self.MIDDLE_FINGER_PIP,self.MIDDLE_FINGER_DIP,self.MIDDLE_FINGER_TIP]
        self.RING               = [self.RING_FINGER_MCP,self.RING_FINGER_PIP,self.RING_FINGER_DIP,self.RING_FINGER_TIP]
        self.PINKY              = [self.PINKY_MCP,self.PINKY_PIP,self.PINKY_DIP,self.PINKY_TIP]
class Pose:
    def __init__(self,lm_list:list,res):
        self.lm_list          = lm_list
        self.results          = res
        self.nose             = lm_list[0]
        self.left_eye_inner   = lm_list[1]
        self.left_eye         = lm_list[2]
        self.left_eye_outer   = lm_list[3]
        self.right_eye_inner  = lm_list[4]
        self.right_eye        = lm_list[5]
        self.right_eye_outer  = lm_list[6]
        self.left_ear         = lm_list[7]
        self.right_ear        = lm_list[8]
        self.mouth_left       = lm_list[9]
        self.mouth_right      = lm_list[10]
        self.left_shoulder    = lm_list[11]
        self.right_shoulder   = lm_list[12]
        self.left_elbow       = lm_list[13]
        self.right_elbow      = lm_list[14]
        self.left_wrist       = lm_list[15]
        self.right_wrist      = lm_list[16]
        self.left_pinky       = lm_list[17]
        self.right_pinky      = lm_list[18]
        self.left_index       = lm_list[19]
        self.right_index      = lm_list[20]
        self.left_thumb       = lm_list[21]
        self.right_thumb      = lm_list[22]
        self.left_hip         = lm_list[23]
        self.right_hip        = lm_list[24]
        self.left_knee        = lm_list[25]
        self.right_knee       = lm_list[26]
        self.left_ankle       = lm_list[27]
        self.right_ankle      = lm_list[28]
        self.left_heel        = lm_list[29]
        self.right_heel       = lm_list[30]
        self.left_foot_index  = lm_list[31]
        self.right_foot_index = lm_list[32]
class FaceMesh:
    def __init__(self,lm_list:list,faceLms):
        # There is no landmark index on mediapipe.dev
        List = []
        for l in lm_list:
            List.append((l[0]))
        self.lms = List
        self.lms_ext = lm_list
        self.fLms = faceLms
class Face:
    def __init__(self,lm_list:list,res,score:int,bbox):
        # There is no landmark index on mediapipe.dev
        List = []
        for l in lm_list:
            List.append((l[0]))
        self.lms = List
        self.results = res
        self.conf_score = score
        self.bbox = bbox
        self.ext_lms = lm_list
class qr:
    def __init__(self,img,decoded):
        self.img = img
        self.raw_decoded = decoded[0]
        self.decoded_txt = self.raw_decoded.data.decode('utf-8')
        self.qrtype = self.raw_decoded.type
        self.r_rectangle = self.raw_decoded.rect
        self.polygon = self.raw_decoded.polygon
        self.rectangle = self.raw_decoded.rect.left,self.raw_decoded.rect.top,self.raw_decoded.rect.width,self.raw_decoded.rect.height
if __ext_DCF__ == True:
    class DCF:
        Send = Discord_framework.send
        Friends = Discord_framework.friends
        Info = Discord_framework.info
        Token = Discord_framework.token
        All = Discord_framework
else:
    class DCF:
        Send = None
        Friends = None
        Info = None
        Token = None
        All = None