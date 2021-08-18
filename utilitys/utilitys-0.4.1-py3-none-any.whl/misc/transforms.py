from __future__ import annotations

import pickle as pkl
from abc import ABC, ABCMeta
from functools import wraps
from pathlib import Path
from typing import Union, Any, List, Sequence

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
from skimage import io
from skimage import transform as trans
from skimage.feature import CENSURE, match_descriptors
from skimage.feature import corner_harris, corner_peaks
from skimage.measure import ransac
from skimage.transform import FundamentalMatrixTransform

from utilitys.widgets import EasyWidget

NChanImg = np.ndarray


# def registerImsInFolder(inFolder: Path):
#   for imgFname in
def needsGrayscale(func):
  @wraps(func)
  def inner(*args, **kwargs):
    img = args[-1]
    if img.ndim > 2:
      img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    args = args[:-1] + (img,)
    return func(*args, **kwargs)
  return inner

class ImgTransformer(ABC):
  refImg = None
  imgToWarp = None
  tformResult = None
  computedOnInputs = False

  def __init__(self, **kwTransformParams):
    pass

  def computeTform(self):
    raise NotImplementedError

  def resetTformProperties(self, refImg: Union[Path, NChanImg] = None, imgToWarp: Union[Path, NChanImg] = None,
                           **kwProps):
    if refImg is not None:
      if isinstance(refImg, Path):
        refImg = io.imread(refImg)
      self.refImg = refImg

    if imgToWarp is not None:
      if isinstance(imgToWarp, Path):
        imgToWarp = io.imread(imgToWarp)
      self.imgToWarp = imgToWarp

    self.computedOnInputs = False
    self.tformResult = None

  def applyTform(self, saveFname: Union[str, Path]=None, **kwargs):
    if saveFname is not None and self.tformResult is not None:
      saveImg = cv.cvtColor(self.tformResult, cv.COLOR_RGB2BGR)
      cv.imwrite(str(saveFname), saveImg)
    return self.tformResult

  def showTformOverlay(self, saveFname: Path = None):
    if not self.computedOnInputs:
      self.computeTform()
    if self.tformResult is None:
      self.applyTform()

    refIm = self.refImg
    warpedIm = self.tformResult

    if refIm.ndim > 2:
      refIm = cv.cvtColor(refIm, cv.COLOR_BGR2GRAY)
    if warpedIm.ndim > 2:
      warpedIm = cv.cvtColor(warpedIm, cv.COLOR_BGR2GRAY)

    outImg = np.zeros(refIm.shape + (3,), 'uint8')
    outImg[..., 0] = refIm
    outImg[..., 1] = warpedIm
    outImg[..., 2] = refIm

    if saveFname is not None:
      cv.imwrite(str(saveFname), outImg)
    else:
      plt.imshow(outImg)

  def doTformProc(self, *args, tformSaveFname=None, overlaySaveFname=None, **kwargs):
    self.resetTformProperties(*args, **kwargs)
    self.computeTform()
    self.applyTform(tformSaveFname, **kwargs)
    self.showTformOverlay(overlaySaveFname)

  @property
  def tformProps(self):
    raise NotImplementedError

class KeypointFinder:
  hasDescriptors = False

  def __init__(self):
    if not self.hasDescriptors:
      oldCompFeats = self.computeFeatures
      @wraps(self.computeFeatures)
      def newComputeFeatures(img):
        feats = oldCompFeats(img)
        return feats, feats
      self.computeFeatures = newComputeFeatures

  def computeFeatures(self, img: np.ndarray):
    """
    Computes a set of features for a given image. These are calculated for fixed and moving images to estimate a
    projection transform
    """
    raise NotImplementedError


