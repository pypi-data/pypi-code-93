import cv2
import glob
import numpy as np

'''
opencv 张正友的相机标定
https://blog.csdn.net/qq_42399848/article/details/89298212
'''
if __name__ == '__main__':
    # 设置寻找亚像素角点的参数，采用的停止准则是最大循环次数30和最大误差容限0.001
    criteria = (cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS, 30, 0.001)
    # criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.001)

    # 棋盘规格
    cbraw = 9
    cbcol = 7
    path_img = 'E:/image/Ex4/*.jpg'

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((cbraw * cbcol, 3), np.float32)
    '''
    设定世界坐标下点的坐标值，因为用的是棋盘可以直接按网格取；
    假定棋盘正好在x-y平面上，这样z=0，简化初始化步骤。
    mgrid把列向量[0:cbraw]复制了cbcol列，把行向量[0:cbcol]复制了cbraw行。
    转置reshape后，每行都是9*11网格中的某个点的坐标。
    '''
    objp[:, :2] = np.mgrid[0:cbraw, 0:cbcol].T.reshape(-1, 2)

    objpoints = []  # 存储3D点 3d point in real world space
    imgpoints = []  # 存储2D点2d points in image plane.
    # glob是个文件名管理工具
    images = glob.glob(path_img)
    for fname in images:
        # 对每张图片，识别出角点，记录世界物体坐标和图像坐标
        img = cv2.imread(fname)  # source image
        # 我用的图片太大，缩小了一半
        img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转灰度
        # cv2.imshow('img',gray)
        # cv2.waitKey(1000)
        # 寻找角点，存入corners，ret是找到角点的flag  第一个参数为图片，第二个为图片横纵角点的个数
        ret, corners = cv2.findChessboardCorners(gray, (cbraw, cbcol), None)
        # 执行亚像素级角点检测 格子大小 单位mm 测量得到
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        objpoints.append(objp)
        imgpoints.append(corners2)
        # 在棋盘上绘制角点,只是可视化工具
        img = cv2.drawChessboardCorners(gray, (cbraw, cbcol), corners2, ret)
        cv2.imshow('img', img)
        # cv2.waitKey(1000)

    cv2.destroyAllWindows()
    '''
    传入所有图片各自角点的三维、二维坐标，相机标定。
    每张图片都有自己的旋转和平移矩阵，但是相机内参和畸变系数只有一组。
    mtx，相机内参；dist，畸变系数；revcs，旋转矩阵；tvecs，平移矩阵。
    '''
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    print("-----------------------------------------------------")

    img = cv2.imread('E:/image/Ex4/1.jpg')
    # 注意这里跟循环开头读取图片一样，如果图片太大要同比例缩放，不然后面优化相机内参肯定是错的。
    img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    h, w = img.shape[:2]

    '''
    优化相机内参（camera matrix），这一步可选。
    参数1表示保留所有像素点，同时可能引入黑色像素， 显示更大范围的图片（正常重映射之后会删掉一部分图像）
    设为0表示尽可能裁剪不想要的像素，这是个scale，0-1都可以取。
    '''
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    # 纠正畸变 方法一
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # 纠正畸变 方法二  首先找到从扭曲图像到非扭曲图像的映射函数。然后使用重测函数
    # mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)
    # dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

    # 输出纠正畸变以后的图片
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    cv2.imwrite('Ex4result.png', dst)
    # 打印我们要求的两个矩阵参数
    print("newcameramtx:\n", newcameramtx)
    print("dist:\n", dist)

    # -------------------- 计算误差 ----------------------
    tot_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        tot_error += error

    print("total error mean: ", tot_error / len(objpoints))

    # 保存
    # np.savez()
    # np.savetxt()
