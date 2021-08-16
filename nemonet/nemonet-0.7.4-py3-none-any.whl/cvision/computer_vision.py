import cv2
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error

import imutils
import imagehash
from PIL import Image

class ComputerVision:



    def diff(self, filenameA, filenameB):
        imageA = cv2.imread(filenameA)
        imageB = cv2.imread(filenameB)

        imageA_grey = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        imageB_grey = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        #It’s important to note that a value of 0 for MSE indicates perfect similarity
        _mse = mean_squared_error(imageA_grey, imageB_grey)
        # the SSIM value can vary between -1 and 1, where 1 indicates perfect similarity.
        _ssim = ssim(imageA_grey, imageB_grey)

        if ( _mse > 0 and _ssim < 1 ):

            (score, diff) = ssim(imageA_grey, imageB_grey, full=True)

            diff = (diff * 255).astype("uint8")

            thresh = cv2.threshold(diff, 0, 255,
                                   cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            # loop over the contours
            for c in cnts:
                # compute the bounding box of the contour and then draw the
                # bounding box on both input images to represent where the two
                # images differ
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # show the output images
            cv2.imwrite('compared_' + filenameA, imageA)
            cv2.imwrite('compared_' + filenameB, imageB)

            return False
        else:
            return True

    def diff_with_phash_image_hash(self, filenameA, filenameB):
        base_line_hash = imagehash.phash(Image.open(filenameA))
        compare_base_line_hash = imagehash.phash(Image.open(filenameB))
        return (base_line_hash == compare_base_line_hash)