class KeypointCorrelator(ImgTransformer, metaclass=ABCMeta):
  def __init__(self, keypointFinder: KeypointFinder, **kwTransformParams):
    super().__init__(**kwTransformParams)
    self.keypointFinder = keypointFinder
    self.foundKeypoints = False
    self.refPts = None
    self.toWarpPts = None
    self.refDescrs = None
    self.toWarpDescrs = None

  def _getKeypoints(self) -> (Any, Any):
    """Returns keypoints and descriptors for fixed and moving images"""
    outPts = []
    outDescrs = []
    for pts, descrs, img in zip([self.refPts, self.toWarpPts], [self.refDescrs, self.toWarpDescrs], [self.refImg, self.imgToWarp]):
      if pts is None or not self.foundKeypoints:
        pts, descrs = self.keypointFinder.computeFeatures(img)
      outPts.append(pts)
      outDescrs.append(descrs)
    self.refPts, self.toWarpPts = outPts
    self.refDescrs, self.toWarpDescrs = outDescrs
    lens = [len(pts) if pts is not None else 0 for pts in outPts]
    if 0 in lens:
      raise ValueError('Either ref keypoints or warp keypoints were not generated')
    return outPts, outDescrs

  def batchTformProc(self, imgsToWarp: Sequence[Path], outDir: Path, refImg: Union[Path, NChanImg]=None, overlayDir: Path=None,
                    **kwProps):
    self.resetTformProperties(refImg, **kwProps)
    self.refPts, self.refDescrs = self.keypointFinder.computeFeatures(self.refImg)
    outDir.mkdir(exist_ok=True)
    overlayDir.mkdir(exist_ok=True)
    # Save original image
    if isinstance(refImg, np.ndarray):
      name = outDir/'original.png'
    else:
      name = refImg
    cv.imwrite(str(name), cv.cvtColor(self.refImg, cv.COLOR_RGB2BGR))
    for img in imgsToWarp:
      self.resetTformProperties(imgToWarp=img)
      self.toWarpPts, self.toWarpDescrs = self.keypointFinder.computeFeatures(self.imgToWarp)
      self.foundKeypoints = True
      self.computeTform()
      if overlayDir is not None:
        self.showTformOverlay(overlayDir /f'{img.stem}_overlay{img.suffix}')
      self.applyTform(outDir/img.name)

class HomographyTransform(KeypointCorrelator):
  homography: np.ndarray
  numFeatures: int

  def computeTform(self):

    # Match features between the two images.
    # We create a Brute Force matcher with
    # Hamming distance as measurement mode.
    matcher = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)

    pts, descrs = self._getKeypoints()
    # Match the two sets of descriptors.
    matches = matcher.match(*descrs)

    # Sort matches on the basis of their Hamming distance.
    matches.sort(key=lambda x: x.distance)

    # Take the top 90 % matches forward.
    matches = matches[:int(len(matches) * 90)]
    matchIdxs = np.empty((len(matches), 2), dtype=int)
    for ii in range(len(matches)):
      match = matches[ii]
      matchIdxs[ii] = match.queryIdx, match.trainIdx

    for ii in range(2):
      pts[ii] = pts[ii][matchIdxs[:,ii],:]

    # Find the homography matrix
    self.homography, mask = cv.findHomography(*pts, cv.RANSAC)
    self.computedOnInputs = True

  def applyTform(self, saveFname: Union[str, Path]=None, useNearestNbr=False):
    # Use this matrix to transform the
    # colored image wrt the reference image.
    if useNearestNbr:
      mode = dict(flags=cv.INTER_NEAREST)
    else:
      mode = {}
    transformed_img = cv.warpPerspective(self.imgToWarp, self.homography, self.refImg.shape[:2][::-1],
                                         **mode)
    self.tformResult = transformed_img
    return super().applyTform(saveFname)

  @property
  def tformProps(self):
    return dict(homography=self.homography)


def _ptClickedAttach(scatPlt: pg.ScatterPlotItem):
  def ptClicked(pt: np.ndarray):
    scatPlt.addPoints(x=pt[[0]], y=pt[[1]], brush=pg.mkBrush(color='r'))
  return ptClicked

class GenericTransform(KeypointCorrelator):

  def __init__(self, keypointFinder: KeypointFinder, tformKind: str='euclidean', **kwTransformParams):
    super().__init__(keypointFinder, **kwTransformParams)
    qualifiedTformKind = tformKind.title() + 'Transform'
    self.tform = getattr(trans, qualifiedTformKind)()

  def computeTform(self):
    keyPts, descriptors = self._getKeypoints()
    matches = match_descriptors(*descriptors, cross_check=True)
    filterKeypts = lambda _matches: [keyPts[ii][_matches[:,ii]] for ii in range(2)]
    try:
      model, inliers = ransac(filterKeypts(matches),
                              FundamentalMatrixTransform, min_samples=len(matches),
                              residual_threshold=1, max_trials=5000)
      matches = matches[inliers]
    except ValueError:
      pass
    self.tform.estimate(*filterKeypts(matches))
    self.computedOnInputs = True

  def applyTform(self, saveFname: Union[str, Path] = None, **kwargs):
    floatImg = trans.warp(self.imgToWarp, self.tform, output_shape=self.refImg.shape[:2])
    self.tformResult = (floatImg*255).astype('uint8')
    return super().applyTform(saveFname, **kwargs)

  @property
  def tformProps(self):
    return dict(tform=self.tform)

