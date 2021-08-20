import cv2
import numpy as np
import random
import math

class RandomAffine:
    def __init__(self, probability=0.2, degrees=(-5, 5), translate=(0.05, 0.05), scale=(0.9, 1.1), shear=(-3, 3),
                 borderValue=(127.5, 127.5, 127.5)):
        """affine transformer
        :param degrees: rotation range (angle1, angle2)
        :param translate: (+/-height_ratio_range, +/-width_ratio_range)
        :param scale: scale range
        :param shear (+/-height_angle_range, +/-width_angle_range)
        :param borderValue"""
        self.probability = probability
        self.degrees = degrees
        self.translate = translate
        self.scale = scale
        self.shear = shear
        self.borderValue = borderValue

    def __call__(self, img, boxes=None):
        if np.random.uniform(0, 1) > self.probability:
            if boxes is None:
                return img
            else:
                return img, boxes

        height = max(img.shape[0], img.shape[1])

        # Rotation and Scale
        R = np.eye(3)
        a = random.random() * (self.degrees[1] - self.degrees[0]) + self.degrees[0]
        s = random.random() * (self.scale[1] - self.scale[0]) + self.scale[0]
        R[:2] = cv2.getRotationMatrix2D(angle=a, center=(img.shape[1] / 2, img.shape[0] / 2), scale=s)

        # Translation
        T = np.eye(3)
        T[0, 2] = np.random.uniform(-self.translate[0], self.translate[0]) * img.shape[0]  # x translation (pixels)
        T[1, 2] = np.random.uniform(-self.translate[1], self.translate[1]) * img.shape[1]  # y translation (pixels)

        # Shear
        S = np.eye(3)
        S[0, 1] = math.tan((random.random() * (self.shear[1] - self.shear[0]) + self.shear[0]) * math.pi / 180)  # x shear (deg)
        S[1, 0] = math.tan((random.random() * (self.shear[1] - self.shear[0]) + self.shear[0]) * math.pi / 180)  # y shear (deg)

        M = S @ T @ R  # Combined rotation matrix. ORDER IS IMPORTANT HERE!!
        imw = cv2.warpPerspective(img, M, dsize=(height, height), flags=cv2.INTER_LINEAR,
                                  borderValue=self.borderValue)  # BGR order borderValue

        # Return warped points also
        if boxes is not None:
            n = boxes.shape[0]
            points = boxes.copy()
            area0 = (points[:, 2] - points[:, 0]) * (points[:, 3] - points[:, 1])

            # warp points
            xy = np.ones((n * 4, 3))
            xy[:, :2] = points[:, [0, 1, 2, 3, 0, 3, 2, 1]].reshape(n * 4, 2)  # x1y1, x2y2, x1y2, x2y1
            xy = (xy @ M.T)[:, :2].reshape(n, 8)

            # create new boxes
            x = xy[:, [0, 2, 4, 6]]
            y = xy[:, [1, 3, 5, 7]]
            xy = np.concatenate((x.min(1), y.min(1), x.max(1), y.max(1))).reshape(4, n).T

            # apply angle-based reduction
            radians = a * math.pi / 180
            reduction = max(abs(math.sin(radians)), abs(math.cos(radians))) ** 0.5
            x = (xy[:, 2] + xy[:, 0]) / 2
            y = (xy[:, 3] + xy[:, 1]) / 2
            w = (xy[:, 2] - xy[:, 0]) * reduction
            h = (xy[:, 3] - xy[:, 1]) * reduction
            xy = np.concatenate((x - w / 2, y - h / 2, x + w / 2, y + h / 2)).reshape(4, n).T

            # reject warped points outside of image
            """reject by aspect ratio, area ratio, minimum of height/width """
            np.clip(xy, 0, height, out=xy)
            w = xy[:, 2] - xy[:, 0]
            h = xy[:, 3] - xy[:, 1]
            area = w * h
            ar = np.maximum(w / (h + 1e-16), h / (w + 1e-16))
            keep_index = (w > 4) & (h > 4) & (area / (area0 + 1e-16) > 0.1) & (ar < 10)

            boxes = xy[keep_index]
            return imw, boxes, keep_index
        else:
            return imw

if __name__ == "__main__":
    T = RandomAffine(degrees=(-5, 5), translate=(0.05, 0.05), scale=(0.9, 1.1), shear=(-3, 3))
    label = np.loadtxt("/home/liam/deepblue/datasets/VOC2007/train/label/000009.txt", dtype=np.str)
    bbox = label[:, 4: 8].astype(np.float)
    while True:
        img = cv2.imread("/home/liam/deepblue/datasets/VOC2007/train/image/000009.jpg")
        img2, bbox2, keep_index = T(img, bbox)
        print(len(label), len(bbox2))

        for box in bbox:
            cv2.rectangle(img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
        cv2.imshow("img", img)

        for box in bbox2:
            cv2.rectangle(img2, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
        cv2.imshow("img2", img2)
        cv2.waitKey(0)