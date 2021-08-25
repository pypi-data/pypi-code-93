import time
import cv2
import random
from shutil import copyfile
import threading
import sys
import threading
import ntpath
import os

if __name__ == "__main__":
    import sys, os, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, parentdir)


from define import *
from test_handler.calibration import crop_rotate
from test_handler.qr_identify import qrIdentify

def camInstCreate(cameraIndex):
    try:
        device="/dev/video"+str(cameraIndex)
        print(device)
        camInst=cv2.VideoCapture(device)
        #time.sleep(1)
        camInst.set(cv2.CAP_PROP_FRAME_WIDTH,  MAX_CAMERA_RESOLUTION_WIDTH)
        camInst.set(cv2.CAP_PROP_FRAME_HEIGHT, MAX_CAMERA_RESOLUTION_HEIGHT)
        print (camInst)
        return camInst
    except Exception as camErr:
        print("Camera create exception:",camErr)
        return None;
    

camera_sem = threading.Semaphore()
def takePhoto(cameraIndex,qrCode,event):
    rtn = None
    print('in takePhoto')
    for i in range(5):
        camera_sem.acquire()    
        try:
            cam=camInstCreate(cameraIndex)
            s, img=cam.read()
            if s:
                print('got image')
#                cv2.imwrite(str(int(time.time())) + '_'+time.strftime('%Y%m%d%H%M%S')+'.jpg', img)
                if qrCode!=None:   ## got Qr code, regular picture for detection.
                    photo=qrCode+'_'+str(int(time.time())) + '_'+time.strftime('%Y%m%d%H%M%S')+'.jpg'
                    imageFile=IMG_PATH+photo
                    if crop_rotate(img,imageFile):
                        cam.release()
                        camera_sem.release()
                        rtn=photo
                        break;
                else: ## No Qr code, identify it from image.
                    print('qr image')
                    #cv2.imwrite(str(int(time.time())) + '_'+time.strftime('%Y%m%d%H%M%S')+'.jpg', img)
                    photo=qrIdentify(img);
                    cam.release()
                    camera_sem.release()
                    if photo == None:
                        rtn=NON_QR
                    else:
                        rtn=photo
                    break;
            else:
                print("Photo taking failed!",qrCode, time.strftime('%Y%m%d%H%M%S'))
        except cv2.error as cv2Error:
            print("takePhoto cv2 Error: ", cv2Error)
        except Exception as e:
            print("takePhoto Exception: ", e)
    
        if cam !=None:
            cam.release()
        camera_sem.release()            
        event.wait(2)
        if event.isSet():
            break;
    return rtn


def take_photo_test(cameraIndex,qrCode,event):
    from test_handler.calibration import imageFilter
    rtn = None
    print('in takePhoto')
    for i in range(5):
        camera_sem.acquire()    
        try:
            cam=camInstCreate(cameraIndex)
            #time.sleep(5)
            s, img=cam.read()
            if s:
                print('got image')
                original = str(int(time.time())) + '_'+time.strftime('%Y%m%d%H%M%S')
                new = original+'_new'
                cv2.imwrite(original+'.jpg', img)
#                 newImg=imageFilter(img)
#                 cv2.imwrite(new+'.jpg', newImg)
#                 if qrCode!=None:   ## got Qr code, regular picture for detection.
#                     photo=qrCode+'_'+str(int(time.time())) + '_'+time.strftime('%Y%m%d%H%M%S')+'.jpg'
#                     imageFile=IMG_PATH+photo
#                     if crop_rotate(img,imageFile):
#                         cam.release()
#                         camera_sem.release()
#                         rtn=photo
#                         break;
#                 else: ## No Qr code, identify it from image.
#                     print('qr image')
#                     #cv2.imwrite(str(int(time.time())) + '_'+time.strftime('%Y%m%d%H%M%S')+'.jpg', img)
#                     photo=qrIdentify(img);
#                     cam.release()
#                     camera_sem.release()
#                     if photo == None:
#                         rtn=NON_QR
#                     else:
#                         rtn=photo
#                     break;
            else:
                print("Photo taking failed!",qrCode, time.strftime('%Y%m%d%H%M%S'))
        except cv2.error as cv2Error:
            print("takePhoto cv2 Error: ", cv2Error)
        except Exception as e:
            print("takePhoto Exception: ", e)
    
        if cam !=None:
            cam.release()
        camera_sem.release()            
        event.wait(2)
        if event.isSet():
            break;
    return rtn

class TakePhotoProcedure(threading.Thread):
    def __init__(self, slotIndex, qrCode, camera, qCom, stopTakingPhoto):
        threading.Thread.__init__(self)
        self.slotIndex=slotIndex
        self.qrCode=qrCode
        self.camera = camera
        self.qCom = qCom
       
        self.timerParaIndex = 0
        self.taskStop=False
        self.event=stopTakingPhoto

    def run(self):
        while True:
            begin=time.time()
            self.procedure(self.timerParaIndex)
            end=time.time()
                        
            if self.timerParaIndex < len(PHOTO_TAKING_GAPS):
                delay=PHOTO_TAKING_GAPS[self.timerParaIndex] - (end-begin)
                self.timerParaIndex += 1
                if delay > 0:
                    self.event.wait(delay)                
            else:
                self.timerParaIndex = 0
                break;
            
            if self.event.isSet():
                #print(time.strftime('%Y%m%d%H%M%S'), "got stop command")
                break;
            
    def procedure(self,photoIndex):
        if self.qrCode != None:
            photoFile=takePhoto(self.camera, self.qrCode+'_'+str(self.slotIndex)+'_'+str(photoIndex), self.event)
        else:
            photoFile=takePhoto(self.camera, None, self.event) ## For Qr code
        if(photoFile !=None ):
            print(photoFile)
            self.qCom.put(photoFile)
        
        
   
def takePhoto_test():
    for i in range(1):
        cameraIndex = 2
    #    qrCode ='8888'
        qrCode =None
        stopTakingPhoto = threading.Event()
        stopTakingPhoto.set()
        print (take_photo_test(cameraIndex,qrCode,stopTakingPhoto) )
        time.sleep(5)
    
def takePhotoProcedure_test():
    None
    
    
if __name__ == "__main__":
    takePhoto_test()
          