class ManualKeypoints(KeypointFinder):
  imgItems : List[pg.ImageItem]
  refPts: np.ndarray = None
  toWarpPts: np.ndarray = None

  def __init__(self):
    super().__init__()
    self._displayWin = QtWidgets.QMainWindow()
    self.win = self._mkImgWin()

  def _mkImgWin(self):
    pg.mkQApp()
    children = []
    lbl = QtWidgets.QLabel('Select points (in order) on each image to register')
    lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    refPltItem = pg.PlotWidget()
    toWarpPltItem = pg.PlotWidget()
    children.append([refPltItem, toWarpPltItem])
    scats = []
    self.imgItems = []
    for pltItm, title in zip([refPltItem, toWarpPltItem], ['Reference', 'To Warp']):
      pltItm.getViewBox().setAspectLocked(True)
      pltItm.getViewBox().invertY(True)

      pltItm.setTitle(title)
      img = ClickableImage()
      scat = pg.ScatterPlotItem()
      scats.append(scat)
      img.sigClicked.connect(_ptClickedAttach(scat))
      self.imgItems.append(img)
      pltItm.addItem(img)
      pltItm.addItem(scat)
    doneBtn = QtWidgets.QPushButton('Done')
    children.append(doneBtn)
    def setPts():
      extractor = lambda _scat: np.c_[_scat.data['x'], _scat.data['y']]
      self.refPts = extractor(scats[0])
      self.toWarpPts = extractor(scats[1])
      scats[1].clear()
    doneBtn.clicked.connect(setPts)
    win = EasyWidget.buildMainWin(children)
    doneBtn.clicked.connect(lambda: QtCore.QTimer.singleShot(0, win.close))
    return win

  def computeFeatures(self, img: np.ndarray) -> np.ndarray:
    """Hacky implementation since manual transform wants to calculate both images at the same time"""
    if self.refPts is None or len(self.refPts) == 0:
      self.imgItems[0].setImage(img)
      ret = lambda: self.refPts
    else:
      self.imgItems[1].setImage(img)
      ret = lambda: self.toWarpPts
    self.win.show()
    pg.mkQApp().exec_()
    return ret()

class ClickableImage(pg.ImageItem):
  sigClicked = QtCore.Signal(object)

  def mouseClickEvent(self, ev: QtGui.QMouseEvent):
    pxCoords = self.mapFromParent(ev.pos())
    pxCoords = np.array([pxCoords.x(), pxCoords.y()])
    self.sigClicked.emit(pxCoords)

    super().mouseClickEvent(ev)

def hasNoDescriptors(func):
  @wraps(func)
  def inner(*args, **kwargs):
    ret = func(*args, **kwargs)
    return ret, ret
  return inner

class CensureKeypoints(KeypointFinder):

  def __init__(self):
    super().__init__()
    self.detector = CENSURE()

  @needsGrayscale
  def computeFeatures(self, img: np.ndarray) -> np.ndarray:
    self.detector.detect(img)
    return self.detector.keypoints

class CornerKeypoints(KeypointFinder):

  @needsGrayscale
  def computeFeatures(self, img: np.ndarray) -> np.ndarray:
    return corner_peaks(corner_harris(img), min_distance=5, threshold_rel=0.02)

class OrbKeypoints(KeypointFinder):
  hasDescriptors = True

  def __init__(self, numFeatures=5000):
    super().__init__()

    self.numFeatures = numFeatures
    self.orb_detector = cv.ORB_create(self.numFeatures)

  @needsGrayscale
  def computeFeatures(self, img: np.ndarray):
    keypoints, descrs  = self.orb_detector.detectAndCompute(img, None)
    outPts = np.empty((len(keypoints), 2))
    for ii in range(len(keypoints)):
      outPts[ii] = keypoints[ii].pt
    return outPts, descrs

