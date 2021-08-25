import cv2
import os
import random
import ntpath

from PIL import Image
import piexif


ROW = 0
COL = 1


CROP_HEIGHT = 285
CROP_WIDTH  = 740

EXTEND = 200


IDEAL_BAR_ROW_OFFSET  = 90
IDEAL_BAR_COL_OFFSET  = 280

IDEAL_BAR_WIDTH = 40
IDEAL_BAR_HEIGHT = 105


FIRST_CROP_ROW =460
FIRST_CROP_COL =215

CROP_TOP    =[FIRST_CROP_ROW, FIRST_CROP_COL]
CROP_BOTTOM =[FIRST_CROP_ROW+CROP_HEIGHT+EXTEND, FIRST_CROP_COL+CROP_WIDTH]





SAMPLE_PIXELS = [[1,1], [100,100], [200,200]]


TOP    = [0, IDEAL_BAR_COL_OFFSET - 150]   # row, col
BOTTOM = [CROP_HEIGHT+EXTEND, IDEAL_BAR_COL_OFFSET + 240] # the range is from TOP  to [BOTTOM[ROW-1], BOTTOM[COL-1]]

TARGET = [20, 10]   # height, width
TARGET_HEIGHT = 20
TARGET_WIDTH  = 10


HEIGHT = 0
WIDTH  =1

def isLine(img, begin, end):
    for c in range(begin[COL], end[COL]):
        if img[begin[ROW], c] !=0:
            return False
    return True
def isBlock(img, top, bottom):
    for r in range(top[ROW], bottom[ROW]):
        if not isLine(img, [r, top[COL]], [r, bottom[COL]]):
            return False
    return True

def findTarget(img, top, bottom, target):
    finalRow = -1
    finalCol = -1
    
    print(top, bottom)

    for c in range(top[COL], bottom[COL] - target[WIDTH]):
        if finalCol != -1:
            break;
        for r in range(top[ROW], bottom[ROW] - target[HEIGHT]):
            if isBlock(img, [r, c], [r+target[HEIGHT], c+target[WIDTH]]):
                finalCol = c
                break;
    
    if finalCol == -1:
        return -1,-1

    print("got col offset ", finalCol)
    middleR =r-(IDEAL_BAR_HEIGHT-target[HEIGHT])
    print("middle r ", middleR)
    for r in range(middleR,  middleR+ (IDEAL_BAR_HEIGHT-target[HEIGHT]) +1):
        if finalRow != -1:
            break;
        for c in range(finalCol, finalCol+IDEAL_BAR_WIDTH-target[WIDTH]):
            if isBlock(img, [r, c], [r+target[HEIGHT], c+target[WIDTH]]):
                finalRow = r
                break;

    return finalRow, finalCol

# def findTarget(img, top, bottom, target):
#     finalRow = -1
#     finalCol = -1
#     
#     for c in range(top[COL], bottom[COL] - target[WIDTH]):
#         for r in range(top[ROW], bottom[ROW] - target[HEIGHT]):
#             if isBlock(img, [r, c], [r+target[HEIGHT], c+target[WIDTH]]):
#                 finalCol = c
#                 finalRow = r
#                 break;
#     
#     return finalRow, finalCol

def calibration(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 123, 255, cv2.THRESH_BINARY)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        letter = morph.copy()
        finalRow, finalCol = findTarget(letter, TOP, BOTTOM, TARGET)
    except Exception as e:
        print ("calibration exception: ",e)
        finalRow, finalCol =-1, -1
    
    if finalRow == -1 or finalCol == -1:
        print("calibration failed!")
        finalRow, finalCol =IDEAL_BAR_ROW_OFFSET+EXTEND, IDEAL_BAR_COL_OFFSET
    return finalRow, finalCol
    

def crop_rotate(img, imageFile):
    height, width = img.shape[:2]
    for i in range(10):
        row = random.randint(0, height-1)
        col = random.randint(0, width-1)
        sample =img[row,col]
        #print(row, col, sample)
        if sample[0] != sample[1] or sample[0] != sample[2] or sample[1] != sample[2]:
            break;            
    else:
        print("blank picture for", imageFile.split('/')[-1].split('_')[0], imageFile.split('/')[-1].split('_')[1])
#         blankImageFile=IMG_PATH+"blank_"+imageFile.split('/')[2]
#         cv2.imwrite(blankImageFile,img)
        return False
    
    newImg=cv2.rotate(img,cv2.ROTATE_90_COUNTERCLOCKWISE)
    cropImg=newImg[CROP_TOP[ROW]:CROP_BOTTOM[ROW], CROP_TOP[COL]:CROP_BOTTOM[COL]]
    
#     path, file = ntpath.split(imageFile)
#     originalImage = os.path.join(path, 'original_'+file)
#     cv2.imwrite(originalImage, cropImg) 
    #print(imageFile)
    offsetRow, offsetCol = calibration(cropImg)
    print("offset ", offsetRow, offsetCol)
    detectRow = CROP_TOP[ROW] + offsetRow
    detectCol = CROP_TOP[COL] + offsetCol
    
    newRow = detectRow - IDEAL_BAR_ROW_OFFSET
    newCol = detectCol - IDEAL_BAR_COL_OFFSET
    print("new ", newRow, newCol)
    finalImg=newImg[newRow:newRow+CROP_HEIGHT, newCol:newCol+CROP_WIDTH]
    cv2.imwrite(imageFile, finalImg)
    
    my_exif_ifd = {
                piexif.ExifIFD.CameraOwnerName: u"Spot II",
                }
    exif_dict = {"Exif":my_exif_ifd}
    exif_bytes = piexif.dump(exif_dict)
    im = Image.open(imageFile)
    im.save(imageFile, exif=exif_bytes)
    im.close()
    
    
#    print("Save image to ",imageFile)
    return True
#     gaussianBlurKernel = np.array(([[1, 2, 1], [2, 4, 2], [1, 2, 1]]), np.float32)/9
#     sharpenKernel = np.array(([[0, -1, 0], [-1, 9, -1], [0, -1, 0]]), np.float32)/9
#     meanBlurKernel = np.ones((3, 3), np.float32)/9

#def imageFilter(img):
def imageFilter():
    import cv2
    import numpy as np

    img = cv2.imread("test.jpg")
    img = cv2.resize(img, (0, 0), None, .25, .25)

    gaussianBlurKernel = np.array(([[1, 2, 1], [2, 4, 2], [1, 2, 1]]), np.float32)/9
    sharpenKernel = np.array(([[-1, -4, -2], [2, 18, 2], [-3, -3, -1]]), np.float32)/9
    meanBlurKernel = np.ones((3, 3), np.float32)/9

    gaussianBlur = cv2.filter2D(src=img, kernel=gaussianBlurKernel, ddepth=-1)
    meanBlur = cv2.filter2D(src=img, kernel=meanBlurKernel, ddepth=-1)
    sharpen = cv2.filter2D(src=img, kernel=sharpenKernel, ddepth=-1)

    horizontalStack = np.concatenate((img, gaussianBlur, meanBlur, sharpen), axis=1)

    cv2.imwrite("Output.jpg", horizontalStack)

    cv2.imshow("2D Convolution Example", horizontalStack)

    cv2.waitKey(0)
    #cv2.destroyAllWindow()
    
if __name__ == "__main__":
    imageFilter()

